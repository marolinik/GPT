import unittest
import tempfile
from src.models.game_state import GameState
from src.models.persistence import GamePersistence

class PersistenceTestCase(unittest.TestCase):
    def test_save_and_load_game_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = GamePersistence(tmpdir)
            game_state = GameState(num_teams=2, num_rounds=3)
            game_state.initialize_game()
            game_id = game_state.game_id
            saved = persistence.save_game(
                game_id,
                game_state.to_dict(),
                admin_code=game_state.admin_code,
                team_codes=game_state.team_codes,
            )
            self.assertTrue(saved)
            loaded_state = persistence.load_game(game_id)
            self.assertIsNotNone(loaded_state)
            self.assertEqual(loaded_state["game_id"], game_id)
            self.assertEqual(loaded_state["num_teams"], 2)
            self.assertEqual(loaded_state["num_rounds"], 3)

if __name__ == "__main__":
    unittest.main()
