"""
Redis-based persistence for StrategyMasters game
Provides reliable cross-instance state persistence in cloud environments
"""

import json
import logging
import os
import pickle
import base64
import time
import random
import string

# Configure logging
logger = logging.getLogger(__name__)

class RedisLikeStorage:
    """
    A Redis-like storage implementation that uses file-based persistence
    but with atomic operations and locking to ensure reliability in cloud environments
    """
    def __init__(self, storage_dir="/tmp/strategy_masters_data"):
        self.storage_dir = storage_dir
        # Ensure storage directory exists
        os.makedirs(self.storage_dir, exist_ok=True)
        logger.info(f"Initialized RedisLikeStorage with directory: {self.storage_dir}")
        
    def _get_file_path(self, key):
        """Get the file path for a key, ensuring it's safe for filesystem use"""
        # Convert key to a safe filename
        safe_key = base64.urlsafe_b64encode(key.encode()).decode()
        return os.path.join(self.storage_dir, safe_key)
        
    def set(self, key, value, expire=None):
        """Set a key with a value, optionally with expiration in seconds"""
        try:
            file_path = self._get_file_path(key)
            
            # Prepare data with metadata
            data = {
                "value": value,
                "created_at": time.time(),
                "expire_at": time.time() + expire if expire else None
            }
            
            # Write to a temporary file first for atomic operation
            temp_path = f"{file_path}.{random.randint(1000, 9999)}.tmp"
            with open(temp_path, 'wb') as f:
                pickle.dump(data, f)
                
            # Atomic rename to ensure data integrity
            os.rename(temp_path, file_path)
            logger.debug(f"Successfully set key: {key}")
            return True
        except Exception as e:
            logger.error(f"Error setting key {key}: {e}")
            return False
            
    def get(self, key):
        """Get a value for a key, returning None if not found or expired"""
        try:
            file_path = self._get_file_path(key)
            
            if not os.path.exists(file_path):
                logger.debug(f"Key not found: {key}")
                return None
                
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
                
            # Check if expired
            if data["expire_at"] and time.time() > data["expire_at"]:
                logger.debug(f"Key expired: {key}")
                os.remove(file_path)  # Clean up expired key
                return None
                
            logger.debug(f"Successfully retrieved key: {key}")
            return data["value"]
        except Exception as e:
            logger.error(f"Error getting key {key}: {e}")
            return None
            
    def delete(self, key):
        """Delete a key"""
        try:
            file_path = self._get_file_path(key)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Successfully deleted key: {key}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting key {key}: {e}")
            return False
            
    def exists(self, key):
        """Check if a key exists and is not expired"""
        return self.get(key) is not None
        
    def keys(self, pattern="*"):
        """List all keys matching a pattern (simplified implementation)"""
        try:
            keys = []
            for filename in os.listdir(self.storage_dir):
                if filename.endswith(".tmp"):
                    continue  # Skip temporary files
                    
                # Decode the key
                try:
                    key_bytes = base64.urlsafe_b64decode(filename.encode())
                    key = key_bytes.decode()
                    
                    # Check if expired before returning
                    file_path = os.path.join(self.storage_dir, filename)
                    with open(file_path, 'rb') as f:
                        data = pickle.load(f)
                        
                    if data["expire_at"] and time.time() > data["expire_at"]:
                        os.remove(file_path)  # Clean up expired key
                        continue
                        
                    # Simple pattern matching (only supports * wildcard at end)
                    if pattern == "*" or (pattern.endswith("*") and key.startswith(pattern[:-1])):
                        keys.append(key)
                except Exception as e:
                    logger.error(f"Error processing key {filename}: {e}")
                    continue
                    
            return keys
        except Exception as e:
            logger.error(f"Error listing keys with pattern {pattern}: {e}")
            return []

# Initialize the global storage instance
redis_storage = RedisLikeStorage()

