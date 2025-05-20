"""
Main application file for StrategyMasters: The Smartphone Industry Challenge
Flask web application for MBA strategy simulation game
"""

import os
import json
import logging
import secrets
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, abort

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import game models
from models.game_state import GameState
from models.redis_persistence import game_state_manager

app = Flask(__name__)

# Game state storage
active_games = {}

@app.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')

@app.route('/create_game', methods=['POST'])
def create_game():
    """Create a new game session"""
    try:
        logger.info("Creating new game")
        data = request.get_json()
        
        num_teams = int(data.get('num_teams', 5))
        num_rounds = int(data.get('num_rounds', 10))
        
        # Create and initialize game state
        game_state = GameState(num_teams=num_teams, num_rounds=num_rounds)
        game_state.initialize_game()
        
        # Save game state to persistent storage
        success = game_state_manager.save_game_state(game_state)
        
        if not success:
            logger.error("Failed to save game state")
            return jsonify({"error": "Error saving game state"}), 500
        
        # Return game information
        return jsonify({
            "game_id": game_state.game_id,
            "admin_code": game_state.admin_code,
            "team_codes": game_state.team_codes
        })
    except Exception as e:
        logger.error(f"Error creating game: {e}", exc_info=True)
        return jsonify({"error": "Error processing game state"}), 500

@app.route('/admin/<game_id>')
def admin_dashboard(game_id):
    """Render the admin dashboard for a game"""
    admin_code = request.args.get('admin_code')
    
    if not admin_code:
        return render_template('404.html', message="Admin code required"), 404
    
    # Verify admin credentials
    if not game_state_manager.verify_admin(game_id, admin_code):
        return render_template('404.html', message="Invalid admin credentials"), 404
    
    return render_template('admin.html', game_id=game_id, admin_code=admin_code)

@app.route('/api/admin/game_state/<game_id>')
def get_admin_game_state(game_id):
    """Get the game state for admin view"""
    try:
        admin_code = request.args.get('admin_code')
        
        if not admin_code:
            return jsonify({"error": "Admin code required"}), 400
        
        # Verify admin credentials
        if not game_state_manager.verify_admin(game_id, admin_code):
            return jsonify({"error": "Invalid admin credentials"}), 403
        
        # Load game state
        game_state = game_state_manager.load_game_state(game_id)
        
        if not game_state:
            return jsonify({"error": "Game not found"}), 404
        
        # Get admin view
        admin_view = game_state.get_admin_view()
        
        return jsonify(admin_view)
    except Exception as e:
        logger.error(f"Error getting admin game state: {e}", exc_info=True)
        return jsonify({"error": "Error processing game state"}), 500

@app.route('/api/admin/advance_round/<game_id>', methods=['POST'])
def advance_round(game_id):
    """Advance the game to the next round"""
    try:
        admin_code = request.args.get('admin_code')
        
        if not admin_code:
            return jsonify({"error": "Admin code required"}), 400
        
        # Verify admin credentials
        if not game_state_manager.verify_admin(game_id, admin_code):
            return jsonify({"error": "Invalid admin credentials"}), 403
        
        # Load game state
        game_state = game_state_manager.load_game_state(game_id)
        
        if not game_state:
            return jsonify({"error": "Game not found"}), 404
        
        # Advance to next round
        if game_state.current_round < game_state.num_rounds:
            game_state.current_round += 1
            game_state.start_new_round()
            
            # Save updated game state
            game_state_manager.save_game_state(game_state)
            
            return jsonify({"success": True, "round": game_state.current_round})
        else:
            return jsonify({"error": "Game already finished"}), 400
    except Exception as e:
        logger.error(f"Error advancing round: {e}", exc_info=True)
        return jsonify({"error": "Error processing game state"}), 500

@app.route('/team/<game_id>/<team_id>')
def team_dashboard(game_id, team_id):
    """Render the team dashboard for a game"""
    team_code = request.args.get('team_code')
    
    if not team_code:
        return render_template('404.html', message="Team code required"), 404
    
    # Load game state
    game_state = game_state_manager.load_game_state(game_id)
    
    if not game_state or team_id not in game_state.teams:
        logger.warning(f"Team not found: {team_id} in game {game_id}")
        return render_template('404.html', message="Team not found"), 404
    
    # Verify team code
    if game_state.team_codes.get(team_id) != team_code:
        logger.warning(f"Invalid team code for team {team_id}")
        return render_template('404.html', message="Invalid team code"), 404
    
    return render_template('team.html', game_id=game_id, team_id=team_id, team_code=team_code)

