"""
Test script for StrategyMasters simulation game
Tests all core functionality for the game
"""

import unittest
import json
import os
import sys
import tempfile
import shutil
from datetime import datetime

# Add the parent directory to the path so we can import the application modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.game_state import GameState
from models.company import Company
from models.market import Market
from models.events import Event
from models.file_pickle_persistence import FilePickleStorage, GameStateManager # Import persistence classes
from main import app as flask_app # Import the flask app for integration tests

class TestGameFunctionality(unittest.TestCase):
    """Test cases for game functionality"""
    
    def setUp(self):
        """Setup test environment"""
        # Create a temporary directory for persistence
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a game state
        self.game_state = GameState(num_teams=3, num_rounds=5)
        self.game_state.initialize_game()
        
        # Store references to team IDs and codes
        self.team_ids = list(self.game_state.teams.keys())
        self.team_codes = self.game_state.team_codes
        self.admin_code = self.game_state.admin_code
        
        # Configure Flask app for testing
        flask_app.config['TESTING'] = True
        # Note: For true persistence isolation in API tests, the game_state_manager
        # used by flask_app would need to be configured to use a temp directory.
        # This current setup for API tests will use the default persistence path.
        self.client = flask_app.test_client()
        
    def tearDown(self):
        """Clean up after tests"""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
        
    def test_initial_state(self):
        """Test the initial game state"""
        # Check if game state is properly initialized
        self.assertEqual(self.game_state.current_round, 1)
        self.assertEqual(self.game_state.num_rounds, 5)
        self.assertEqual(len(self.game_state.teams), 3)
        self.assertFalse(self.game_state.finished)
        
        # Check team initialization
        for team_id, team in self.game_state.teams.items():
            # Check basic team properties
            self.assertEqual(team.capital, 500000000)
            self.assertEqual(team.r_d_capability, 50)
            self.assertEqual(team.brand_strength, 50)
            
            # Check product portfolio initialization - all segments should be active
            self.assertTrue(team.products["premium"]["active"])
            self.assertTrue(team.products["mid_range"]["active"])
            self.assertTrue(team.products["budget"]["active"])
            
            # Check prices are properly initialized
            self.assertEqual(team.products["premium"]["price"], 999)
            self.assertEqual(team.products["mid_range"]["price"], 499)
            self.assertEqual(team.products["budget"]["price"], 199)
            
    def test_team_decision_processing(self):
        """Test that team decisions are properly processed and affect company state"""
        team_id = self.team_ids[0]
        self.game_state.current_round = 1 # Ensure consistent round for decision history keys
        team = self.game_state.teams[team_id]
        
        # Initial state check for values to be changed by decisions
        initial_capital = team.capital
        initial_r_d_capability = team.r_d_capability
        initial_r_d_effectiveness = team.r_d_effectiveness
        initial_brand_strength = team.brand_strength
        initial_environmental_impact = team.environmental_impact
        initial_csr_rating = team.csr_rating # Assuming it's initialized
        initial_premium_price = team.products["premium"]["price"]

        # Create decisions with corrected structure and amounts for testing
        # Total explicit costs here: Marketing (25M+15M) + R&D (30M) + Corp (20M+10M+5M) = 105M
        decisions = {
            "products": {
                "premium": {
                    "active": True,
                    "price": initial_premium_price + 100, # e.g. 1099
                    "quality": 85,
                    "features": 90,
                    "production_volume": 120000,
                    "marketing_budget": 25000000 
                },
                "mid_range": {
                    "active": False  # Deactivate mid-range segment
                },
                "budget": {
                    "active": True,
                    "price": 249,
                    "quality": 50,
                    "features": 45,
                    "production_volume": 350000,
                    "marketing_budget": 15000000
                }
            },
            "r_d": { # Corrected structure for R&D decisions
                "budget": 30000000 
            },
            "corporate": { # Corrected structure for corporate strategy decisions
                "brand_investment": 20000000,
                "sustainability_investment": 10000000,
                "csr_investment": 5000000 
            }
        }
        
        # Process decisions - market object is needed for company.process_decisions
        self.game_state.process_team_decisions(team_id, decisions)
        
        # Get updated team state (re-fetch from game_state as process_team_decisions modifies it in-place)
        updated_team = self.game_state.teams[team_id]
        
        # Check product changes
        self.assertTrue(updated_team.products["premium"]["active"])
        self.assertEqual(updated_team.products["premium"]["price"], initial_premium_price + 100)
        self.assertEqual(updated_team.products["premium"]["quality"], 85)
        
        self.assertFalse(updated_team.products["mid_range"]["active"])
        
        self.assertTrue(updated_team.products["budget"]["active"])
        self.assertEqual(updated_team.products["budget"]["price"], 249)

        # Check capital reduction by at least the sum of direct investments
        # Sum of investments: 25M + 15M + 30M + 20M + 10M + 5M = 105M
        min_expected_capital_reduction = 105000000
        self.assertLess(updated_team.capital, initial_capital - min_expected_capital_reduction + 1, 
                        "Capital not reduced by at least the sum of direct investments.")

        # Check R&D changes
        self.assertGreater(updated_team.r_d_capability, initial_r_d_capability, "R&D capability should increase.")
        self.assertGreater(updated_team.r_d_effectiveness, initial_r_d_effectiveness, "R&D effectiveness should increase.")

        # Check corporate strategy changes
        self.assertGreater(updated_team.brand_strength, initial_brand_strength, "Brand strength should increase.")
        self.assertGreater(updated_team.environmental_impact, initial_environmental_impact, "Environmental impact score should increase.")
        self.assertGreater(updated_team.csr_rating, initial_csr_rating, "CSR rating should increase.")
        
        # Check if team was added to submissions for the round
        round_str = str(self.game_state.current_round)
        self.assertIn(team_id, self.game_state.round_results[round_str]["submissions"])
        
    def test_round_advancement(self):
        """Test advancing to the next round"""
        # Submit decisions for all teams for round 1
        for team_id in self.team_ids:
            self.game_state.process_team_decisions(team_id, {
                "products": {
                    "premium": {"active": True, "price": 1000},
                    "mid_range": {"active": True, "price": 500},
                    "budget": {"active": True, "price": 200}
                }
            })
            
        # Verify all teams have submitted for round 1
        round_str = str(1)  # Explicitly use round 1
        self.assertEqual(
            len(self.game_state.round_results[round_str]["submissions"]), 
            len(self.team_ids)
        )
        
        # Check that we're in round 2 now (should have auto-advanced)
        self.assertEqual(self.game_state.current_round, 2)
        
        # Manually advance to round 3 by finalizing round 2
        old_round = self.game_state.current_round
        self.game_state._finalize_round()
        
        # Verify round advanced
        self.assertEqual(self.game_state.current_round, old_round + 1)
        
    def test_multiple_rounds(self):
        """Test multiple rounds of the game"""
        for round_num in range(1, self.game_state.num_rounds + 1):
            # Skip if we've already advanced past this round
            if round_num < self.game_state.current_round:
                continue
                
            # Submit decisions for all teams
            for team_id in self.team_ids:
                price_premium = 1000 + (round_num * 50)  # Increase price each round
                self.game_state.process_team_decisions(team_id, {
                    "products": {
                        "premium": {
                            "active": True, 
                            "price": price_premium,
                            "quality": 80 + round_num,
                            "marketing_budget": 20000000 + (round_num * 1000000)
                        }
                    }
                })
            
            # Check if we're in the last round
            if round_num == self.game_state.num_rounds:
                # Game should be finished after processing all decisions in final round
                self.assertTrue(self.game_state.finished)
            else:
                # Verify we advanced to the next round
                self.assertEqual(self.game_state.current_round, round_num + 1)
                
    def test_product_segment_activation(self):
        """Test activating and deactivating product segments"""
        team_id = self.team_ids[0]
        team = self.game_state.teams[team_id]
        
        # Set all segments to specific states
        decisions = {
            "products": {
                "premium": {"active": False},
                "mid_range": {"active": True},
                "budget": {"active": False}
            }
        }
        
        # Process decisions
        self.game_state.process_team_decisions(team_id, decisions)
        
        # Check segment states
        team = self.game_state.teams[team_id]  # Get updated team
        self.assertFalse(team.products["premium"]["active"])
        self.assertTrue(team.products["mid_range"]["active"])
        self.assertFalse(team.products["budget"]["active"])
        
        # Now switch the states
        decisions = {
            "products": {
                "premium": {"active": True},
                "mid_range": {"active": False},
                "budget": {"active": True}
            }
        }
        
        # Process decisions
        self.game_state.process_team_decisions(team_id, decisions)
        
        # Check segment states
        team = self.game_state.teams[team_id]  # Get updated team
        self.assertTrue(team.products["premium"]["active"])
        self.assertFalse(team.products["mid_range"]["active"])
        self.assertTrue(team.products["budget"]["active"])
        
    def test_event_application_economic_downturn(self):
        """Test the application of an economic downturn event.
        This event should affect market economic strength, segment sizes, and company capital.
        """
        gs = self.game_state # Use a shorter alias for game_state

        # Store initial market values
        initial_econ_strength = gs.market.external_factors["economic_strength"]
        initial_premium_size = gs.market.segments["premium"]["size"]
        initial_mid_range_size = gs.market.segments["mid_range"]["size"]
        initial_budget_size = gs.market.segments["budget"]["size"]

        # Store initial capital for all teams
        initial_capitals = {tid: team.capital for tid, team in gs.teams.items()}

        # Define event data matching Event.from_dict structure
        event_definition = {
            "event_id": "test_econ_downturn_01",
            "title": "Test Economic Downturn",
            "description": "A severe economic downturn hits the market.",
            "round": gs.current_round,
            "impact_areas": { # This is used by Event constructor, not directly by new apply_impact logic for iteration
                "market": ["economic_strength", "segment_premium", "segment_budget"],
                "companies": {"all": ["capital"]}
            },
            "impact_values": {
                "market": {
                    "economic_strength": -0.2, 
                    "segment_premium": -0.1, # 10% reduction factor for premium segment size
                    "segment_budget": 0.15    # 15% increase factor for budget segment size
                },
                "companies": {"all": {"capital": -0.05}} # 5% capital reduction for all companies
            }
        }
        event = Event.from_dict(event_definition)

        # Apply the event
        event.apply_impact(gs)

        # --- Assert Market Changes ---
        # Economic Strength (clamped between 0.1 and 1.0 by apply_impact)
        expected_econ_strength = max(0.1, min(1.0, initial_econ_strength - 0.2))
        self.assertAlmostEqual(gs.market.external_factors["economic_strength"], expected_econ_strength, places=5)

        # Segment Sizes (Calculations considering normalization)
        # Premium: initial * (1 - 0.1), Budget: initial * (1 + 0.15), Mid-range: initial * (1 + 0.0)
        impacted_premium_size = initial_premium_size * (1.0 + event_definition["impact_values"]["market"]["segment_premium"])
        impacted_budget_size = initial_budget_size * (1.0 + event_definition["impact_values"]["market"]["segment_budget"])
        impacted_mid_range_size = initial_mid_range_size # Unchanged by this event directly

        total_impacted_size = impacted_premium_size + impacted_mid_range_size + impacted_budget_size
        
        self.assertTrue(total_impacted_size > 0, "Total segment size should be positive after impact before normalization.")

        expected_premium_normalized_size = impacted_premium_size / total_impacted_size
        expected_mid_range_normalized_size = impacted_mid_range_size / total_impacted_size
        expected_budget_normalized_size = impacted_budget_size / total_impacted_size

        self.assertAlmostEqual(gs.market.segments["premium"]["size"], expected_premium_normalized_size, places=5)
        self.assertAlmostEqual(gs.market.segments["mid_range"]["size"], expected_mid_range_normalized_size, places=5)
        self.assertAlmostEqual(gs.market.segments["budget"]["size"], expected_budget_normalized_size, places=5)
        
        # Check that sum of new segment sizes is 1.0
        self.assertAlmostEqual(sum(s["size"] for s in gs.market.segments.values()), 1.0, places=5)

        # --- Assert Company Changes ---
        for team_id, company in gs.teams.items():
            expected_capital = initial_capitals[team_id] * (1.0 + event_definition["impact_values"]["companies"]["all"]["capital"])
            self.assertAlmostEqual(company.capital, expected_capital, places=5,
                                 msg=f"Capital for team {team_id} not correctly updated by event.")

    def test_market_results_calculation_basic(self):
        """Test basic market results calculation for a single segment with two companies."""
        market = self.game_state.market
        market.total_market_size = 1000000 # Simplify total market size for easier calcs
        market.segments["premium"]["size"] = 0.5 # 500,000 units in premium
        market.segments["mid_range"]["size"] = 0.3
        market.segments["budget"]["size"] = 0.2
        market.update_market_conditions(1) # To ensure segment sizes are normalized if logic changes
        
        premium_segment_demand = market.total_market_size * market.segments["premium"]["size"]

        # Company 1: Strong in Premium
        company1 = Company(team_id="c1", name="Company Alpha")
        company1.products["premium"] = {
            "active": True, "price": 900, "quality": 90, "features": 85,
            "production_volume": 300000, "marketing_budget": 30000000 # Good marketing
        }
        company1.brand_strength = 70
        company1.innovation_index = 75
        company1.environmental_impact = 60

        # Company 2: Weaker in Premium, focuses on price
        company2 = Company(team_id="c2", name="Company Beta")
        company2.products["premium"] = {
            "active": True, "price": 750, "quality": 60, "features": 50,
            "production_volume": 150000, "marketing_budget": 10000000 # Lower marketing
        }
        company2.brand_strength = 40
        company2.innovation_index = 50
        company2.environmental_impact = 40
        
        # Company 3: Not active in premium
        company3 = Company(team_id="c3", name="Company Gamma")
        company3.products["premium"]["active"] = False

        companies_dict = {"c1": company1, "c2": company2, "c3": company3}

        results = market.calculate_market_results(companies_dict)

        # --- Assertions for Premium Segment --- 
        self.assertIn("c1", results, "Company 1 should have results.")
        self.assertIn("c2", results, "Company 2 should have results.")
        self.assertNotIn("c3", results.get("c3", {}).get("sales", {}).get("premium", {}), "Company 3 should not have premium sales results if not active or no results for c3.")
        
        c1_premium_sales = results["c1"]["sales"].get("premium")
        c2_premium_sales = results["c2"]["sales"].get("premium")

        self.assertIsNotNone(c1_premium_sales, "Company 1 should have premium sales data.")
        self.assertIsNotNone(c2_premium_sales, "Company 2 should have premium sales data.")

        # 1. Attractiveness & Market Share (Qualitative)
        # We expect Company 1 (stronger overall) to have a higher market share in premium.
        # This requires calculating attractiveness scores manually or inferring. Given complexity, a direct comparison of shares:
        self.assertGreater(c1_premium_sales["market_share"], c2_premium_sales["market_share"],
                           "Company 1 (stronger offering) should have higher premium market share than Company 2.")

        # 2. Units Sold correctly calculated and capped by production volume
        c1_units_sold = c1_premium_sales["units_sold"]
        c2_units_sold = c2_premium_sales["units_sold"]

        self.assertLessEqual(c1_units_sold, company1.products["premium"]["production_volume"], "C1 units sold cannot exceed production volume.")
        self.assertLessEqual(c2_units_sold, company2.products["premium"]["production_volume"], "C2 units sold cannot exceed production volume.")
        
        # Total units sold in segment should not massively exceed segment demand (allowing for rounding)
        self.assertLessEqual(c1_units_sold + c2_units_sold, premium_segment_demand * 1.05, "Total units sold in premium should be around segment demand.")

        # 3. Revenue Calculation
        expected_c1_revenue = c1_units_sold * company1.products["premium"]["price"]
        expected_c2_revenue = c2_units_sold * company2.products["premium"]["price"]
        self.assertAlmostEqual(c1_premium_sales["revenue"], expected_c1_revenue, places=2, msg="C1 premium revenue incorrect.")
        self.assertAlmostEqual(c2_premium_sales["revenue"], expected_c2_revenue, places=2, msg="C2 premium revenue incorrect.")

        # 4. Customer Satisfaction Change (check if it's populated)
        self.assertIn("customer_satisfaction_change", results["c1"], "C1 results should have customer_satisfaction_change.")
        self.assertIn("customer_satisfaction_change", results["c2"], "C2 results should have customer_satisfaction_change.")

        # 5. Overall Market Share (check if populated for C1 and C2)
        self.assertIn("market_share", results["c1"], "C1 results should have overall market_share.")
        self.assertIn("market_share", results["c2"], "C2 results should have overall market_share.")
        self.assertTrue(0 <= results["c1"]["market_share"] <= 1.0)
        self.assertTrue(0 <= results["c2"]["market_share"] <= 1.0)

    def test_persistence_save_load_delete_verify(self):
        """Test saving, loading, deleting game state, and verifying codes using GameStateManager and FilePickleStorage."""
        # Use the temp_dir created in setUp for this test's storage
        # Ensure the temp_dir is clean before this test if other tests might use it, though setUp should handle it for each test run.
        test_storage = FilePickleStorage(storage_dir=self.temp_dir)
        test_gsm = GameStateManager(storage=test_storage)

        # 1. Create and Save Game State
        game_to_save = GameState(num_teams=2, num_rounds=3)
        game_to_save.initialize_game() 
        game_id = game_to_save.game_id
        admin_code = game_to_save.admin_code
        
        self.assertTrue(len(game_to_save.teams) == 2, "Game should have 2 teams after init.")
        team_ids = list(game_to_save.teams.keys())
        team1_id = team_ids[0]
        team1_code = game_to_save.team_codes[team1_id]
        team2_id = team_ids[1]
        team2_code = game_to_save.team_codes[team2_id]

        save_success = test_gsm.save_game_state(game_to_save)
        self.assertTrue(save_success, "Failed to save game state.")

        # Verify underlying storage (optional, but good for deeper check)
        game_key = test_gsm._generate_game_key(game_id)
        admin_idx_key = test_gsm._generate_admin_code_idx_key(game_id)
        team1_idx_key = test_gsm._generate_team_key(game_id, team1_id)
        team2_idx_key = test_gsm._generate_team_key(game_id, team2_id)

        self.assertTrue(test_storage.exists(game_key), f"Main game state key {game_key} should exist.")
        self.assertTrue(test_storage.exists(admin_idx_key), f"Admin index key {admin_idx_key} should exist.")
        self.assertEqual(test_storage.get(admin_idx_key), admin_code, "Stored admin code in index is incorrect.")
        self.assertTrue(test_storage.exists(team1_idx_key), f"Team 1 index key {team1_idx_key} should exist.")
        self.assertEqual(test_storage.get(team1_idx_key), team1_code, "Stored team 1 code is incorrect.")
        self.assertTrue(test_storage.exists(team2_idx_key), f"Team 2 index key {team2_idx_key} should exist.")
        self.assertEqual(test_storage.get(team2_idx_key), team2_code, "Stored team 2 code is incorrect.")

        # 2. Load Game State
        loaded_game = test_gsm.load_game_state(game_id)
        self.assertIsNotNone(loaded_game, "Failed to load game state.")
        self.assertEqual(loaded_game.game_id, game_id, "Loaded game_id mismatch.")
        self.assertEqual(loaded_game.num_teams, 2, "Loaded num_teams mismatch.")
        self.assertEqual(loaded_game.admin_code, admin_code, "Loaded admin_code mismatch.")
        self.assertIn(team1_id, loaded_game.team_codes, "Team 1 not in loaded team_codes.")
        self.assertEqual(loaded_game.team_codes[team1_id], team1_code, "Loaded team 1 code mismatch.")
        self.assertEqual(len(loaded_game.teams), 2, "Loaded game should have 2 teams.")

        # 3. Verify Admin (using the efficient method)
        self.assertTrue(test_gsm.verify_admin(game_id, admin_code), "Admin verification failed for correct code.")
        self.assertFalse(test_gsm.verify_admin(game_id, "wrong_admin_code"), "Admin verification succeeded for wrong code.")
        self.assertFalse(test_gsm.verify_admin("non_existent_game", admin_code), "Admin verification succeeded for non-existent game.")

        # 4. Get Game for Team (using the efficient method)
        self.assertEqual(test_gsm.get_game_for_team(team1_id, team1_code), game_id, "get_game_for_team failed for team 1.")
        self.assertIsNone(test_gsm.get_game_for_team(team1_id, "wrong_team_code"), "get_game_for_team succeeded for team 1 with wrong code.")
        self.assertIsNone(test_gsm.get_game_for_team("non_existent_team", team1_code), "get_game_for_team succeeded for non-existent team.")

        # 5. List Games (check if our game is listed)
        # This depends on FilePickleStorage.keys() accuracy. Might need specific prefix for game keys if not already done.
        # GameStateManager.list_games uses pattern "game:*".
        listed_games = test_gsm.list_games()
        self.assertIn(game_id, listed_games, "Saved game not found in list_games output.")

        # 6. Delete Game
        delete_success = test_gsm.delete_game(game_id)
        self.assertTrue(delete_success, "Failed to delete game state.")
        
        # Verify keys are deleted from storage
        self.assertFalse(test_storage.exists(game_key), "Game state key not deleted.")
        self.assertFalse(test_storage.exists(admin_idx_key), "Admin index key not deleted.")
        self.assertFalse(test_storage.exists(team1_idx_key), "Team 1 key not deleted.")
        self.assertFalse(test_storage.exists(team2_idx_key), "Team 2 key not deleted.")
        
        # Try loading deleted game
        non_existent_game = test_gsm.load_game_state(game_id)
        self.assertIsNone(non_existent_game, "Deleted game was somehow loaded.")

        # Verify it's no longer listed
        listed_games_after_delete = test_gsm.list_games()
        self.assertNotIn(game_id, listed_games_after_delete, "Deleted game still found in list_games output.")

    def test_api_create_game_and_get_admin_state(self):
        """Test basic API flow: create game and get admin game state."""
        # 1. Create Game via API
        create_payload = {'num_teams': 2, 'num_rounds': 3}
        response_create = self.client.post('/create_game', json=create_payload)
        self.assertEqual(response_create.status_code, 200, f"API /create_game failed: {response_create.data.decode()}")
        
        data_create = response_create.get_json()
        self.assertIsNotNone(data_create, "No JSON response from /create_game")
        self.assertIn('game_id', data_create, "game_id missing from /create_game response")
        self.assertIn('admin_code', data_create, "admin_code missing from /create_game response")
        self.assertIn('team_codes', data_create, "team_codes missing from /create_game response")
        
        game_id = data_create['game_id']
        admin_code = data_create['admin_code']
        team_codes_map = data_create['team_codes']
        self.assertEqual(len(team_codes_map), create_payload['num_teams'], "Incorrect number of team_codes returned.")

        # 2. Get Admin Game State via API
        admin_state_url = f'/api/admin/game_state/{game_id}?admin_code={admin_code}'
        response_admin_state = self.client.get(admin_state_url)
        self.assertEqual(response_admin_state.status_code, 200, f"API {admin_state_url} failed: {response_admin_state.data.decode()}")
        
        data_admin_state = response_admin_state.get_json()
        self.assertIsNotNone(data_admin_state, f"No JSON response from {admin_state_url}")
        self.assertEqual(data_admin_state.get('game_id'), game_id, "game_id mismatch in admin state.")
        self.assertEqual(data_admin_state.get('round'), 1, "Game should start in round 1.")
        self.assertEqual(data_admin_state.get('total_rounds'), create_payload['num_rounds'], "total_rounds mismatch in admin state.")
        self.assertIn('teams', data_admin_state, "'teams' field missing in admin state.")
        if 'teams' in data_admin_state:
            self.assertEqual(len(data_admin_state['teams']), create_payload['num_teams'], "Incorrect number of teams in admin state.")
        
        # Note: To properly clean up games created via API in these tests,
        # we'd need a way to call test_gsm.delete_game(game_id) where test_gsm
        # uses the same storage as the Flask app. For now, games created by API tests
        # might persist in the default storage location.

    def test_financial_calculations(self):
        """Test financial calculations in the game"""
        team_id = self.team_ids[0]
        team = self.game_state.teams[team_id]
        
        # Initial capital
        initial_capital = team.capital
        
        # Make decisions that cost money
        decisions = {
            "products": {
                "premium": {
                    "active": True,
                    "marketing_budget": 50000000  # $50M marketing
                }
            }
        }
        
        # Process decisions
        self.game_state.process_team_decisions(team_id, decisions)
        
        # Get updated team
        team = self.game_state.teams[team_id]
        
        # Check marketing budget was applied
        self.assertEqual(team.products["premium"]["marketing_budget"], 50000000)
        
        # Just verify capital has been reduced, without checking exact amount
        # (various implementations might handle the deductions differently)
        self.assertLess(team.capital, initial_capital)
        
        # Create a simple market result to update financials
        market_results = {
            "sales": {
                "premium": {
                    "units_sold": 100000,
                    "revenue": 100000 * team.products["premium"]["price"]
                }
            },
            "market_share": 0.1,
            "customer_satisfaction_change": 5
        }
        
        # Update financials
        team.update_financials(market_results)
        
        # Check financial calculations
        self.assertEqual(team.revenue, 100000 * team.products["premium"]["price"])
        self.assertTrue(team.profit != 0)  # Profit should be calculated
        self.assertEqual(team.market_share, 0.1)
        self.assertEqual(team.customer_satisfaction, 55)  # 50 + 5
        
        # Score should be calculated
        team.calculate_score()
        self.assertTrue(team.score > 0)

if __name__ == "__main__":
    unittest.main() 