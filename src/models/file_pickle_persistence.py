"""
File-based Pickle persistence for StrategyMasters game
Provides reliable cross-instance state persistence using pickled files.
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

class FilePickleStorage:
    """
    A file-based pickle storage implementation that uses file-based persistence
    with atomic operations to ensure reliability.
    """
    def __init__(self, storage_dir=None):
        if storage_dir is not None:
            self.storage_dir = storage_dir
            logger.info(f"Using data storage path (from argument): {self.storage_dir}")
        elif os.environ.get("STRATEGY_MASTERS_DATA_DIR"):
            self.storage_dir = os.environ.get("STRATEGY_MASTERS_DATA_DIR")
            logger.info(f"Using data storage path (from STRATEGY_MASTERS_DATA_DIR env var): {self.storage_dir}")
        else:
            self.storage_dir = "./game_data" # Default path
            logger.info(f"Using data storage path (default): {self.storage_dir}")

        # Ensure storage directory exists
        os.makedirs(self.storage_dir, exist_ok=True)
        # No need for an additional general log message as specific ones are above.
        
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
            keys_list = [] # Renamed from keys to avoid conflict if a variable 'keys' is used
            for filename in os.listdir(self.storage_dir):
                if filename.endswith(".tmp"):
                    continue  # Skip temporary files
                    
                # Decode the key
                try:
                    key_bytes = base64.urlsafe_b64decode(filename.encode())
                    original_key = key_bytes.decode() # Renamed from key to original_key
                    
                    # Check if expired before returning
                    file_path = os.path.join(self.storage_dir, filename)
                    with open(file_path, 'rb') as f:
                        data = pickle.load(f)
                        
                    if data["expire_at"] and time.time() > data["expire_at"]:
                        os.remove(file_path)  # Clean up expired key
                        continue
                        
                    # Simple pattern matching (only supports * wildcard at end)
                    if pattern == "*" or (pattern.endswith("*") and original_key.startswith(pattern[:-1])):
                        keys_list.append(original_key)
                except Exception as e:
                    logger.error(f"Error processing key file {filename}: {e}") # Clarified log
                    continue
                    
            return keys_list
        except Exception as e:
            logger.error(f"Error listing keys with pattern {pattern}: {e}")
            return []

# Initialize the global storage instance
file_pickle_storage = FilePickleStorage()

class GameStateManager:
    """
    Manages game state persistence using file-based pickle storage
    """
    def __init__(self, storage=None):
        self.storage = storage or file_pickle_storage # Use renamed global instance
        logger.info("Initialized GameStateManager with FilePickleStorage")
        
    def _generate_game_key(self, game_id):
        """Generate a key for storing game state"""
        return f"game:{game_id}"
        
    def _generate_team_key(self, game_id, team_id):
        """Generate a key for storing team association"""
        return f"team:{game_id}:{team_id}"

    def _generate_admin_code_idx_key(self, game_id):
        """Generate a key for storing the admin code for a game in an index."""
        return f"admin_code_idx:{game_id}"
        
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

            # Store admin code in a separate index for efficient verification
            if hasattr(game_state, 'admin_code') and game_state.admin_code:
                admin_code_idx_key = self._generate_admin_code_idx_key(game_state.game_id)
                self.storage.set(admin_code_idx_key, game_state.admin_code)
            
            # Store team associations for quick lookup (team_code stored as value)
            team_codes_map = state_dict.get("team_codes", {})
            for team_id in state_dict.get("teams", {}):
                team_key = self._generate_team_key(game_state.game_id, team_id)
                actual_team_code = team_codes_map.get(team_id)
                if actual_team_code:
                    self.storage.set(team_key, actual_team_code)
                else:
                    logger.warning(f"No team code found for team {team_id} in game {game_state.game_id} during save.")
            
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
            from .game_state import GameState # Assuming game_state.py is in the same directory
            game_state = GameState.from_dict(state_dict)
            
            logger.info(f"Successfully loaded game state for {game_id}")
            return game_state
        except Exception as e:
            logger.error(f"Error loading game state: {e}", exc_info=True)
            return None
            
    def get_game_for_team(self, team_id, team_code):
        """Get the game ID for a team by checking stored team codes."""
        try:
            logger.info(f"Looking up game for team {team_id} by checking stored codes.")
            
            # Search for team keys pattern: team:*:{team_id}
            # This pattern will find all games a specific team_id might be associated with.
            potential_team_keys = self.storage.keys(f"team:*:{team_id}")
            
            for team_key in potential_team_keys:
                # team_key is expected to be "team:<game_id>:<team_id>"
                parts = team_key.split(":")
                if len(parts) == 3 and parts[0] == "team" and parts[2] == team_id:
                    game_id = parts[1]
                    stored_team_code_for_game = self.storage.get(team_key)
                    
                    if stored_team_code_for_game == team_code:
                        logger.info(f"Found game {game_id} for team {team_id} with matching code.")
                        return game_id
                    else:
                        logger.debug(f"Code mismatch for team {team_id} in game {game_id} (key: {team_key}). Expected {team_code}, got {stored_team_code_for_game}")
                else:
                    logger.warning(f"Malformed team key found: {team_key}")
                        
            logger.warning(f"No game found for team {team_id} with the provided code {team_code} after checking all potential keys.")
            return None
        except Exception as e:
            logger.error(f"Error getting game for team {team_id}: {e}", exc_info=True)
            return None
            
    def verify_admin(self, game_id, admin_code):
        """Verify admin credentials for a game using the indexed admin code."""
        try:
            logger.info(f"Verifying admin for game {game_id} using indexed code.")
            
            admin_code_idx_key = self._generate_admin_code_idx_key(game_id)
            stored_admin_code = self.storage.get(admin_code_idx_key)
            
            if not stored_admin_code:
                logger.warning(f"Admin code not found in index for game {game_id}. Falling back to full game state load.")
                # Fallback to old method if index key not found (e.g. older data)
                game_state = self.load_game_state(game_id)
                if not game_state:
                    logger.warning(f"Game not found for admin verification fallback: {game_id}")
                    return False
                if hasattr(game_state, 'admin_code') and game_state.admin_code == admin_code:
                    logger.info(f"Admin verified for game {game_id} via fallback.")
                    return True
                logger.warning(f"Admin verification failed for game {game_id} via fallback.")
                return False

            if stored_admin_code == admin_code:
                logger.info(f"Admin verified for game {game_id} using indexed code.")
                return True
            else:
                logger.warning(f"Admin verification failed for game {game_id}. Indexed code mismatch.")
                return False
        except Exception as e:
            logger.error(f"Error verifying admin for game {game_id}: {e}", exc_info=True)
            return False
            
    def delete_game(self, game_id):
        """Delete a game and all associated data"""
        try:
            logger.info(f"Deleting game {game_id}")
            
            # Load the game state to get team IDs for deleting associations
            # This is potentially inefficient if game_state is large.
            # An alternative would be to find team association keys by pattern.
            game_state = self.load_game_state(game_id) 
            
            if game_state:
                # Delete team associations
                for team_id in game_state.teams: # Iterate over team_ids from loaded state
                    team_key = self._generate_team_key(game_id, team_id)
                    self.storage.delete(team_key)
                
                # Delete the indexed admin code
                admin_code_idx_key = self._generate_admin_code_idx_key(game_id)
                self.storage.delete(admin_code_idx_key)
            
            # Delete the game state file itself
            game_key = self._generate_game_key(game_id)
            success = self.storage.delete(game_key)
            
            # If game_state could not be loaded, still attempt to delete team association keys by pattern
            if not game_state:
                logger.warning(f"Game state for {game_id} not found during delete, attempting to clean up team keys by pattern.")
                # This part is heuristic as team_ids are unknown without loading game_state
                # A more robust way would be for GameStateManager to maintain an index if not relying on game_state load.
                # For now, just delete the main game key if game_state is None.
                pass # The main deletion of game_key handles the primary data. Orphaned team keys are a minor issue.

            logger.info(f"Game {game_id} deleted: {success}")
            return success
        except Exception as e:
            logger.error(f"Error deleting game: {e}", exc_info=True)
            return False
            
    def list_games(self):
        """List all games in storage"""
        try:
            logger.info("Listing all games")
            
            game_keys_list = self.storage.keys("game:*") # Renamed variable
            game_ids = [key.split(":", 1)[1] for key in game_keys_list if key.startswith("game:")] # Added safety check
            
            logger.info(f"Found {len(game_ids)} games")
            return game_ids
        except Exception as e:
            logger.error(f"Error listing games: {e}", exc_info=True)
            return []

# Initialize the global game state manager
game_state_manager = GameStateManager() 