@app.route('/api/team/game_state/<game_id>/<team_id>')
def get_team_game_state(game_id, team_id):
    """Get the game state for team view"""
    try:
        team_code = request.args.get('team_code')
        
        if not team_code:
            return jsonify({"error": "Team code required"}), 400
        
        # Load game state
        game_state = game_state_manager.load_game_state(game_id)
        
        if not game_state:
            logger.warning(f"Game not found: {game_id}")
            return jsonify({"error": "Game not found"}), 404
        
        if team_id not in game_state.teams:
            logger.warning(f"Team not found: {team_id} in game {game_id}")
            return jsonify({"error": "Team not found"}), 404
        
        # Verify team code
        if game_state.team_codes.get(team_id) != team_code:
            logger.warning(f"Invalid team code for team {team_id}")
            return jsonify({"error": "Invalid team code"}), 403
        
        # Get team view
        team_view = game_state.get_team_view(team_id)
        
        return jsonify(team_view)
    except Exception as e:
        logger.error(f"Error getting team game state: {e}", exc_info=True)
        return jsonify({"error": "Error processing game state"}), 500

@app.route('/api/team/submit_decisions/<game_id>/<team_id>', methods=['POST'])
def submit_decisions(game_id, team_id):
    """Submit team decisions for the current round"""
    try:
        team_code = request.args.get('team_code')
        
        if not team_code:
            return jsonify({"error": "Team code required"}), 400
        
        # Load game state
        game_state = game_state_manager.load_game_state(game_id)
        
        if not game_state:
            return jsonify({"error": "Game not found"}), 404
        
        if team_id not in game_state.teams:
            return jsonify({"error": "Team not found"}), 404
        
        # Verify team code
        if game_state.team_codes.get(team_id) != team_code:
            return jsonify({"error": "Invalid team code"}), 403
        
        # Get decisions from request
        decisions = request.get_json()
        
        # Process decisions
        game_state.process_team_decisions(team_id, decisions)
        
        # Save updated game state
        game_state_manager.save_game_state(game_state)
        
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error submitting decisions: {e}", exc_info=True)
        return jsonify({"error": "Error processing decisions"}), 500

@app.route('/join_game', methods=['POST'])
def join_game():
    """Join an existing game as a team or facilitator"""
    try:
        data = request.get_json()
        
        game_id = data.get('game_id')
        role = data.get('role')
        code = data.get('code')
        
        if not game_id or not role or not code:
            return jsonify({"error": "Missing required parameters"}), 400
        
        # Load game state
        game_state = game_state_manager.load_game_state(game_id)
        
        if not game_state:
            logger.warning(f"Game not found: {game_id}")
            return jsonify({"error": "Game not found"}), 404
        
        if role == 'admin':
            # Verify admin code
            if game_state.admin_code != code:
                logger.warning(f"Invalid admin code for game {game_id}")
                return jsonify({"error": "Invalid admin code"}), 403
            
            return jsonify({
                "redirect": f"/admin/{game_id}?admin_code={code}"
            })
        elif role == 'team':
            # Find team ID by code
            team_id = None
            for tid, team_code in game_state.team_codes.items():
                if team_code == code:
                    team_id = tid
                    break
            
            if not team_id:
                logger.warning(f"Invalid team code for game {game_id}")
                return jsonify({"error": "Invalid team code"}), 403
            
            return jsonify({
                "redirect": f"/team/{game_id}/{team_id}?team_code={code}"
            })
        else:
            return jsonify({"error": "Invalid role"}), 400
    except Exception as e:
        logger.error(f"Error joining game: {e}", exc_info=True)
        return jsonify({"error": "Error processing request"}), 500

@app.route('/join')
def join_page():
    """Render the join game page"""
    return render_template('join.html')

@app.route('/results/<game_id>')
def results_page(game_id):
    """Render the results page for a game"""
    admin_code = request.args.get('admin_code')
    
    if not admin_code:
        return render_template('404.html', message="Admin code required"), 404
    
    # Verify admin credentials
    if not game_state_manager.verify_admin(game_id, admin_code):
        return render_template('404.html', message="Invalid admin credentials"), 404
    
    return render_template('results.html', game_id=game_id, admin_code=admin_code)

@app.route('/api/results/<game_id>')
def get_results(game_id):
    """Get the final results for a game"""
    try:
        admin_code = request.args.get('admin_code')
        
        if not admin_code:
            return jsonify({"error": "Admin code required"}), 400
        
        # Verify admin credentials
        if not game_state_manager.verify_admin(game_id, admin_code):
            return jsonify({"error": "Invalid admin credentials"}), 403
        
        # Load game state
        game_state = game_state_manager.load_game_state(game_id)
        
        if not game_state:
            return jsonify({"error": "Game not found"}), 404
        
        # Get rankings
        rankings = game_state.get_rankings()
        
        return jsonify({
            "rankings": rankings,
            "finished": game_state.finished,
            "rounds_completed": game_state.current_round - 1 if not game_state.finished else game_state.num_rounds
        })
    except Exception as e:
        logger.error(f"Error getting results: {e}", exc_info=True)
        return jsonify({"error": "Error processing game state"}), 500

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
