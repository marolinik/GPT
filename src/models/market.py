"""
Market Model for StrategyMasters: The Smartphone Industry Challenge
Simulates market dynamics, consumer behavior, and competitive interactions
"""

import random
import math

class Market:
    def __init__(self):
        """Initialize the market simulation"""
        self.current_round = 0
        self.total_market_size = 10000000  # 10 million units per quarter
        self.market_growth_rate = 0.05  # 5% annual growth
        
        # Market segments
        self.segments = {
            "premium": {
                "size": 0.2,  # 20% of total market
                "price_sensitivity": 0.3,  # Low price sensitivity (0-1)
                "quality_importance": 0.8,  # High quality importance (0-1)
                "feature_importance": 0.9,  # High feature importance (0-1)
                "brand_importance": 0.7,  # High brand importance (0-1)
                "avg_price": 999,  # Average price point
                "price_range": [699, 1499]  # Min-max price range
            },
            "mid_range": {
                "size": 0.5,  # 50% of total market
                "price_sensitivity": 0.6,  # Medium price sensitivity
                "quality_importance": 0.6,  # Medium quality importance
                "feature_importance": 0.6,  # Medium feature importance
                "brand_importance": 0.5,  # Medium brand importance
                "avg_price": 499,  # Average price point
                "price_range": [299, 699]  # Min-max price range
            },
            "budget": {
                "size": 0.3,  # 30% of total market
                "price_sensitivity": 0.9,  # High price sensitivity
                "quality_importance": 0.4,  # Low quality importance
                "feature_importance": 0.3,  # Low feature importance
                "brand_importance": 0.3,  # Low brand importance
                "avg_price": 199,  # Average price point
                "price_range": [99, 299]  # Min-max price range
            }
        }
        
        # Market trends
        self.trends = {
            "camera_importance": 0.5,
            "battery_importance": 0.6,
            "processor_importance": 0.7,
            "display_importance": 0.5,
            "software_importance": 0.6,
            "sustainability_importance": 0.4,
            "innovation_preference": 0.5
        }
        
        # External factors
        self.external_factors = {
            "economic_strength": 0.7,  # 0-1, higher is stronger economy
            "technology_advancement": 0.5,  # 0-1, higher is faster advancement
            "competitive_intensity": 0.6,  # 0-1, higher is more intense
            "regulatory_pressure": 0.4  # 0-1, higher is more regulation
        }
        
    def update_market_conditions(self, round_number):
        """Update market conditions for the current round"""
        self.current_round = round_number
        
        # Update market size with growth
        growth_factor = 1 + (self.market_growth_rate / 4)  # Quarterly growth
        self.total_market_size *= growth_factor
        
        # Adjust segment sizes based on trends and round progression
        if round_number > 5:  # Mid-game shift
            # Premium segment grows slightly
            self.segments["premium"]["size"] += 0.01
            self.segments["mid_range"]["size"] -= 0.005
            self.segments["budget"]["size"] -= 0.005
            
        if round_number > 8:  # Late-game shift
            # Innovation becomes more important
            self.trends["innovation_preference"] += 0.1
            self.trends["sustainability_importance"] += 0.1
            
        # Normalize segment sizes to ensure they sum to 1
        total_size = sum(segment["size"] for segment in self.segments.values())
        for segment in self.segments.values():
            segment["size"] /= total_size
            
        # Update external factors
        # Economic cycles
        economic_change = random.uniform(-0.1, 0.1)
        self.external_factors["economic_strength"] = max(0.1, min(1.0, 
                                                       self.external_factors["economic_strength"] + economic_change))
        
        # Technology advancement increases over time
        self.external_factors["technology_advancement"] = min(1.0, 
                                                           self.external_factors["technology_advancement"] + 0.05)
        
        # Competitive intensity fluctuates
        competitive_change = random.uniform(-0.05, 0.15)  # Bias toward increasing
        self.external_factors["competitive_intensity"] = max(0.3, min(1.0, 
                                                          self.external_factors["competitive_intensity"] + competitive_change))
        
        # Random trend shifts
        for trend in self.trends:
            change = random.uniform(-0.05, 0.05)
            self.trends[trend] = max(0.1, min(0.9, self.trends[trend] + change))
            
    def calculate_market_results(self, companies):
        """Calculate market results based on company decisions"""
        results = {}
        
        # Calculate segment sizes in units
        segment_units = {
            segment: int(self.total_market_size * self.segments[segment]["size"])
            for segment in self.segments
        }
        
        # For each segment, calculate market share and sales for each company
        for segment, segment_info in self.segments.items():
            # Collect all companies competing in this segment
            competing_companies = {}
            for team_id, company in companies.items():
                if (segment in company.products and 
                    company.products[segment]["active"] and 
                    company.products[segment]["production_volume"] > 0):
                    competing_companies[team_id] = company
            
            # If no companies in this segment, continue
            if not competing_companies:
                continue
                
            # Calculate attractiveness score for each company in this segment
            attractiveness_scores = {}
            total_attractiveness = 0
            
            for team_id, company in competing_companies.items():
                product = company.products[segment]
                
                # Price attractiveness (inverse relationship)
                price = product["price"]
                price_range = segment_info["price_range"]
                price_position = (price_range[1] - price) / (price_range[1] - price_range[0])
                price_position = max(0, min(1, price_position))  # Clamp between 0-1
                price_score = price_position ** segment_info["price_sensitivity"]
                
                # Quality attractiveness
                quality = product["quality"]
                quality_score = (quality / 100) ** segment_info["quality_importance"]
                
                # Features attractiveness
                features = product["features"]
                feature_score = (features / 100) ** segment_info["feature_importance"]
                
                # Brand attractiveness
                brand = company.brand_strength
                brand_score = (brand / 100) ** segment_info["brand_importance"]
                
                # Marketing effectiveness
                marketing_budget = product["marketing_budget"]
                marketing_effectiveness = min(1, marketing_budget / 50000000)  # $50M for max effect
                
                # Innovation bonus
                innovation_bonus = (company.innovation_index / 100) * self.trends["innovation_preference"]
                
                # Sustainability bonus
                sustainability_bonus = (company.environmental_impact / 100) * self.trends["sustainability_importance"]
                
                # Calculate overall attractiveness
                attractiveness = (
                    price_score * 0.3 +
                    quality_score * 0.25 +
                    feature_score * 0.2 +
                    brand_score * 0.15 +
                    marketing_effectiveness * 0.1 +
                    innovation_bonus * 0.05 +
                    sustainability_bonus * 0.05
                )
                
                attractiveness_scores[team_id] = attractiveness
                total_attractiveness += attractiveness
            
            # Calculate market share for each company in this segment
            market_shares = {}
            if total_attractiveness > 0:
                for team_id, attractiveness in attractiveness_scores.items():
                    market_shares[team_id] = attractiveness / total_attractiveness
            else:
                # Equal distribution if all have zero attractiveness
                equal_share = 1.0 / len(competing_companies)
                for team_id in competing_companies:
                    market_shares[team_id] = equal_share
            
            # Calculate units sold for each company
            segment_total_units = segment_units[segment]
            for team_id, market_share in market_shares.items():
                company = competing_companies[team_id]
                potential_units = int(segment_total_units * market_share)
                
                # Limited by production capacity
                actual_units = min(potential_units, company.products[segment]["production_volume"])
                
                # Initialize company results if not exists
                if team_id not in results:
                    results[team_id] = {
                        "sales": {},
                        "market_share": 0,
                        "customer_satisfaction_change": 0
                    }
                
                # Store sales results
                results[team_id]["sales"][segment] = {
                    "units_sold": actual_units,
                    "revenue": actual_units * company.products[segment]["price"],
                    "market_share": market_share
                }
                
                # Calculate customer satisfaction change
                price_satisfaction = price_score - 0.5  # -0.5 to 0.5
                quality_satisfaction = quality_score - 0.5  # -0.5 to 0.5
                
                # If demand exceeds supply, satisfaction decreases
                supply_demand_ratio = min(1, company.products[segment]["production_volume"] / potential_units)
                supply_satisfaction = (supply_demand_ratio - 0.5) * 2  # -1 to 1
                
                satisfaction_change = (
                    price_satisfaction * 3 +
                    quality_satisfaction * 5 +
                    supply_satisfaction * 2
                ) / 10
                
                results[team_id]["customer_satisfaction_change"] += satisfaction_change * 5  # Scale to -5 to +5
        
        # Calculate overall market share for each company
        total_units = sum(segment_units.values())
        for team_id, company_results in results.items():
            total_company_units = sum(
                segment["units_sold"] for segment in company_results["sales"].values()
            )
            company_results["market_share"] = total_company_units / total_units if total_units > 0 else 0
        
        return results
    
    def generate_report(self, round_number):
        """Generate a market report for the current round"""
        return {
            "round": round_number,
            "total_market_size": self.total_market_size,
            "market_growth_rate": self.market_growth_rate,
            "segments": self.segments,
            "trends": self.trends,
            "external_factors": self.external_factors,
            "insights": self._generate_market_insights(round_number)
        }
    
    def _generate_market_insights(self, round_number):
        """Generate market insights based on current conditions"""
        insights = []
        
        # Economic insights
        if self.external_factors["economic_strength"] > 0.7:
            insights.append("Consumer spending is strong, premium segment shows growth potential.")
        elif self.external_factors["economic_strength"] < 0.4:
            insights.append("Economic downturn is affecting consumer spending. Budget segment may see increased demand.")
        
        # Technology insights
        if self.external_factors["technology_advancement"] > 0.7:
            insights.append("Rapid technological advancement is creating opportunities for innovation.")
        
        # Competitive insights
        if self.external_factors["competitive_intensity"] > 0.8:
            insights.append("Market is highly competitive. Differentiation is crucial for success.")
        
        # Trend insights
        highest_trend = max(self.trends.items(), key=lambda x: x[1])
        insights.append(f"Consumer interest in {highest_trend[0].replace('_', ' ')} is particularly strong.")
        
        # Segment-specific insights
        largest_segment = max(self.segments.items(), key=lambda x: x[1]["size"])
        insights.append(f"The {largest_segment[0]} segment represents {int(largest_segment[1]['size']*100)}% of the market.")
        
        # Round-specific insights
        if round_number == 1:
            insights.append("Market is in early development stage with room for all players to establish position.")
        elif round_number == 5:
            insights.append("Mid-game market consolidation is beginning. Strategic positioning is crucial.")
        elif round_number == 8:
            insights.append("Late-game market maturity approaching. Innovation and sustainability gaining importance.")
        
        return insights
    
    def to_dict(self):
        """Convert market to dictionary for serialization"""
        return {
            "current_round": self.current_round,
            "total_market_size": self.total_market_size,
            "market_growth_rate": self.market_growth_rate,
            "segments": self.segments,
            "trends": self.trends,
            "external_factors": self.external_factors
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a market instance from dictionary data"""
        market = cls()
        market.current_round = data["current_round"]
        market.total_market_size = data["total_market_size"]
        market.market_growth_rate = data["market_growth_rate"]
        market.segments = data["segments"]
        market.trends = data["trends"]
        market.external_factors = data["external_factors"]
        return market
