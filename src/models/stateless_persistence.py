"""
Game state persistence module for StrategyMasters
Uses a more robust approach for stateless environments
"""

import logging
import uuid
import json
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class StatelessGamePersistence:
    """
    Handles game state persistence using a more robust approach
    that works in stateless cloud environments
    """
    
    def __init__(self):
        """Initialize the persistence manager with empty storage"""
        # Main storage for game states - will be serialized/deserialized
        self.games = {}
        
        # Storage for access codes
        self.admin_codes = {}
        self.team_codes = {}
        
        logger.info("Stateless-compatible game persistence initialized")
    
    def save_game(self, game_id, game_state, admin_code=None, team_codes=None):
        """
        Save a game state to storage
        
        Args:
            game_id (str): Unique identifier for the game
            game_state (dict): Game state data to save
            admin_code (str, optional): Admin access code
            team_codes (dict, optional): Team access codes
        
        Returns:
            bool: True if save was successful
        """
        try:
            # Validate inputs to prevent null object errors
            if game_id is None:
                logger.error("Cannot save game with None game_id")
                return False
                
            if game_state is None:
                logger.error(f"Cannot save None game_state for game {game_id}")
                return False
            
            # Ensure game_state is a valid dictionary
            if not isinstance(game_state, dict):
                logger.error(f"Game state must be a dictionary, got {type(game_state)}")
                return False
            
            # Save the game state
            self.games[game_id] = game_state
            
            # Save access codes if provided
            if admin_code:
                self.admin_codes[game_id] = admin_code
            
            if team_codes:
                # Ensure team_codes is a dictionary
                if not isinstance(team_codes, dict):
                    logger.warning(f"Team codes must be a dictionary, got {type(team_codes)}")
                    # Create an empty dict if invalid
                    self.team_codes[game_id] = {}
                else:
                    self.team_codes[game_id] = team_codes
            
            logger.info(f"Game {game_id} saved successfully to stateless storage")
            return True
        except Exception as e:
            logger.error(f"Error saving game {game_id}: {e}", exc_info=True)
            return False
    
    def load_game(self, game_id):
        """
        Load a game state from storage
        
        Args:
            game_id (str): Unique identifier for the game
        
        Returns:
            dict: Game state data or None if not found
        """
        try:
            if game_id in self.games:
                logger.debug(f"Game {game_id} found in stateless storage")
                return self.games[game_id]
            else:
                logger.warning(f"Game {game_id} not found in stateless storage")
                return None
        except Exception as e:
            logger.error(f"Error loading game {game_id}: {e}", exc_info=True)
            return None
    
    def get_admin_code(self, game_id):
        """Get the admin code for a game"""
        try:
            admin_code = self.admin_codes.get(game_id)
            if admin_code:
                logger.debug(f"Admin code found for game {game_id}")
            else:
                logger.warning(f"Admin code not found for game {game_id}")
            return admin_code
        except Exception as e:
            logger.error(f"Error getting admin code for game {game_id}: {e}", exc_info=True)
            return None
    
    def get_team_code(self, game_id, team_id):
        """Get the team code for a specific team"""
        try:
            team_codes = self.team_codes.get(game_id, {})
            team_code = team_codes.get(team_id)
            if team_code:
                logger.debug(f"Team code found for team {team_id} in game {game_id}")
            else:
                logger.warning(f"Team code not found for team {team_id} in game {game_id}")
            return team_code
        except Exception as e:
            logger.error(f"Error getting team code for game {game_id}, team {team_id}: {e}", exc_info=True)
            return None
    
    def get_team_codes(self, game_id):
        """Get all team codes for a game"""
        try:
            return self.team_codes.get(game_id, {})
        except Exception as e:
            logger.error(f"Error getting team codes for game {game_id}: {e}", exc_info=True)
            return {}
    
    def list_games(self):
        """
        List all available games
        
        Returns:
            list: List of game IDs
        """
        try:
            game_ids = list(self.games.keys())
            logger.info(f"Found {len(game_ids)} games in stateless storage")
            return game_ids
        except Exception as e:
            logger.error(f"Error listing games: {e}", exc_info=True)
            return []
    
    def delete_game(self, game_id):
        """
        Delete a game from storage
        
        Args:
            game_id (str): Unique identifier for the game
        
        Returns:
            bool: True if deletion was successful
        """
        try:
            # Remove from storage
            if game_id in self.games:
                del self.games[game_id]
            
            # Remove admin code
            if game_id in self.admin_codes:
                del self.admin_codes[game_id]
            
            # Remove team codes
            if game_id in self.team_codes:
                del self.team_codes[game_id]
            
            logger.info(f"Game {game_id} deleted successfully from stateless storage")
            return True
        except Exception as e:
            logger.error(f"Error deleting game {game_id}: {e}", exc_info=True)
            return False
            
    def serialize(self):
        """
        Serialize the persistence state to a JSON string
        
        Returns:
            str: JSON string representation of the persistence state
        """
        try:
            state = {
                'games': self.games,
                'admin_codes': self.admin_codes,
                'team_codes': self.team_codes
            }
            return json.dumps(state)
        except Exception as e:
            logger.error(f"Error serializing persistence state: {e}", exc_info=True)
            return json.dumps({})
            
    def deserialize(self, state_json):
        """
        Deserialize a JSON string to restore the persistence state
        
        Args:
            state_json (str): JSON string representation of the persistence state
            
        Returns:
            bool: True if deserialization was successful
        """
        try:
            if not state_json:
                logger.warning("Empty state JSON provided for deserialization")
                return False
                
            state = json.loads(state_json)
            
            if 'games' in state:
                self.games = state['games']
            
            if 'admin_codes' in state:
                self.admin_codes = state['admin_codes']
                
            if 'team_codes' in state:
                self.team_codes = state['team_codes']
                
            logger.info("Persistence state deserialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error deserializing persistence state: {e}", exc_info=True)
            return False
