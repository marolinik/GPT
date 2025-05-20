"""
Market Model for StrategyMasters: The Smartphone Industry Challenge
Simulates market dynamics, consumer behavior, and competitive interactions
"""

import random
import math
import copy

# --- Initial Market Defaults ---
INITIAL_TOTAL_MARKET_SIZE = 10000000.0  # Units per quarter
INITIAL_MARKET_GROWTH_RATE = 0.05  # Annual growth rate (5%)

# --- Market Segments Configuration ---
# This will be deep-copied for the instance's segments attribute
DEFAULT_SEGMENTS_CONFIG = {
    "premium": {
        "size": 0.2, "price_sensitivity": 0.3, "quality_importance": 0.8,
        "feature_importance": 0.9, "brand_importance": 0.7,
        "avg_price": 999.0, "price_range": [699.0, 1499.0]
    },
    "mid_range": {
        "size": 0.5, "price_sensitivity": 0.6, "quality_importance": 0.6,
        "feature_importance": 0.6, "brand_importance": 0.5,
        "avg_price": 499.0, "price_range": [299.0, 699.0]
    },
    "budget": {
        "size": 0.3, "price_sensitivity": 0.9, "quality_importance": 0.4,
        "feature_importance": 0.3, "brand_importance": 0.3,
        "avg_price": 199.0, "price_range": [99.0, 299.0]
    }
}

# --- Market Trends Initial Values ---
INITIAL_TRENDS = {
    "camera_importance": 0.5, "battery_importance": 0.6,
    "processor_importance": 0.7, "display_importance": 0.5,
    "software_importance": 0.6, "sustainability_importance": 0.4,
    "innovation_preference": 0.5
}

# --- External Factors Initial Values ---
INITIAL_EXTERNAL_FACTORS = {
    "economic_strength": 0.7, "technology_advancement": 0.5,
    "competitive_intensity": 0.6, "regulatory_pressure": 0.4
}

# --- Market Update Dynamics ---
QUARTERLY_GROWTH_DIVISOR = 4.0 # For converting annual to quarterly growth
MID_GAME_SHIFT_ROUND = 5
LATE_GAME_SHIFT_ROUND = 8
PREMIUM_SEGMENT_GROWTH_MID_GAME = 0.01
MID_RANGE_SEGMENT_SHRINK_MID_GAME = 0.005 # Negative value means shrink
BUDGET_SEGMENT_SHRINK_MID_GAME = 0.005    # Negative value means shrink
INNOVATION_PREFERENCE_BOOST_LATE_GAME = 0.1
SUSTAINABILITY_IMPORTANCE_BOOST_LATE_GAME = 0.1

ECONOMIC_STRENGTH_CHANGE_MIN = -0.1
ECONOMIC_STRENGTH_CHANGE_MAX = 0.1
ECONOMIC_STRENGTH_MIN_BOUND = 0.1
ECONOMIC_STRENGTH_MAX_BOUND = 1.0

TECH_ADVANCEMENT_PER_ROUND = 0.05
TECH_ADVANCEMENT_MAX_BOUND = 1.0

COMPETITIVE_INTENSITY_CHANGE_MIN = -0.05
COMPETITIVE_INTENSITY_CHANGE_MAX = 0.15
COMPETITIVE_INTENSITY_MIN_BOUND = 0.3
COMPETITIVE_INTENSITY_MAX_BOUND = 1.0

TREND_VALUE_CHANGE_MIN = -0.05
TREND_VALUE_CHANGE_MAX = 0.05
TREND_VALUE_MIN_BOUND = 0.1
TREND_VALUE_MAX_BOUND = 0.9

# --- Market Results Calculation Factors ---
ATTRIBUTE_NORMALIZATION_DIVISOR = 100.0 # For quality, features, brand (0-100 scale)
MARKETING_EFFECTIVENESS_BUDGET_CAP = 50000000.0 # Budget for max marketing effectiveness

# Attractiveness Score Weights
ATTR_WEIGHT_PRICE = 0.3
ATTR_WEIGHT_QUALITY = 0.25
ATTR_WEIGHT_FEATURES = 0.20
ATTR_WEIGHT_BRAND = 0.15
ATTR_WEIGHT_MARKETING = 0.10
ATTR_WEIGHT_INNOVATION = 0.05
ATTR_WEIGHT_SUSTAINABILITY = 0.05

