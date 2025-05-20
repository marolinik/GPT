"""
Game state persistence module for StrategyMasters
Handles saving and loading game states from persistent storage
"""

import os
import json
import uuid
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class GamePersistence:
    """
    Handles persistent storage of game states
    """
    
    def __init__(self, storage_dir):
        """
        Initialize the persistence manager
        
        Args:
            storage_dir (str): Directory to store game data
        """
        self.storage_dir = storage_dir
        
        # Ensure storage directory exists and is writable
        try:
            os.makedirs(self.storage_dir, exist_ok=True)
            logger.info(f"Using storage directory: {self.storage_dir}")
            
            # Test write permissions by creating a test file
            test_file = os.path.join(self.storage_dir, '.test_write')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            logger.info(f"Storage directory is writable: {self.storage_dir}")
        except Exception as e:
            logger.error(f"Error initializing storage directory: {e}")
            raise RuntimeError(f"Storage directory is not usable: {e}")
        
        # Cache of loaded games
        self.game_cache = {}
        
        # Index of admin and team codes
        self.code_index = {
            'admin_codes': {},  # game_id -> admin_code
            'team_codes': {}    # game_id -> {team_id -> team_code}
        }
        
        # Load the code index if it exists
        self._load_code_index()
    
    def _get_game_path(self, game_id):
        """Get the file path for a game state"""
        return os.path.join(self.storage_dir, f"{game_id}.json")
    
    def _get_index_path(self):
        """Get the file path for the code index"""
        return os.path.join(self.storage_dir, "code_index.json")
    
    def _load_code_index(self):
        """Load the code index from file"""
        index_path = self._get_index_path()
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r') as f:
                    self.code_index = json.load(f)
                logger.info("Code index loaded successfully")
            except Exception as e:
                logger.error(f"Error loading code index: {e}")
                # Initialize a new index if loading fails
                self.code_index = {
                    'admin_codes': {},
                    'team_codes': {}
                }
        else:
            logger.info("No existing code index found, creating new one")
    
    def _save_code_index(self):
        """Save the code index to file"""
        index_path = self._get_index_path()
        try:
            with open(index_path, 'w') as f:
                json.dump(self.code_index, f)
            logger.debug("Code index saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving code index: {e}")
            return False
    
    def save_game(self, game_id, game_state, admin_code=None, team_codes=None):
        """
        Save a game state to persistent storage
        
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
            game_path = self._get_game_path(game_id)
            logger.debug(f"Saving game state to {game_path}")
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(game_path), exist_ok=True)
            
            with open(game_path, 'w') as f:
                json.dump(game_state, f)
            
            # Update the code index if codes are provided
            if admin_code:
                self.code_index['admin_codes'][game_id] = admin_code
            
            if team_codes:
                self.code_index['team_codes'][game_id] = team_codes
            
            # Save the updated index
            index_saved = self._save_code_index()
            if not index_saved:
                logger.warning(f"Failed to save code index for game {game_id}")
            
            # Update the cache
            self.game_cache[game_id] = game_state
            
            logger.info(f"Game {game_id} saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving game {game_id}: {e}", exc_info=True)
            return False
    
    def load_game(self, game_id):
        """
        Load a game state from persistent storage
        
        Args:
            game_id (str): Unique identifier for the game
        
        Returns:
            dict: Game state data or None if not found
        """
        # Check the cache first
        if game_id in self.game_cache:
            logger.debug(f"Game {game_id} found in cache")
            return self.game_cache[game_id]
        
        # Load from file if not in cache
        game_path = self._get_game_path(game_id)
        if os.path.exists(game_path):
            try:
                logger.debug(f"Loading game state from {game_path}")
                with open(game_path, 'r') as f:
                    game_state = json.load(f)
                
                # Update the cache
                self.game_cache[game_id] = game_state
                
                logger.info(f"Game {game_id} loaded successfully")
                return game_state
            except Exception as e:
                logger.error(f"Error loading game {game_id}: {e}", exc_info=True)
                return None
        else:
            logger.warning(f"Game file not found: {game_path}")
            return None
    
    def get_admin_code(self, game_id):
        """Get the admin code for a game"""
        admin_code = self.code_index['admin_codes'].get(game_id)
        if admin_code:
            logger.debug(f"Admin code found for game {game_id}")
        else:
            logger.warning(f"Admin code not found for game {game_id}")
        return admin_code
    
    def get_team_code(self, game_id, team_id):
        """Get the team code for a specific team"""
        team_codes = self.code_index['team_codes'].get(game_id, {})
        team_code = team_codes.get(team_id)
        if team_code:
            logger.debug(f"Team code found for team {team_id} in game {game_id}")
        else:
            logger.warning(f"Team code not found for team {team_id} in game {game_id}")
        return team_code
    
    def get_team_codes(self, game_id):
        """Get all team codes for a game"""
        return self.code_index['team_codes'].get(game_id, {})
    
    def list_games(self):
        """
        List all available games
        
        Returns:
            list: List of game IDs
        """
        games = []
        try:
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.json') and filename != "code_index.json":
                    games.append(filename.split('.')[0])
            logger.info(f"Found {len(games)} games")
            return games
        except Exception as e:
            logger.error(f"Error listing games: {e}", exc_info=True)
            return []
    
    def delete_game(self, game_id):
        """
        Delete a game from persistent storage
        
        Args:
            game_id (str): Unique identifier for the game
        
        Returns:
            bool: True if deletion was successful
        """
        try:
            # Remove from cache
            if game_id in self.game_cache:
                del self.game_cache[game_id]
            
            # Remove from code index
            if game_id in self.code_index['admin_codes']:
                del self.code_index['admin_codes'][game_id]
            
            if game_id in self.code_index['team_codes']:
                del self.code_index['team_codes'][game_id]
            
            # Save the updated index
            index_saved = self._save_code_index()
            if not index_saved:
                logger.warning(f"Failed to save code index after deleting game {game_id}")
            
            # Delete the game file
            game_path = self._get_game_path(game_id)
            if os.path.exists(game_path):
                os.remove(game_path)
                logger.info(f"Game {game_id} deleted successfully")
                return True
            else:
                logger.warning(f"Game file not found when deleting: {game_path}")
                return False
        except Exception as e:
            logger.error(f"Error deleting game {game_id}: {e}", exc_info=True)
            return False
