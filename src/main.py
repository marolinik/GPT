"""
Main application file for StrategyMasters: The Smartphone Industry Challenge
Flask web application for MBA strategy simulation game
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, abort

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import game models
from models.game_state import GameState
from models.file_pickle_persistence import game_state_manager

app = Flask(__name__)

# Game state storage (This seems unused as persistence is handled by game_state_manager)
# active_games = {}

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
            logger.warning(f"Admin code missing for game {game_id}")
            return jsonify({"error": "Admin code required"}), 400
        
        # Verify admin credentials
        if not game_state_manager.verify_admin(game_id, admin_code):
            logger.warning(f"Invalid admin credentials for game {game_id}")
            return jsonify({"error": "Invalid admin credentials"}), 403
        
        # Load game state
        game_state = game_state_manager.load_game_state(game_id)
        
        if not game_state:
            logger.warning(f"Game not found: {game_id}")
            return jsonify({"error": "Game not found"}), 404
        
        # Get admin view
        admin_view = game_state.get_admin_view()
        
        logger.info(f"Successfully returned admin view for game {game_id}")
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
            logger.warning(f"Missing admin code for game {game_id}")
            return jsonify({"error": "Admin code required", "success": False}), 400
        
        # Verify admin credentials
        if not game_state_manager.verify_admin(game_id, admin_code):
            logger.warning(f"Invalid admin credentials for game {game_id}")
            return jsonify({"error": "Invalid admin credentials", "success": False}), 403
        
        # Load game state
        game_state = game_state_manager.load_game_state(game_id)
        
        if not game_state:
            logger.warning(f"Game not found: {game_id}")
            return jsonify({"error": "Game not found", "success": False}), 404
            
        # Get force parameter (default to false)
        data = request.get_json() or {}
        force = data.get('force', False)
        
        logger.info(f"Advance round request - Game: {game_id}, Current round: {game_state.current_round}, Force: {force}")
        
        # Check if game is already finished
        if game_state.finished:
            logger.warning(f"Attempt to advance finished game: {game_id}")
            return jsonify({
                "error": "Game already finished", 
                "success": False,
                "is_finished": True
            }), 400
        
        # Check if we've reached the last round
        if game_state.current_round >= game_state.num_rounds:
            logger.warning(f"Game {game_id} already at final round {game_state.current_round}")
            game_state.finished = True
            game_state_manager.save_game_state(game_state)
            return jsonify({
                "error": "Game already at final round", 
                "success": False,
                "is_finished": True
            }), 400
        
        # Check if all teams have submitted or if force=true
        current_round_str = str(game_state.current_round)
        round_data = game_state.round_results.get(current_round_str, {})
        submissions = round_data.get("submissions", [])
        
        logger.info(f"Current submissions for round {game_state.current_round}: {submissions}")
        logger.info(f"Teams: {list(game_state.teams.keys())}")
        
        all_submitted = len(submissions) == len(game_state.teams)
        
        if not all_submitted and not force:
            logger.warning(f"Cannot advance round: not all teams submitted and force=false")
            return jsonify({
                "error": "Not all teams have submitted decisions", 
                "success": False,
                "submissions": submissions,
                "total_teams": len(game_state.teams),
                "submitted_count": len(submissions),
                "missing_teams": [team for team in game_state.teams if team not in submissions]
            }), 400
        
        logger.info(f"Advancing game {game_id} from round {game_state.current_round} to next round (force={force})")
        
        # If some teams haven't submitted, process empty decisions for them
        if not all_submitted and force:
            for team_id in game_state.teams:
                if team_id not in submissions:
                    logger.info(f"Processing empty decisions for team {team_id} due to force advance")
                    game_state.process_team_decisions(team_id, {})
        
        # Move to next round
        old_round = game_state.current_round
        new_round = old_round + 1
        game_state.current_round = new_round
        
        # Initialize the new round
        success = game_state.start_new_round()
        
        # Set game as finished if this was the last round
        if new_round >= game_state.num_rounds:
            game_state.finished = True
            logger.info(f"Game {game_id} marked as finished after reaching final round {new_round}")
        
        # Save updated game state
        if not game_state_manager.save_game_state(game_state):
            logger.error(f"Failed to save game state for game {game_id}")
            return jsonify({"error": "Failed to save game state", "success": False}), 500
        
        logger.info(f"Successfully advanced game {game_id} to round {new_round}")
        
        return jsonify({
            "success": True, 
            "round": new_round,
            "current_round": new_round,
            "message": f"Advanced to round {new_round}",
            "previous_round": old_round,
            "is_finished": game_state.finished
        })
    except Exception as e:
        logger.error(f"Error advancing round: {e}", exc_info=True)
        return jsonify({"error": f"Error processing game state: {str(e)}", "success": False}), 500

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
            logger.warning(f"Team code missing for team {team_id} in game {game_id}")
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
        
        if not team_view:
            logger.error(f"Failed to generate team view for team {team_id}")
            return jsonify({"error": "Error generating team view"}), 500
        
        logger.info(f"Successfully returned team view for team {team_id} in game {game_id}")
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
            logger.warning(f"Team code missing for team {team_id} in game {game_id}")
            return jsonify({"error": "Team code required", "success": False}), 400
        
        # Load game state
        game_state = game_state_manager.load_game_state(game_id)
        
        if not game_state:
            logger.warning(f"Game not found: {game_id}")
            return jsonify({"error": "Game not found", "success": False}), 404
        
        if team_id not in game_state.teams:
            logger.warning(f"Team not found: {team_id} in game {game_id}")
            return jsonify({"error": "Team not found", "success": False}), 404
        
        # Verify team code
        if game_state.team_codes.get(team_id) != team_code:
            logger.warning(f"Invalid team code for team {team_id}")
            return jsonify({"error": "Invalid team code", "success": False}), 403
            
        # Check if game is already finished
        if game_state.finished:
            logger.warning(f"Cannot submit decisions: game {game_id} is already finished")
            return jsonify({"error": "Game already finished", "success": False}), 400
            
        # Check if team has already submitted for current round
        current_round_str = str(game_state.current_round)
        round_data = game_state.round_results.get(current_round_str, {"submissions": []})
        submissions = round_data.get("submissions", [])
        
        if team_id in submissions:
            logger.warning(f"Team {team_id} already submitted decisions for round {game_state.current_round}")
            return jsonify({
                "error": "Team already submitted decisions for this round", 
                "success": False,
                "already_submitted": True
            }), 400
        
        # Get decisions from request
        decisions = request.get_json()
        if not decisions:
            logger.warning(f"Empty decisions payload from team {team_id}")
            return jsonify({"error": "No decisions provided", "success": False}), 400
            
        logger.info(f"Processing decisions for team {team_id} in game {game_id}, round {game_state.current_round}")
        logger.debug(f"Decision payload: {decisions}")
        
        # Process decisions
        game_state.process_team_decisions(team_id, decisions)
        
        # Save updated game state
        if not game_state_manager.save_game_state(game_state):
            logger.error(f"Failed to save game state for game {game_id}")
            return jsonify({"error": "Failed to save game state", "success": False}), 500
        
        # Check if all teams have submitted - this could auto-advance the round
        current_round_str = str(game_state.current_round)
        round_data = game_state.round_results.get(current_round_str, {"submissions": []})
        submissions = round_data.get("submissions", [])
        
        all_submitted = len(submissions) == len(game_state.teams)
        was_last_round = game_state.current_round >= game_state.num_rounds
        
        if all_submitted:
            logger.info(f"All teams submitted for round {current_round_str} in game {game_id}")
            
            # Auto-advance if all teams submitted and it's not the last round
            if not was_last_round:
                logger.info(f"Auto-advancing round for game {game_id}")
                # Game logic should handle round advancement in _finalize_round
        
        return jsonify({
            "success": True,
            "message": "Decisions submitted successfully",
            "round": game_state.current_round,
            "all_submitted": all_submitted
        })
    except Exception as e:
        logger.error(f"Error submitting decisions: {e}", exc_info=True)
        return jsonify({"error": f"Error processing decisions: {str(e)}", "success": False}), 500

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