# Customer Satisfaction Change Factors
CUST_SAT_PRICE_FACTOR = 3.0
CUST_SAT_QUALITY_FACTOR = 5.0
CUST_SAT_SUPPLY_FACTOR = 2.0
CUST_SAT_TOTAL_DIVISOR = 10.0
CUST_SAT_OVERALL_SCALE_FACTOR = 5.0

# --- Market Insights Thresholds ---
INSIGHT_ECON_STRONG_THRESHOLD = 0.7
INSIGHT_ECON_WEAK_THRESHOLD = 0.4
INSIGHT_TECH_ADV_STRONG_THRESHOLD = 0.7
INSIGHT_COMPETITION_HIGH_THRESHOLD = 0.8
INSIGHT_ROUND_EARLY_GAME = 1
INSIGHT_ROUND_MID_GAME_CONSOLIDATION = 5
INSIGHT_ROUND_LATE_GAME_MATURITY = 8

class Market:
    def __init__(self):
        """Initialize the market simulation"""
        self.current_round = 0
        self.total_market_size = float(INITIAL_TOTAL_MARKET_SIZE)
        self.market_growth_rate = float(INITIAL_MARKET_GROWTH_RATE)
        
        # Market segments - deep copy to ensure instance has its own mutable dicts
        self.segments = copy.deepcopy(DEFAULT_SEGMENTS_CONFIG)
        
        # Market trends - copy the dictionary
        self.trends = INITIAL_TRENDS.copy()
        
        # External factors - copy the dictionary
        self.external_factors = INITIAL_EXTERNAL_FACTORS.copy()
        
    def update_market_conditions(self, round_number):
        """Update market conditions for the current round"""
        self.current_round = round_number
        
        # Update market size with growth
        growth_factor = 1.0 + (self.market_growth_rate / QUARTERLY_GROWTH_DIVISOR)  # Quarterly growth
        self.total_market_size *= growth_factor
        
        # Adjust segment sizes based on trends and round progression
        if round_number > MID_GAME_SHIFT_ROUND:  # Mid-game shift
            self.segments["premium"]["size"] += PREMIUM_SEGMENT_GROWTH_MID_GAME
            self.segments["mid_range"]["size"] -= MID_RANGE_SEGMENT_SHRINK_MID_GAME # Effectively adding a negative
            self.segments["budget"]["size"] -= BUDGET_SEGMENT_SHRINK_MID_GAME    # Effectively adding a negative
            
        if round_number > LATE_GAME_SHIFT_ROUND:  # Late-game shift
            self.trends["innovation_preference"] = min(TREND_VALUE_MAX_BOUND, self.trends["innovation_preference"] + INNOVATION_PREFERENCE_BOOST_LATE_GAME)
            self.trends["sustainability_importance"] = min(TREND_VALUE_MAX_BOUND, self.trends["sustainability_importance"] + SUSTAINABILITY_IMPORTANCE_BOOST_LATE_GAME)
            
        # Normalize segment sizes to ensure they sum to 1
        current_total_segment_size = sum(segment["size"] for segment in self.segments.values())
        if current_total_segment_size > 0: # Avoid division by zero
            for segment_data in self.segments.values(): # Renamed segment to segment_data
                segment_data["size"] /= current_total_segment_size
        else: # Fallback: if all segments are zero somehow, reset to defaults (or handle error)
            # This case should ideally not be reached if initial sizes are non-zero and changes are small.
            # For robustness, one might re-initialize to default proportions.
            # For now, if this happens, they remain 0 or whatever they were.
            pass 
            
        # Update external factors
        # Economic cycles
        economic_change = random.uniform(ECONOMIC_STRENGTH_CHANGE_MIN, ECONOMIC_STRENGTH_CHANGE_MAX)
        self.external_factors["economic_strength"] = max(ECONOMIC_STRENGTH_MIN_BOUND, min(ECONOMIC_STRENGTH_MAX_BOUND, 
                                                       self.external_factors["economic_strength"] + economic_change))
        
        # Technology advancement increases over time
        self.external_factors["technology_advancement"] = min(TECH_ADVANCEMENT_MAX_BOUND, 
                                                           self.external_factors["technology_advancement"] + TECH_ADVANCEMENT_PER_ROUND)
        
        # Competitive intensity fluctuates
        competitive_change = random.uniform(COMPETITIVE_INTENSITY_CHANGE_MIN, COMPETITIVE_INTENSITY_CHANGE_MAX)
        self.external_factors["competitive_intensity"] = max(COMPETITIVE_INTENSITY_MIN_BOUND, min(COMPETITIVE_INTENSITY_MAX_BOUND, 
                                                          self.external_factors["competitive_intensity"] + competitive_change))
        
        # Random trend shifts (for trends not specifically boosted by late game stage)
        for trend_key in self.trends: # Renamed trend to trend_key
            if not (round_number > LATE_GAME_SHIFT_ROUND and trend_key in ["innovation_preference", "sustainability_importance"]):
                change = random.uniform(TREND_VALUE_CHANGE_MIN, TREND_VALUE_CHANGE_MAX)
                self.trends[trend_key] = max(TREND_VALUE_MIN_BOUND, min(TREND_VALUE_MAX_BOUND, self.trends[trend_key] + change))
            
    def calculate_market_results(self, companies):
        """Calculate market results based on company decisions"""
        results = {}
        
        # Calculate segment sizes in units
        segment_units = {
            segment_name: int(self.total_market_size * segment_info["size"])
            for segment_name, segment_info in self.segments.items()
        }
        
        # For each segment, calculate market share and sales for each company
        for segment_name, segment_info in self.segments.items(): # Renamed segment to segment_name
            competing_companies = {}
            for team_id, company in companies.items():
                if (segment_name in company.products and 
                    company.products[segment_name]["active"] and 
                    company.products[segment_name]["production_volume"] > 0):
                    competing_companies[team_id] = company
            
            if not competing_companies:
                continue
                
            attractiveness_scores = {}
            total_attractiveness = 0.0
            
            for team_id, company in competing_companies.items():
                product = company.products[segment_name]
                
                price = float(product["price"])
                price_range_min = float(segment_info["price_range"][0])
                price_range_max = float(segment_info["price_range"][1])
                # Price position: 1.0 if price is at min_range, 0.0 if at max_range
                price_denominator = price_range_max - price_range_min
                price_position = (price_range_max - price) / price_denominator if price_denominator > 0 else 0.5 # Avoid div by zero, default to mid if range is zero
                price_position = max(0.0, min(1.0, price_position))
                price_score = price_position ** float(segment_info["price_sensitivity"]) # price_sensitivity is 0-1
                
                quality = float(product["quality"])
                quality_score = (quality / ATTRIBUTE_NORMALIZATION_DIVISOR) ** float(segment_info["quality_importance"])
                
                features = float(product["features"])
                feature_score = (features / ATTRIBUTE_NORMALIZATION_DIVISOR) ** float(segment_info["feature_importance"])
                
                brand = float(company.brand_strength)
                brand_score = (brand / ATTRIBUTE_NORMALIZATION_DIVISOR) ** float(segment_info["brand_importance"])
                
                marketing_budget = float(product["marketing_budget"])
                marketing_effectiveness = min(1.0, marketing_budget / MARKETING_EFFECTIVENESS_BUDGET_CAP)
                
                innovation_bonus = (float(company.innovation_index) / ATTRIBUTE_NORMALIZATION_DIVISOR) * float(self.trends["innovation_preference"])
                sustainability_bonus = (float(company.environmental_impact) / ATTRIBUTE_NORMALIZATION_DIVISOR) * float(self.trends["sustainability_importance"])
                
                attractiveness = (
                    price_score * ATTR_WEIGHT_PRICE +
                    quality_score * ATTR_WEIGHT_QUALITY +
                    feature_score * ATTR_WEIGHT_FEATURES +
                    brand_score * ATTR_WEIGHT_BRAND +
                    marketing_effectiveness * ATTR_WEIGHT_MARKETING +
                    innovation_bonus * ATTR_WEIGHT_INNOVATION +
                    sustainability_bonus * ATTR_WEIGHT_SUSTAINABILITY
                )
                
                attractiveness_scores[team_id] = attractiveness
                total_attractiveness += attractiveness
            
            market_shares = {}
            if total_attractiveness > 0:
                for team_id, attractiveness_val in attractiveness_scores.items(): # Renamed attractiveness
                    market_shares[team_id] = attractiveness_val / total_attractiveness
            elif competing_companies: # Avoid division by zero if total_attractiveness is 0 but companies exist
                equal_share = 1.0 / len(competing_companies)
                for team_id in competing_companies:
                    market_shares[team_id] = equal_share
            
            segment_total_units_available = float(segment_units[segment_name])
            for team_id, market_share_val in market_shares.items(): # Renamed market_share
                company = competing_companies[team_id]
                potential_units = segment_total_units_available * market_share_val
                
                actual_units_sold = min(potential_units, float(company.products[segment_name]["production_volume"]))
                
                if team_id not in results:
                    results[team_id] = {
                        "sales": {},
                        "market_share": 0.0,
                        "customer_satisfaction_change": 0.0
                    }
                
                results[team_id]["sales"][segment_name] = {
                    "units_sold": actual_units_sold,
                    "revenue": actual_units_sold * float(company.products[segment_name]["price"]),
                    "market_share": market_share_val # Segment-specific market share
                }
                
                price_satisfaction_score = price_score - 0.5  # Range -0.5 to 0.5
                quality_satisfaction_score = quality_score - 0.5  # Range -0.5 to 0.5
                
                supply_demand_ratio = min(1.0, float(company.products[segment_name]["production_volume"]) / potential_units) if potential_units > 0 else 1.0 # Avoid div by zero
                supply_satisfaction_score = (supply_demand_ratio - 0.5) * 2.0  # Range -1.0 to 1.0
                
                satisfaction_change_for_segment = (
                    price_satisfaction_score * CUST_SAT_PRICE_FACTOR +
                    quality_satisfaction_score * CUST_SAT_QUALITY_FACTOR +
                    supply_satisfaction_score * CUST_SAT_SUPPLY_FACTOR
                ) / CUST_SAT_TOTAL_DIVISOR
                
                results[team_id]["customer_satisfaction_change"] += satisfaction_change_for_segment * CUST_SAT_OVERALL_SCALE_FACTOR
        
        total_market_units_sold_overall = sum(s_info["units_sold"] for r_info in results.values() for s_info in r_info["sales"].values())
        for team_id, company_results_dict in results.items(): # Renamed company_results
            total_company_units_sold = sum(
                segment_sales_info["units_sold"] for segment_sales_info in company_results_dict["sales"].values()
            )
            # Overall market share for the company across all segments it sold in, relative to total market units for those segments
            # Or, it could be relative to total_market_size if that's more appropriate.
            # The original logic was total_company_units / total_units (where total_units was sum of segment_units.values() from market demand)
            # This seems more accurate to actual sales achieved by the company.
            if self.total_market_size > 0: # use initial total market size as base
                 company_results_dict["market_share"] = total_company_units_sold / self.total_market_size
            else:
                 company_results_dict["market_share"] = 0.0
        
        return results
    
    def generate_report(self, round_number):
        """Generate a market report for the current round"""
        return {
            "round": round_number,
            "total_market_size": self.total_market_size,
            "market_growth_rate": self.market_growth_rate,
            "segments": copy.deepcopy(self.segments), # Return a copy to prevent external modification
            "trends": self.trends.copy(),
            "external_factors": self.external_factors.copy(),
            "insights": self._generate_market_insights(round_number)
        }
    
    def _generate_market_insights(self, round_number):
        """Generate market insights based on current conditions"""
        insights = []
        
        # Economic insights
        if self.external_factors["economic_strength"] > INSIGHT_ECON_STRONG_THRESHOLD:
            insights.append("Consumer spending is strong, premium segment shows growth potential.")
        elif self.external_factors["economic_strength"] < INSIGHT_ECON_WEAK_THRESHOLD:
            insights.append("Economic downturn is affecting consumer spending. Budget segment may see increased demand.")
        
        # Technology insights
        if self.external_factors["technology_advancement"] > INSIGHT_TECH_ADV_STRONG_THRESHOLD:
            insights.append("Rapid technological advancement is creating opportunities for innovation.")
        
        # Competitive insights
        if self.external_factors["competitive_intensity"] > INSIGHT_COMPETITION_HIGH_THRESHOLD:
            insights.append("Market is highly competitive. Differentiation is crucial for success.")
        
        # Trend insights
        if self.trends: # Ensure trends is not empty
            highest_trend_key, highest_trend_value = max(self.trends.items(), key=lambda item: item[1])
            insights.append(f"Consumer interest in {highest_trend_key.replace('_', ' ')} is particularly strong.")
        
        # Segment-specific insights
        if self.segments: # Ensure segments is not empty
            largest_segment_name, largest_segment_info = max(self.segments.items(), key=lambda item: item[1]["size"])
            insights.append(f"The {largest_segment_name} segment represents {int(largest_segment_info['size']*100.0)}% of the market.")
        
        # Round-specific insights
        if round_number == INSIGHT_ROUND_EARLY_GAME:
            insights.append("Market is in early development stage with room for all players to establish position.")
        elif round_number == INSIGHT_ROUND_MID_GAME_CONSOLIDATION:
            insights.append("Mid-game market consolidation is beginning. Strategic positioning is crucial.")
        elif round_number == INSIGHT_ROUND_LATE_GAME_MATURITY:
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
