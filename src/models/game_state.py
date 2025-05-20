"""
Game State Model for StrategyMasters: The Smartphone Industry Challenge
Manages the overall state of the game, including rounds, teams, and market conditions
"""

import json
import random
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class GameState:
    def __init__(self, num_teams=5, num_rounds=10):
        """Initialize a new game state"""
        self.num_teams = num_teams
        self.num_rounds = num_rounds
        self.current_round = 0
        self.teams = {}
        self.market = None
        self.events = []
        self.round_results = {}
        self.game_id = f"game_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.started = False
        self.finished = False
        self.team_codes = {}  # Store team codes for authentication
        self.admin_code = None  # Store admin code for authentication
        
    def initialize_game(self):
        """Set up the initial game state"""
        from .company import Company
        from .market import Market
        
        # Create teams/companies
        for i in range(1, self.num_teams + 1):
            team_id = f"team_{i}"
            self.teams[team_id] = Company(
                team_id=team_id,
                name=f"Company {i}",
                capital=500000000,  # $500M starting capital
                r_d_capability=50,  # Base R&D capability (0-100)
                production_capacity=500000,  # Units per quarter
                brand_strength=50,  # Base brand strength (0-100)
            )
            
            # Generate a unique team code
            self.team_codes[team_id] = self._generate_code()
        
        # Generate admin code
        self.admin_code = self._generate_code()
        
        # Initialize market
        self.market = Market()
        
        # Set game as started
        self.started = True
        self.current_round = 1
        
        # Generate initial market report
        self._generate_market_report()
        
    def _generate_code(self, length=8):
        """Generate a random code for team or admin authentication"""
        chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        return ''.join(random.choice(chars) for _ in range(length))
        
    def start_new_round(self):
        """Start a new round of the game"""
        if self.current_round >= self.num_rounds:
            self.finished = True
            return False
            
        # Generate strategic events for this round
        new_events_this_round = self._generate_events()
        
        # Apply impacts of the new events for the current round
        logger.info(f"Applying {len(new_events_this_round)} new events for round {self.current_round}")
        for event in new_events_this_round:
            if event.round == self.current_round: # Ensure event is for the current round
                logger.info(f"Applying event: {event.title} (ID: {event.event_id})")
                event.apply_impact(self) # 'self' is the game_state instance
            else:
                logger.warning(f"Skipping event {event.title} (ID: {event.event_id}) intended for round {event.round}, current round is {self.current_round}")

        # Update market conditions
        if self.market:
            self.market.update_market_conditions(self.current_round)
            
        return True
        
    def process_team_decisions(self, team_id, decisions):
        """Process decisions submitted by a team"""
        if team_id not in self.teams:
            return False
            
        # Update company state based on decisions
        company = self.teams[team_id]
        company.process_decisions(decisions, self.market)
        
        # Mark team as having submitted decisions for this round
        if str(self.current_round) not in self.round_results:
            self.round_results[str(self.current_round)] = {"submissions": []}
            
        self.round_results[str(self.current_round)]["submissions"].append(team_id)
        
        # Check if all teams have submitted
        if len(self.round_results[str(self.current_round)]["submissions"]) == self.num_teams:
            self._finalize_round()
            
        return True
        
    def _finalize_round(self):
        """Calculate results after all teams have submitted decisions"""
        # Calculate market interactions
        market_results = self.market.calculate_market_results(self.teams)
        
        # Update each company based on market results
        for team_id, company in self.teams.items():
            company.update_financials(market_results.get(team_id, {}))
            company.calculate_score()
        
        # Store round results
        self.round_results[str(self.current_round)]["market_results"] = market_results
        self.round_results[str(self.current_round)]["company_states"] = {
            team_id: company.get_state() for team_id, company in self.teams.items()
        }
        
        # Advance to next round
        self.current_round += 1
        if self.current_round <= self.num_rounds:
            self.start_new_round()
        else:
            self.finished = True
            
    def _generate_events(self):
        """Generate strategic events for the current round"""
        from .events import Event
        
        # Number of events increases as game progresses
        num_events = 1 if self.current_round < 5 else 2
        
        generated_events_for_round = []
        for _ in range(num_events):
            event = Event.generate_random_event(self.current_round)
            generated_events_for_round.append(event)
            
        self.events.extend(generated_events_for_round) # Add to the main list of all events
        logger.info(f"Generated {len(generated_events_for_round)} events for round {self.current_round}. Total events now: {len(self.events)}")
        return generated_events_for_round # Return only the newly generated events
        
    def _generate_market_report(self):
        """Generate market report for the current round"""
        if not self.market:
            return {}
            
        return self.market.generate_report(self.current_round)
        
    def get_team_view(self, team_id):
        """Get the game state from a specific team's perspective"""
        logger.info(f"Getting team view for team {team_id}, game {self.game_id}")
        
        if team_id not in self.teams:
            logger.warning(f"Team not found: {team_id}")
            return None
            
        company = self.teams[team_id]
        
        # Compile market information
        market_info = self._generate_market_report()
        
        # Get current events
        current_events = [event.to_dict() for event in self.events 
                         if event.round == self.current_round]
        
        # Get limited information about competitors
        competitors = {}
        for tid, comp in self.teams.items():
            if tid != team_id:
                competitors[tid] = {
                    "name": comp.name,
                    "market_share": comp.market_share,
                    "brand_strength": comp.brand_strength,
                    # Only public information is available about competitors
                }
        
        # Compile previous round results if available
        previous_results = None
        if self.current_round > 1 and str(self.current_round - 1) in self.round_results:
            prev_round = str(self.current_round - 1)
            previous_results = {
                "company_state": self.round_results[prev_round]["company_states"].get(team_id),
                "market_results": self.round_results[prev_round]["market_results"].get(team_id)
            }
        
        team_view = {
            "round": self.current_round,
            "total_rounds": self.num_rounds,
            "company": company.get_state(),
            "market": market_info,
            "events": current_events,
            "competitors": competitors,
            "previous_results": previous_results
        }
        
        logger.info(f"Completed team view construction for team {team_id}, round {self.current_round}")
        return team_view
        
    def get_admin_view(self):
        """Get the complete game state for the admin/facilitator"""
        logger.info(f"Getting admin view for game {self.game_id}, round {self.current_round}")
        
        try:
            admin_view = {
                "game_id": self.game_id,
                "round": self.current_round,
                "total_rounds": self.num_rounds,
                "started": self.started,
                "finished": self.finished,
                "teams": {team_id: company.get_state() for team_id, company in self.teams.items()},
                "market": self._generate_market_report(),
                "events": [event.to_dict() for event in self.events], # Shows all historical events
                "round_results": self.round_results
            }
            
            logger.info(f"Completed admin view construction for game {self.game_id}, round {self.current_round}")
            return admin_view
            
        except Exception as e:
            logger.error(f"Error generating admin view for game {self.game_id}: {str(e)}", exc_info=True)
            # Return a minimal valid response
            return {
                "game_id": self.game_id,
                "round": self.current_round,
                "total_rounds": self.num_rounds,
                "error": "Error generating complete game state"
            }
        
    def get_rankings(self):
        """Get current team rankings based on scores"""
        rankings = []
        for team_id, company in self.teams.items():
            rankings.append({
                "team_id": team_id,
                "name": company.name,
                "score": company.score,
                "financial_score": company.financial_score,
                "market_score": company.market_score,
                "innovation_score": company.innovation_score,
                "sustainability_score": company.sustainability_score
            })
            
        # Sort by total score, descending
        rankings.sort(key=lambda x: x["score"], reverse=True)
        
        # Add rank
        for i, team in enumerate(rankings):
            team["rank"] = i + 1
            
        return rankings
    
    def to_dict(self):
        """
        Convert the game state to a dictionary for serialization
        Ensures all nested objects are properly serialized
        """
        try:
            logger.debug(f"Converting GameState {self.game_id} to dictionary")
            
            # Handle teams with explicit error checking
            teams_dict = {}
            if self.teams:
                for team_id, company in self.teams.items():
                    try:
                        if hasattr(company, 'to_dict') and callable(company.to_dict):
                            teams_dict[team_id] = company.to_dict()
                        else:
                            logger.warning(f"Company {team_id} missing to_dict method, using get_state")
                            teams_dict[team_id] = company.get_state()
                    except Exception as e:
                        logger.error(f"Error serializing team {team_id}: {e}")
                        # Provide a minimal fallback representation
                        teams_dict[team_id] = {"team_id": team_id, "name": getattr(company, 'name', 'Unknown')}
            
            # Handle market with explicit error checking
            market_dict = None
            if self.market:
                try:
                    if hasattr(self.market, 'to_dict') and callable(self.market.to_dict):
                        market_dict = self.market.to_dict()
                    else:
                        logger.warning("Market missing to_dict method, using generate_report")
                        market_dict = self.market.generate_report(self.current_round)
                except Exception as e:
                    logger.error(f"Error serializing market: {e}")
                    market_dict = {"error": "Could not serialize market data"}
            
            # Handle events with explicit error checking
            events_list = []
            for i, event in enumerate(self.events):
                try:
                    if hasattr(event, 'to_dict') and callable(event.to_dict):
                        events_list.append(event.to_dict())
                    else:
                        logger.warning(f"Event {i} missing to_dict method")
                        events_list.append({"description": str(event), "round": getattr(event, 'round', 0)})
                except Exception as e:
                    logger.error(f"Error serializing event {i}: {e}")
                    events_list.append({"error": f"Could not serialize event {i}"})
            
            # Create the main dictionary with all attributes
            state_dict = {
                "game_id": self.game_id,
                "num_teams": self.num_teams,
                "num_rounds": self.num_rounds,
                "current_round": self.current_round,
                "started": self.started,
                "finished": self.finished,
                "teams": teams_dict,
                "market": market_dict,
                "events": events_list,
                "round_results": self.round_results,  # This should already be JSON-serializable
                "team_codes": self.team_codes,  # Include team codes for authentication
                "admin_code": self.admin_code  # Include admin code for authentication
            }
            
            # Validate the dictionary is JSON-serializable
            try:
                json.dumps(state_dict)
                logger.debug(f"Successfully validated GameState dictionary is JSON-serializable")
            except (TypeError, OverflowError) as e:
                logger.error(f"GameState dictionary is not JSON-serializable: {e}")
                # This would require deeper inspection to fix all non-serializable objects
                
            return state_dict
            
        except Exception as e:
            logger.error(f"Unexpected error in GameState.to_dict: {e}", exc_info=True)
            # Return a minimal valid dictionary to prevent complete failure
            return {
                "game_id": self.game_id,
                "error": "Error serializing game state",
                "num_teams": self.num_teams,
                "num_rounds": self.num_rounds,
                "current_round": self.current_round
            }
        
    @classmethod
    def from_dict(cls, state_dict):
        """
        Create a GameState instance from a dictionary
        """
        try:
            logger.debug(f"Creating GameState from dictionary for game {state_dict.get('game_id', 'unknown')}")
            
            # Create a new instance
            game = cls(
                num_teams=state_dict.get("num_teams", 5),
                num_rounds=state_dict.get("num_rounds", 10)
            )
            
            # Set basic properties
            game.game_id = state_dict.get("game_id", game.game_id)
            game.current_round = state_dict.get("current_round", 0)
            game.started = state_dict.get("started", False)
            game.finished = state_dict.get("finished", False)
            game.team_codes = state_dict.get("team_codes", {})
            game.admin_code = state_dict.get("admin_code")
            game.events = [] # Initialize events list, will be populated from dict
            
            # Restore teams
            from .company import Company
            teams_dict = state_dict.get("teams", {})
            for team_id, team_data in teams_dict.items():
                try:
                    game.teams[team_id] = Company.from_dict(team_data)
                except Exception as e:
                    logger.error(f"Error deserializing team {team_id}: {e}")
                    # Create a minimal company object
                    game.teams[team_id] = Company(
                        team_id=team_id,
                        name=team_data.get("name", f"Company {team_id}"),
                        capital=team_data.get("capital", 500000000)
                    )
            
            # Restore market
            from .market import Market
            market_data = state_dict.get("market")
            if market_data:
                try:
                    game.market = Market.from_dict(market_data)
                except Exception as e:
                    logger.error(f"Error deserializing market: {e}")
                    game.market = Market()  # Create a default market
            
            # Restore events
            from .events import Event
            events_data = state_dict.get("events", [])
            for event_data in events_data:
                try:
                    game.events.append(Event.from_dict(event_data))
                except Exception as e:
                    logger.error(f"Error deserializing event: {e}")
                    # Skip this event
            
            # Restore round results
            game.round_results = state_dict.get("round_results", {})
            
            return game
            
        except Exception as e:
            logger.error(f"Unexpected error in GameState.from_dict: {e}", exc_info=True)
            # Return a minimal valid GameState
            game = cls()
            game.game_id = state_dict.get("game_id", game.game_id)
            return game