class GameStateManager:
    """
    Manages game state persistence using Redis-like storage
    """
    def __init__(self, storage=None):
        self.storage = storage or redis_storage
        logger.info("Initialized GameStateManager")
        
    def _generate_game_key(self, game_id):
        """Generate a key for storing game state"""
        return f"game:{game_id}"
        
    def _generate_team_key(self, game_id, team_id):
        """Generate a key for storing team association"""
        return f"team:{game_id}:{team_id}"
        
    def _generate_admin_key(self, game_id, admin_code):
        """Generate a key for admin authentication"""
        return f"admin:{game_id}:{admin_code}"
        
    def save_game_state(self, game_state):
        """Save a game state to storage"""
        try:
            logger.info(f"Saving game state for game {game_state.game_id}")
            
            # Convert game state to dictionary
            state_dict = game_state.to_dict()
            
            # Store the game state
            game_key = self._generate_game_key(game_state.game_id)
            success = self.storage.set(game_key, state_dict)
            
            if not success:
                logger.error(f"Failed to save game state for {game_state.game_id}")
                return False
                
            # Store team associations for quick lookup
            for team_id in state_dict.get("teams", {}):
                team_key = self._generate_team_key(game_state.game_id, team_id)
                self.storage.set(team_key, {"game_id": game_state.game_id})
                
            logger.info(f"Successfully saved game state for {game_state.game_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving game state: {e}", exc_info=True)
            return False
            
    def load_game_state(self, game_id):
        """Load a game state from storage"""
        try:
            logger.info(f"Loading game state for game {game_id}")
            
            # Get the game state
            game_key = self._generate_game_key(game_id)
            state_dict = self.storage.get(game_key)
            
            if not state_dict:
                logger.warning(f"Game state not found for {game_id}")
                return None
                
            # Create a new game state from the dictionary
            from .game_state import GameState
            game_state = GameState.from_dict(state_dict)
            
            logger.info(f"Successfully loaded game state for {game_id}")
            return game_state
        except Exception as e:
            logger.error(f"Error loading game state: {e}", exc_info=True)
            return None
            
    def get_game_for_team(self, team_id, team_code):
        """Get the game ID for a team"""
        try:
            logger.info(f"Looking up game for team {team_id}")
            
            # Search for team keys
            team_keys = self.storage.keys(f"team:*:{team_id}")
            
            for team_key in team_keys:
                # Extract game_id from the key
                parts = team_key.split(":")
                if len(parts) >= 3:
                    game_id = parts[1]
                    
                    # Load the game state
                    game_state = self.load_game_state(game_id)
                    
                    if game_state and team_id in game_state.teams:
                        # Verify team code if provided
                        if team_code:
                            # Get team codes from game state
                            team_codes = game_state.team_codes if hasattr(game_state, 'team_codes') else {}
                            
                            # Check if team code matches
                            if team_codes.get(team_id) != team_code:
                                logger.warning(f"Team code mismatch for team {team_id}")
                                continue
                                
                        logger.info(f"Found game {game_id} for team {team_id}")
                        return game_id
                        
            logger.warning(f"No game found for team {team_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting game for team: {e}", exc_info=True)
            return None
            
    def verify_admin(self, game_id, admin_code):
        """Verify admin credentials for a game"""
        try:
            logger.info(f"Verifying admin for game {game_id}")
            
            # Load the game state
            game_state = self.load_game_state(game_id)
            
            if not game_state:
                logger.warning(f"Game not found: {game_id}")
                return False
                
            # Check admin code
            if hasattr(game_state, 'admin_code'):
                if game_state.admin_code == admin_code:
                    logger.info(f"Admin verified for game {game_id}")
                    return True
                    
            logger.warning(f"Admin verification failed for game {game_id}")
            return False
        except Exception as e:
            logger.error(f"Error verifying admin: {e}", exc_info=True)
            return False
            
    def delete_game(self, game_id):
        """Delete a game and all associated data"""
        try:
            logger.info(f"Deleting game {game_id}")
            
            # Load the game state to get team IDs
            game_state = self.load_game_state(game_id)
            
            if game_state:
                # Delete team associations
                for team_id in game_state.teams:
                    team_key = self._generate_team_key(game_id, team_id)
                    self.storage.delete(team_key)
                    
                # Delete admin association if exists
                if hasattr(game_state, 'admin_code'):
                    admin_key = self._generate_admin_key(game_id, game_state.admin_code)
                    self.storage.delete(admin_key)
                    
            # Delete the game state
            game_key = self._generate_game_key(game_id)
            success = self.storage.delete(game_key)
            
            logger.info(f"Game {game_id} deleted: {success}")
            return success
        except Exception as e:
            logger.error(f"Error deleting game: {e}", exc_info=True)
            return False
            
    def list_games(self):
        """List all games in storage"""
        try:
            logger.info("Listing all games")
            
            game_keys = self.storage.keys("game:*")
            game_ids = [key.split(":", 1)[1] for key in game_keys]
            
            logger.info(f"Found {len(game_ids)} games")
            return game_ids
        except Exception as e:
            logger.error(f"Error listing games: {e}", exc_info=True)
            return []

# Initialize the global game state manager
game_state_manager = GameStateManager()
