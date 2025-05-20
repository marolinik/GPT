"""
Events Model for StrategyMasters: The Smartphone Industry Challenge
Defines strategic events that impact the game and market conditions
"""

import random

class Event:
    def __init__(self, event_id, title, description, round, impact_areas, impact_values):
        """Initialize a new strategic event"""
        self.event_id = event_id
        self.title = title
        self.description = description
        self.round = round
        self.impact_areas = impact_areas  # Dictionary of areas affected
        self.impact_values = impact_values  # Dictionary of impact values
        
    def apply_impact(self, game_state):
        """Apply the event's impact to the game state"""
        # Impact on market
        if "market" in self.impact_areas:
            market_impacts = self.impact_areas["market"]
            for area, impact in market_impacts.items():
                if area == "total_market_size":
                    game_state.market.total_market_size *= (1 + self.impact_values["market"][area])
                elif area == "market_growth_rate":
                    game_state.market.market_growth_rate += self.impact_values["market"][area]
                elif area.startswith("segment_"):
                    segment = area.split("_")[1]
                    if segment in game_state.market.segments:
                        game_state.market.segments[segment]["size"] *= (1 + self.impact_values["market"][area])
                elif area in game_state.market.trends:
                    game_state.market.trends[area] += self.impact_values["market"][area]
                elif area in game_state.market.external_factors:
                    game_state.market.external_factors[area] += self.impact_values["market"][area]
        
        # Normalize segment sizes after changes
        total_size = sum(segment["size"] for segment in game_state.market.segments.values())
        for segment in game_state.market.segments.values():
            segment["size"] /= total_size
            
        # Impact on companies (all or specific)
        if "companies" in self.impact_areas:
            company_impacts = self.impact_areas["companies"]
            for team_id, company in game_state.teams.items():
                # Check if this company is affected
                if "all" in company_impacts or team_id in company_impacts:
                    impacts = company_impacts.get("all", {})
                    if team_id in company_impacts:
                        impacts.update(company_impacts[team_id])
                        
                    for area, impact in impacts.items():
                        impact_value = self.impact_values["companies"].get("all", {}).get(area, 0)
                        if team_id in self.impact_values.get("companies", {}):
                            impact_value = self.impact_values["companies"][team_id].get(area, impact_value)
                            
                        if area == "capital":
                            company.capital *= (1 + impact_value)
                        elif area == "r_d_capability":
                            company.r_d_capability = max(0, min(100, company.r_d_capability + impact_value))
                        elif area == "production_capacity":
                            company.production_capacity *= (1 + impact_value)
                        elif area == "brand_strength":
                            company.brand_strength = max(0, min(100, company.brand_strength + impact_value))
                        elif area == "quality_control":
                            company.quality_control = max(0, min(100, company.quality_control + impact_value))
                        elif area == "customer_satisfaction":
                            company.customer_satisfaction = max(0, min(100, company.customer_satisfaction + impact_value))
                        elif area == "innovation_index":
                            company.innovation_index = max(0, min(100, company.innovation_index + impact_value))
                        elif area == "environmental_impact":
                            company.environmental_impact = max(0, min(100, company.environmental_impact + impact_value))
                            
    def to_dict(self):
        """Convert event to dictionary for serialization"""
        return {
            "event_id": self.event_id,
            "title": self.title,
            "description": self.description,
            "round": self.round,
            "impact_areas": self.impact_areas,
            "impact_values": self.impact_values
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create an event instance from dictionary data"""
        return cls(
            event_id=data["event_id"],
            title=data["title"],
            description=data["description"],
            round=data["round"],
            impact_areas=data["impact_areas"],
            impact_values=data["impact_values"]
        )
        
    @classmethod
    def generate_random_event(cls, round_number):
        """Generate a random event appropriate for the current round"""
        # List of possible events
        events = [
            # Technology events
            {
                "title": "Breakthrough in Battery Technology",
                "description": "A major breakthrough in battery technology has been announced, potentially doubling smartphone battery life. Companies with strong R&D capabilities can capitalize on this innovation.",
                "impact_areas": {
                    "market": ["battery_importance", "innovation_preference"],
                    "companies": {"all": ["r_d_capability"]}
                },
                "impact_values": {
                    "market": {"battery_importance": 0.2, "innovation_preference": 0.1},
                    "companies": {"all": {"r_d_capability": 5}}
                }
            },
            {
                "title": "Revolutionary Display Technology",
                "description": "A new display technology has emerged that offers better resolution, lower power consumption, and improved durability. Early adopters may gain significant market advantage.",
                "impact_areas": {
                    "market": ["display_importance", "innovation_preference"],
                    "companies": {"all": ["innovation_index"]}
                },
                "impact_values": {
                    "market": {"display_importance": 0.15, "innovation_preference": 0.1},
                    "companies": {"all": {"innovation_index": 5}}
                }
            },
            
            # Economic events
            {
                "title": "Economic Downturn",
                "description": "A global economic slowdown is affecting consumer spending. Budget-conscious consumers are delaying smartphone upgrades and seeking more affordable options.",
                "impact_areas": {
                    "market": ["economic_strength", "segment_budget", "segment_premium"],
                    "companies": {"all": ["capital"]}
                },
                "impact_values": {
                    "market": {"economic_strength": -0.2, "segment_budget": 0.15, "segment_premium": -0.1},
                    "companies": {"all": {"capital": -0.05}}
                }
            },
            {
                "title": "Economic Boom",
                "description": "Strong economic growth has increased consumer spending power. Premium smartphone sales are expected to rise as consumers are willing to spend more on high-end devices.",
                "impact_areas": {
                    "market": ["economic_strength", "segment_premium", "segment_budget"],
                    "companies": {"all": ["capital"]}
                },
                "impact_values": {
                    "market": {"economic_strength": 0.2, "segment_premium": 0.15, "segment_budget": -0.1},
                    "companies": {"all": {"capital": 0.05}}
                }
            },
            
            # Regulatory events
            {
                "title": "New Environmental Regulations",
                "description": "Governments worldwide have introduced stricter environmental regulations for electronics manufacturing. Companies must invest in sustainable practices or face penalties.",
                "impact_areas": {
                    "market": ["sustainability_importance", "regulatory_pressure"],
                    "companies": {"all": ["environmental_impact"]}
                },
                "impact_values": {
                    "market": {"sustainability_importance": 0.15, "regulatory_pressure": 0.2},
                    "companies": {"all": {"environmental_impact": -10}}
                }
            },
            {
                "title": "Data Privacy Legislation",
                "description": "New data privacy laws require smartphone manufacturers to implement additional security features. Companies with strong software capabilities will adapt more easily.",
                "impact_areas": {
                    "market": ["software_importance", "regulatory_pressure"],
                    "companies": {"all": ["r_d_capability"]}
                },
                "impact_values": {
                    "market": {"software_importance": 0.1, "regulatory_pressure": 0.15},
                    "companies": {"all": {"r_d_capability": -5}}
                }
            },
            
            # Supply chain events
            {
                "title": "Component Shortage",
                "description": "A global shortage of key smartphone components is affecting production capacity across the industry. Companies with strong supplier relationships may be less impacted.",
                "impact_areas": {
                    "market": ["total_market_size"],
                    "companies": {"all": ["production_capacity"]}
                },
                "impact_values": {
                    "market": {"total_market_size": -0.1},
                    "companies": {"all": {"production_capacity": -0.15}}
                }
            },
            {
                "title": "New Manufacturing Technology",
                "description": "A new manufacturing process has been developed that significantly reduces production costs. Companies that invest in this technology can improve their cost structure.",
                "impact_areas": {
                    "market": ["competitive_intensity"],
                    "companies": {"all": ["production_capacity"]}
                },
                "impact_values": {
                    "market": {"competitive_intensity": 0.1},
                    "companies": {"all": {"production_capacity": 0.1}}
                }
            },
            
            # Consumer trend events
            {
                "title": "Camera-Focused Consumer Trend",
                "description": "Social media trends have increased consumer demand for smartphones with exceptional camera capabilities. Companies with strong camera technology will benefit.",
                "impact_areas": {
                    "market": ["camera_importance"],
                    "companies": {"all": ["customer_satisfaction"]}
                },
                "impact_values": {
                    "market": {"camera_importance": 0.2},
                    "companies": {"all": {"customer_satisfaction": 5}}
                }
            },
            {
                "title": "Gaming Smartphone Boom",
                "description": "Mobile gaming is experiencing explosive growth, driving demand for smartphones with powerful processors and gaming features.",
                "impact_areas": {
                    "market": ["processor_importance", "segment_premium"],
                    "companies": {"all": ["innovation_index"]}
                },
                "impact_values": {
                    "market": {"processor_importance": 0.15, "segment_premium": 0.05},
                    "companies": {"all": {"innovation_index": 5}}
                }
            }
        ]
        
        # Late-game events (only appear after round 5)
        late_game_events = [
            {
                "title": "Disruptive New Competitor",
                "description": "A well-funded startup has entered the market with a revolutionary smartphone concept that's gaining significant attention.",
                "impact_areas": {
                    "market": ["competitive_intensity", "total_market_size", "innovation_preference"],
                    "companies": {"all": ["market_share", "brand_strength"]}
                },
                "impact_values": {
                    "market": {"competitive_intensity": 0.2, "total_market_size": 0.05, "innovation_preference": 0.1},
                    "companies": {"all": {"market_share": -0.05, "brand_strength": -5}}
                }
            },
            {
                "title": "Industry Consolidation",
                "description": "Several smaller smartphone manufacturers have merged or been acquired, intensifying competition among the remaining players.",
                "impact_areas": {
                    "market": ["competitive_intensity", "total_market_size"],
                    "companies": {"all": ["market_share"]}
                },
                "impact_values": {
                    "market": {"competitive_intensity": 0.15, "total_market_size": -0.05},
                    "companies": {"all": {"market_share": 0.05}}
                }
            }
        ]
        
        # Add late-game events if appropriate
        if round_number > 5:
            events.extend(late_game_events)
            
        # Select a random event
        event_template = random.choice(events)
        
        # Create unique ID
        event_id = f"event_{round_number}_{random.randint(1000, 9999)}"
        
        return cls(
            event_id=event_id,
            title=event_template["title"],
            description=event_template["description"],
            round=round_number,
            impact_areas=event_template["impact_areas"],
            impact_values=event_template["impact_values"]
        )
