"""
Cloud-compatible game state persistence module for StrategyMasters
Uses in-memory storage with session-based persistence
"""

import logging
import uuid
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class CloudGamePersistence:
    """
    Handles game state persistence using in-memory storage
    that's compatible with cloud deployment environments
    """
    
    def __init__(self):
        """Initialize the persistence manager with empty storage"""
        # Main storage for game states
        self.games = {}
        
        # Storage for access codes
        self.admin_codes = {}
        self.team_codes = {}
        
        logger.info("Cloud-compatible game persistence initialized")
    
    def save_game(self, game_id, game_state, admin_code=None, team_codes=None):
        """
        Save a game state to in-memory storage
        
        Args:
            game_id (str): Unique identifier for the game
            game_state (dict): Game state data to save
            admin_code (str, optional): Admin access code
            team_codes (dict, optional): Team access codes
        
        Returns:
            bool: True if save was successful
        """
        try:
            # Save the game state
            self.games[game_id] = game_state
            
            # Save access codes if provided
            if admin_code:
                self.admin_codes[game_id] = admin_code
            
            if team_codes:
                self.team_codes[game_id] = team_codes
            
            logger.info(f"Game {game_id} saved successfully to cloud storage")
            return True
        except Exception as e:
            logger.error(f"Error saving game {game_id}: {e}", exc_info=True)
            return False
    
    def load_game(self, game_id):
        """
        Load a game state from in-memory storage
        
        Args:
            game_id (str): Unique identifier for the game
        
        Returns:
            dict: Game state data or None if not found
        """
        try:
            if game_id in self.games:
                logger.debug(f"Game {game_id} found in cloud storage")
                return self.games[game_id]
            else:
                logger.warning(f"Game {game_id} not found in cloud storage")
                return None
        except Exception as e:
            logger.error(f"Error loading game {game_id}: {e}", exc_info=True)
            return None
    
    def get_admin_code(self, game_id):
        """Get the admin code for a game"""
        admin_code = self.admin_codes.get(game_id)
        if admin_code:
            logger.debug(f"Admin code found for game {game_id}")
        else:
            logger.warning(f"Admin code not found for game {game_id}")
        return admin_code
    
    def get_team_code(self, game_id, team_id):
        """Get the team code for a specific team"""
        team_codes = self.team_codes.get(game_id, {})
        team_code = team_codes.get(team_id)
        if team_code:
            logger.debug(f"Team code found for team {team_id} in game {game_id}")
        else:
            logger.warning(f"Team code not found for team {team_id} in game {game_id}")
        return team_code
    
    def get_team_codes(self, game_id):
        """Get all team codes for a game"""
        return self.team_codes.get(game_id, {})
    
    def list_games(self):
        """
        List all available games
        
        Returns:
            list: List of game IDs
        """
        game_ids = list(self.games.keys())
        logger.info(f"Found {len(game_ids)} games in cloud storage")
        return game_ids
    
    def delete_game(self, game_id):
        """
        Delete a game from in-memory storage
        
        Args:
            game_id (str): Unique identifier for the game
        
        Returns:
            bool: True if deletion was successful
        """
        try:
            # Remove game state
            if game_id in self.games:
                del self.games[game_id]
            
            # Remove admin code
            if game_id in self.admin_codes:
                del self.admin_codes[game_id]
            
            # Remove team codes
            if game_id in self.team_codes:
                del self.team_codes[game_id]
            
            logger.info(f"Game {game_id} deleted successfully from cloud storage")
            return True
        except Exception as e:
            logger.error(f"Error deleting game {game_id}: {e}", exc_info=True)
            return False
