"""
Company Model for StrategyMasters: The Smartphone Industry Challenge
Represents each team's company with all relevant attributes and decision processing
"""

import copy  # For deep copying product defaults

# --- Initial Company Defaults ---
INITIAL_CAPITAL = 500000000  # $500M
INITIAL_RD_CAPABILITY = 50
INITIAL_PRODUCTION_CAPACITY = 500000  # Units per quarter
INITIAL_BRAND_STRENGTH = 50
INITIAL_QUALITY_CONTROL = 50
INITIAL_CUSTOMER_SATISFACTION = 50
INITIAL_INNOVATION_INDEX = 50
INITIAL_RD_EFFECTIVENESS = 50
INITIAL_ENVIRONMENTAL_IMPACT = 50  # Higher is better (less negative impact)
INITIAL_CSR_RATING = 50
INITIAL_EMPLOYEE_SATISFACTION = 50

# --- Product Segment Defaults ---
DEFAULT_PRODUCTS_CONFIG = {
    "premium": {
        "active": True, "price": 999, "quality": 80, "features": 80,
        "production_volume": 100000, "marketing_budget": 20000000
    },
    "mid_range": {
        "active": True, "price": 499, "quality": 60, "features": 60,
        "production_volume": 200000, "marketing_budget": 15000000
    },
    "budget": {
        "active": True, "price": 199, "quality": 40, "features": 40,
        "production_volume": 300000, "marketing_budget": 10000000
    }
}

# --- Decision Processing Factors ---
# R&D
RD_BUDGET_DIVISOR_CAPABILITY = 50000000.0
RD_CAPABILITY_POINTS_PER_UNIT = 5.0
RD_EFFECTIVENESS_BOOST_FACTOR = 0.4
RD_INNOVATION_BOOST_PER_ALLOCATION_POINT = 0.1
RD_PATENT_GAIN_BUDGET_DIVISOR = 100000000.0
# Operations
OPS_CAPACITY_INVESTMENT_COST_PER_UNIT = 10000.0
OPS_QUALITY_INVESTMENT_DIVISOR = 10000000.0
OPS_QUALITY_POINTS_PER_UNIT = 5.0
# Corporate Strategy
CORP_SUSTAINABILITY_INVESTMENT_DIVISOR = 5000000.0
CORP_SUSTAINABILITY_POINTS_PER_UNIT = 5.0
CORP_CSR_INVESTMENT_DIVISOR = 5000000.0
CORP_CSR_POINTS_PER_UNIT = 5.0
CORP_EMPLOYEE_INVESTMENT_DIVISOR = 5000000.0
CORP_EMPLOYEE_POINTS_PER_UNIT = 5.0
CORP_BRAND_INVESTMENT_DIVISOR = 20000000.0
CORP_BRAND_POINTS_PER_UNIT = 5.0

MAX_ATTRIBUTE_SCORE = 100.0
MIN_ATTRIBUTE_SCORE = 0.0

# --- Financial Calculation Factors ---
BASE_FIXED_COSTS = 10000000.0
UNIT_COST_BASE = {
    "premium": 300.0,
    "mid_range": 200.0,
    "budget": 100.0
}
UNIT_COST_QUALITY_FACTOR_DIVISOR = 50.0
UNIT_COST_FEATURE_FACTOR_DIVISOR = 50.0
UNIT_COST_RD_EFFICIENCY_BASE = 50.0
UNIT_COST_RD_EFFICIENCY_EFFECT_MAX = 0.2

# --- Scoring Factors ---
# Financial Score (40% of total)
FIN_SCORE_REVENUE_SCALE_DIVISOR = 10000000.0
FIN_SCORE_PROFIT_MARGIN_MULTIPLIER = 5.0
FIN_SCORE_CAPITAL_SCALE_DIVISOR = 10000000.0
FIN_SCORE_WEIGHT_REVENUE = 0.3
FIN_SCORE_WEIGHT_PROFIT = 0.3
FIN_SCORE_WEIGHT_ROI = 0.2
FIN_SCORE_WEIGHT_CAPITAL = 0.2

# Market Position Score (30% of total)
MARKET_SCORE_SHARE_MULTIPLIER = 100.0
MARKET_SCORE_WEIGHT_SHARE = 0.4
MARKET_SCORE_WEIGHT_BRAND = 0.3
MARKET_SCORE_WEIGHT_SATISFACTION = 0.2
MARKET_SCORE_WEIGHT_PORTFOLIO = 0.1

# Innovation & Growth Score (20% of total)
INNOV_SCORE_PATENT_MULTIPLIER = 10.0
INNOV_SCORE_WEIGHT_PATENT = 0.3
INNOV_SCORE_WEIGHT_INNOVATION_IDX = 0.3
INNOV_SCORE_WEIGHT_RD_EFFECTIVENESS = 0.2
INNOV_SCORE_WEIGHT_GROWTH_POTENTIAL = 0.2

# Sustainability Score (10% of total)
SUST_SCORE_WEIGHT_ENVIRONMENTAL = 0.3
SUST_SCORE_WEIGHT_CSR = 0.3
SUST_SCORE_WEIGHT_EMPLOYEE = 0.2
SUST_SCORE_WEIGHT_VIABILITY = 0.2
# Viability Score Thresholds
SUST_VIABILITY_PROFIT_MARGIN_MIN = 0.0
SUST_VIABILITY_CAPITAL_MIN = 100000000.0
SUST_VIABILITY_MARKET_SHARE_MIN = 0.05
SUST_VIABILITY_INNOVATION_INDEX_MIN = 50.0
SUST_VIABILITY_CUSTOMER_SATISFACTION_MIN = 60.0

# Overall Score Weights
OVERALL_SCORE_WEIGHT_FINANCIAL = 0.4
OVERALL_SCORE_WEIGHT_MARKET = 0.3
OVERALL_SCORE_WEIGHT_INNOVATION = 0.2
OVERALL_SCORE_WEIGHT_SUSTAINABILITY = 0.1

class Company:
    def __init__(self, team_id, name, capital=INITIAL_CAPITAL, r_d_capability=INITIAL_RD_CAPABILITY, 
                 production_capacity=INITIAL_PRODUCTION_CAPACITY, brand_strength=INITIAL_BRAND_STRENGTH):
        """Initialize a new company"""
        # Basic information
        self.team_id = team_id
        self.name = name
        
        # Financial attributes
        self.capital = float(capital)  # Ensure float for calculations
        self.revenue = 0.0
        self.costs = 0.0
        self.profit = 0.0
        self.profit_margin = 0.0
        self.roi = 0.0
        
        # Operational attributes
        self.r_d_capability = float(r_d_capability)
        self.production_capacity = float(production_capacity)
        self.brand_strength = float(brand_strength)
        self.quality_control = float(INITIAL_QUALITY_CONTROL)
        
        # Market attributes
        self.market_share = 0.0
        self.customer_satisfaction = float(INITIAL_CUSTOMER_SATISFACTION)
        
        # Innovation attributes
        self.patent_portfolio = 0.0
        self.innovation_index = float(INITIAL_INNOVATION_INDEX)
        self.r_d_effectiveness = float(INITIAL_RD_EFFECTIVENESS)
        
        # Sustainability attributes
        self.environmental_impact = float(INITIAL_ENVIRONMENTAL_IMPACT)
        self.csr_rating = float(INITIAL_CSR_RATING)
        self.employee_satisfaction = float(INITIAL_EMPLOYEE_SATISFACTION)
        
        # Product portfolio - Use deepcopy to ensure each instance has its own mutable dict
        self.products = copy.deepcopy(DEFAULT_PRODUCTS_CONFIG)
        
        # Decision history
        self.decisions_history = {}
        
        # Scoring
        self.score = 0.0
        self.financial_score = 0.0
        self.market_score = 0.0
        self.innovation_score = 0.0
        self.sustainability_score = 0.0
        
    def process_decisions(self, decisions, market):
        """Process decisions submitted by the team for the current round"""
        # Store decisions in history
        round_num = market.current_round
        self.decisions_history[round_num] = decisions
        
        # Process R&D decisions
        if "r_d" in decisions:
            r_d_budget = float(decisions["r_d"].get("budget", 0))
            r_d_focus = decisions["r_d"].get("focus", {})
            
            if r_d_budget > self.capital:
                r_d_budget = self.capital
            self.capital -= r_d_budget
            
            r_d_improvement = (r_d_budget / RD_BUDGET_DIVISOR_CAPABILITY) * RD_CAPABILITY_POINTS_PER_UNIT
            self.r_d_capability = min(MAX_ATTRIBUTE_SCORE, self.r_d_capability + r_d_improvement)

            r_d_effectiveness_boost = r_d_improvement * RD_EFFECTIVENESS_BOOST_FACTOR
            self.r_d_effectiveness = min(MAX_ATTRIBUTE_SCORE, max(MIN_ATTRIBUTE_SCORE, self.r_d_effectiveness + r_d_effectiveness_boost))
            
            innovation_boost = 0.0
            for area, allocation_value in r_d_focus.items():
                if area in ["camera", "battery", "processor", "display", "software"]:
                    innovation_boost += float(allocation_value) * RD_INNOVATION_BOOST_PER_ALLOCATION_POINT
            self.innovation_index = min(MAX_ATTRIBUTE_SCORE, max(MIN_ATTRIBUTE_SCORE, self.innovation_index + innovation_boost))
            
            patent_gain = r_d_budget / RD_PATENT_GAIN_BUDGET_DIVISOR
            self.patent_portfolio += patent_gain
        
        # Process product portfolio decisions
        if "products" in decisions:
            current_capital_before_marketing = self.capital 
            spent_on_marketing_this_round = 0.0

            for segment, product_decisions in decisions["products"].items():
                if segment in self.products:
                    self.products[segment]["active"] = bool(product_decisions.get("active", self.products[segment]["active"]))
                    
                    if self.products[segment]["active"]:
                        self.products[segment]["price"] = float(product_decisions.get("price", self.products[segment]["price"]))
                        self.products[segment]["quality"] = float(product_decisions.get("quality", self.products[segment]["quality"]))
                        self.products[segment]["features"] = float(product_decisions.get("features", self.products[segment]["features"]))
                        self.products[segment]["production_volume"] = float(product_decisions.get("production_volume", self.products[segment]["production_volume"]))
                        
                        marketing_budget_for_segment = float(product_decisions.get("marketing_budget", self.products[segment]["marketing_budget"]))                        
                        
                        affordable_marketing_budget = min(marketing_budget_for_segment, current_capital_before_marketing - spent_on_marketing_this_round)
                        if affordable_marketing_budget < 0: affordable_marketing_budget = 0.0
                        
                        self.products[segment]["marketing_budget"] = affordable_marketing_budget
                        self.capital -= affordable_marketing_budget
                        spent_on_marketing_this_round += affordable_marketing_budget
            
            total_production = sum(p["production_volume"] for p in self.products.values() if p["active"])
            if total_production > self.production_capacity:
                scale_factor = self.production_capacity / total_production if total_production > 0 else 0.0
                for p_data in self.products.values():
                    if p_data["active"]:
                        p_data["production_volume"] *= scale_factor
        
        # Process operations decisions
        if "operations" in decisions:
            ops_decisions = decisions["operations"]
            
            capacity_investment = float(ops_decisions.get("capacity_investment", 0))
            if capacity_investment > self.capital:
                capacity_investment = self.capital
            self.capital -= capacity_investment
            capacity_increase = capacity_investment / OPS_CAPACITY_INVESTMENT_COST_PER_UNIT
            self.production_capacity += capacity_increase
            
            quality_investment = float(ops_decisions.get("quality_investment", 0))
            if quality_investment > self.capital:
                quality_investment = self.capital
            self.capital -= quality_investment
            quality_improvement = (quality_investment / OPS_QUALITY_INVESTMENT_DIVISOR) * OPS_QUALITY_POINTS_PER_UNIT
            self.quality_control = min(MAX_ATTRIBUTE_SCORE, max(MIN_ATTRIBUTE_SCORE, self.quality_control + quality_improvement))
        
        # Process corporate strategy decisions
        if "corporate" in decisions:
            corp_decisions = decisions["corporate"]
            
            sustainability_investment = float(corp_decisions.get("sustainability_investment", 0))
            if sustainability_investment > self.capital:
                sustainability_investment = self.capital
            self.capital -= sustainability_investment
            sustainability_improvement = (sustainability_investment / CORP_SUSTAINABILITY_INVESTMENT_DIVISOR) * CORP_SUSTAINABILITY_POINTS_PER_UNIT
            self.environmental_impact = min(MAX_ATTRIBUTE_SCORE, max(MIN_ATTRIBUTE_SCORE, self.environmental_impact + sustainability_improvement))
            
            csr_investment = float(corp_decisions.get("csr_investment", 0))
            if csr_investment > self.capital:
                csr_investment = self.capital
            self.capital -= csr_investment
            csr_improvement = (csr_investment / CORP_CSR_INVESTMENT_DIVISOR) * CORP_CSR_POINTS_PER_UNIT
            self.csr_rating = min(MAX_ATTRIBUTE_SCORE, max(MIN_ATTRIBUTE_SCORE, self.csr_rating + csr_improvement))
            
            employee_investment = float(corp_decisions.get("employee_investment", 0))
            if employee_investment > self.capital:
                employee_investment = self.capital
            self.capital -= employee_investment
            employee_improvement = (employee_investment / CORP_EMPLOYEE_INVESTMENT_DIVISOR) * CORP_EMPLOYEE_POINTS_PER_UNIT
            self.employee_satisfaction = min(MAX_ATTRIBUTE_SCORE, max(MIN_ATTRIBUTE_SCORE, self.employee_satisfaction + employee_improvement))
            
            brand_investment = float(corp_decisions.get("brand_investment", 0))
            if brand_investment > self.capital:
                brand_investment = self.capital
            self.capital -= brand_investment
            brand_improvement = (brand_investment / CORP_BRAND_INVESTMENT_DIVISOR) * CORP_BRAND_POINTS_PER_UNIT
            self.brand_strength = min(MAX_ATTRIBUTE_SCORE, max(MIN_ATTRIBUTE_SCORE, self.brand_strength + brand_improvement))
    
    def update_financials(self, market_results):
        """Update company financials based on market results"""
        # Reset financial metrics for this round
        self.revenue = 0.0
        self.costs = 0.0
        
        # Calculate revenue from each product segment
        for segment, results in market_results.get("sales", {}).items():
            if segment in self.products and self.products[segment]["active"]:
                units_sold = float(results.get("units_sold", 0))
                price = float(self.products[segment]["price"])
                segment_revenue = units_sold * price
                self.revenue += segment_revenue
                
                # Calculate production costs
                unit_cost = self._calculate_unit_cost(segment)
                production_cost = units_sold * unit_cost
                self.costs += production_cost
        
        # Add fixed costs
        self.costs += BASE_FIXED_COSTS
        
        # Calculate profit
        self.profit = self.revenue - self.costs
        
        # Update capital
        self.capital += self.profit
        
        # Calculate profit margin
        if self.revenue > 0:
            self.profit_margin = (self.profit / self.revenue) * 100.0
        else:
            self.profit_margin = 0.0
            
        # Calculate ROI based on marketing investment for now (could be expanded)
        total_marketing_investment_this_round = sum(float(p["marketing_budget"]) for p in self.products.values() if p["active"])
        if total_marketing_investment_this_round > 0:
            self.roi = (self.profit / total_marketing_investment_this_round) * 100.0
        else:
            self.roi = 0.0
            
        # Update market share
        self.market_share = float(market_results.get("market_share", 0.0))
        
        # Update customer satisfaction
        satisfaction_change = float(market_results.get("customer_satisfaction_change", 0.0))
        self.customer_satisfaction = max(MIN_ATTRIBUTE_SCORE, min(MAX_ATTRIBUTE_SCORE, self.customer_satisfaction + satisfaction_change))
        
    def _calculate_unit_cost(self, segment):
        """Calculate the unit cost for a product segment"""
        # Base cost for segment
        unit_cost = float(UNIT_COST_BASE.get(segment, UNIT_COST_BASE["mid_range"])) # Default to mid_range if segment not found
        
        # Quality increases cost
        quality_factor = float(self.products[segment]["quality"]) / UNIT_COST_QUALITY_FACTOR_DIVISOR 
        unit_cost *= quality_factor
        
        # Features increase cost
        feature_factor = float(self.products[segment]["features"]) / UNIT_COST_FEATURE_FACTOR_DIVISOR
        unit_cost *= feature_factor
        
        # R&D capability can reduce costs through efficiency
        # Scaled around 0: e.g. if r_d_capability is 50 (base), metric is 0. If 100, metric is 1. If 0, metric is -1.
        r_d_efficiency_metric = (self.r_d_capability - UNIT_COST_RD_EFFICIENCY_BASE) / UNIT_COST_RD_EFFICIENCY_BASE 
        # Max cost reduction or increase is capped by UNIT_COST_RD_EFFICIENCY_EFFECT_MAX (e.g. 20%)
        cost_reduction_factor = r_d_efficiency_metric * UNIT_COST_RD_EFFICIENCY_EFFECT_MAX
        # Apply capped reduction: 1 - (capped factor). e.g. if factor is 0.1 (10% reduction), multiply by 0.9
        unit_cost *= (1.0 - min(UNIT_COST_RD_EFFICIENCY_EFFECT_MAX, max(-UNIT_COST_RD_EFFICIENCY_EFFECT_MAX, cost_reduction_factor)))
        
        return max(0.0, unit_cost) # Ensure unit cost is not negative
        
    def calculate_score(self):
        """Calculate the overall score based on the balanced scorecard approach"""
        # Financial Performance (40%)
        if self.revenue > 0:
            revenue_score = min(MAX_ATTRIBUTE_SCORE, self.revenue / FIN_SCORE_REVENUE_SCALE_DIVISOR)
            profit_score = min(MAX_ATTRIBUTE_SCORE, max(MIN_ATTRIBUTE_SCORE, self.profit_margin * FIN_SCORE_PROFIT_MARGIN_MULTIPLIER))
            roi_score = min(MAX_ATTRIBUTE_SCORE, max(MIN_ATTRIBUTE_SCORE, self.roi)) # ROI is already a percentage, so direct use after clamping
            capital_score = min(MAX_ATTRIBUTE_SCORE, self.capital / FIN_SCORE_CAPITAL_SCALE_DIVISOR)
            
            self.financial_score = (revenue_score * FIN_SCORE_WEIGHT_REVENUE + 
                                   profit_score * FIN_SCORE_WEIGHT_PROFIT + 
                                   roi_score * FIN_SCORE_WEIGHT_ROI + 
                                   capital_score * FIN_SCORE_WEIGHT_CAPITAL)
        else:
            self.financial_score = MIN_ATTRIBUTE_SCORE # Or 0.0 directly
            
        # Market Position (30%)
        market_share_score = min(MAX_ATTRIBUTE_SCORE, max(MIN_ATTRIBUTE_SCORE, self.market_share * MARKET_SCORE_SHARE_MULTIPLIER))
        brand_score = self.brand_strength # Assumed to be 0-100 already
        satisfaction_score = self.customer_satisfaction # Assumed to be 0-100 already
        
        active_products = sum(1 for p in self.products.values() if p["active"])
        num_total_segments = len(self.products)
        portfolio_score = (float(active_products) / num_total_segments) * MAX_ATTRIBUTE_SCORE if num_total_segments > 0 else MIN_ATTRIBUTE_SCORE
        
        self.market_score = (market_share_score * MARKET_SCORE_WEIGHT_SHARE + 
                             brand_score * MARKET_SCORE_WEIGHT_BRAND + 
                             satisfaction_score * MARKET_SCORE_WEIGHT_SATISFACTION + 
                             portfolio_score * MARKET_SCORE_WEIGHT_PORTFOLIO)
        
        # Innovation & Growth (20%)
        patent_score = min(MAX_ATTRIBUTE_SCORE, self.patent_portfolio * INNOV_SCORE_PATENT_MULTIPLIER)
        innovation_idx_score = self.innovation_index # Direct use, assumed 0-100
        rd_effectiveness_score = self.r_d_effectiveness # Direct use, assumed 0-100
        # Growth potential: average of r_d_capability and innovation_index
        growth_potential = min(MAX_ATTRIBUTE_SCORE, (self.r_d_capability + self.innovation_index) / 2.0)
        
        self.innovation_score = (patent_score * INNOV_SCORE_WEIGHT_PATENT + 
                                 innovation_idx_score * INNOV_SCORE_WEIGHT_INNOVATION_IDX + 
                                 rd_effectiveness_score * INNOV_SCORE_WEIGHT_RD_EFFECTIVENESS + 
                                 growth_potential * INNOV_SCORE_WEIGHT_GROWTH_POTENTIAL)
        
        # Sustainability (10%)
        environmental_score = self.environmental_impact # Direct use, assumed 0-100
        csr_score = self.csr_rating # Direct use, assumed 0-100
        employee_score = self.employee_satisfaction # Direct use, assumed 0-100
        
        # Calculate long-term viability based on multiple factors
        viability_factors_met = [
            self.profit_margin > SUST_VIABILITY_PROFIT_MARGIN_MIN,
            self.capital > SUST_VIABILITY_CAPITAL_MIN,
            self.market_share > SUST_VIABILITY_MARKET_SHARE_MIN,
            self.innovation_index > SUST_VIABILITY_INNOVATION_INDEX_MIN,
            self.customer_satisfaction > SUST_VIABILITY_CUSTOMER_SATISFACTION_MIN
        ]
        num_viability_factors = len(viability_factors_met)
        viability_score = (float(sum(viability_factors_met)) / num_viability_factors) * MAX_ATTRIBUTE_SCORE if num_viability_factors > 0 else MIN_ATTRIBUTE_SCORE
        
        self.sustainability_score = (environmental_score * SUST_SCORE_WEIGHT_ENVIRONMENTAL + 
                                   csr_score * SUST_SCORE_WEIGHT_CSR + 
                                   employee_score * SUST_SCORE_WEIGHT_EMPLOYEE + 
                                   viability_score * SUST_SCORE_WEIGHT_VIABILITY)
        
        # Calculate total score with weightings
        self.score = (self.financial_score * OVERALL_SCORE_WEIGHT_FINANCIAL + 
                     self.market_score * OVERALL_SCORE_WEIGHT_MARKET + 
                     self.innovation_score * OVERALL_SCORE_WEIGHT_INNOVATION + 
                     self.sustainability_score * OVERALL_SCORE_WEIGHT_SUSTAINABILITY)
                     
        return self.score
        
    def get_state(self):
        """Get the current state of the company for display or limited info sharing."""
        # Products are mutable; return a deep copy to prevent external modification of internal state.
        products_state = copy.deepcopy(self.products)
        return {
            "team_id": self.team_id,
            "name": self.name,
            "financial": {
                "capital": self.capital,
                "revenue": self.revenue,
                "costs": self.costs,
                "profit": self.profit,
                "profit_margin": self.profit_margin,
                "roi": self.roi
            },
            "operational": {
                "r_d_capability": self.r_d_capability,
                "production_capacity": self.production_capacity,
                "brand_strength": self.brand_strength,
                "quality_control": self.quality_control
            },
            "market": {
                "market_share": self.market_share,
                "customer_satisfaction": self.customer_satisfaction
            },
            "innovation": {
                "patent_portfolio": self.patent_portfolio,
                "innovation_index": self.innovation_index,
                "r_d_effectiveness": self.r_d_effectiveness
            },
            "sustainability": {
                "environmental_impact": self.environmental_impact,
                "csr_rating": self.csr_rating,
                "employee_satisfaction": self.employee_satisfaction
            },
            "products": products_state,
            "scores": {
                "total": self.score,
                "financial": self.financial_score,
                "market": self.market_score,
                "innovation": self.innovation_score,
                "sustainability": self.sustainability_score
            }
        }
        
    def to_dict(self):
        """Convert company to dictionary for serialization."""
        # Decisions history keys are round numbers (integers or strings),
        # values are decision dicts. Standard dict copy should be fine.
        # Products should be deep copied to ensure serialized state is independent.
        return {
            "team_id": self.team_id,
            "name": self.name,
            "capital": self.capital,
            "revenue": self.revenue,
            "costs": self.costs,
            "profit": self.profit,
            "profit_margin": self.profit_margin,
            "roi": self.roi,
            "r_d_capability": self.r_d_capability,
            "production_capacity": self.production_capacity,
            "brand_strength": self.brand_strength,
            "quality_control": self.quality_control,
            "market_share": self.market_share,
            "customer_satisfaction": self.customer_satisfaction,
            "patent_portfolio": self.patent_portfolio,
            "innovation_index": self.innovation_index,
            "r_d_effectiveness": self.r_d_effectiveness,
            "environmental_impact": self.environmental_impact,
            "csr_rating": self.csr_rating,
            "employee_satisfaction": self.employee_satisfaction,
            "products": copy.deepcopy(self.products),
            "decisions_history": self.decisions_history.copy(), # Shallow copy for decision history is likely sufficient
            "score": self.score,
            "financial_score": self.financial_score,
            "market_score": self.market_score,
            "innovation_score": self.innovation_score,
            "sustainability_score": self.sustainability_score
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create a company instance from dictionary data."""
        # Use .get for constructor arguments that might be missing in old data, providing defaults.
        company = cls(
            team_id=data["team_id"], # team_id and name are considered mandatory
            name=data["name"],
            capital=float(data.get("capital", INITIAL_CAPITAL)),
            r_d_capability=float(data.get("r_d_capability", INITIAL_RD_CAPABILITY)),
            production_capacity=float(data.get("production_capacity", INITIAL_PRODUCTION_CAPACITY)),
            brand_strength=float(data.get("brand_strength", INITIAL_BRAND_STRENGTH))
        )
        
        # Restore other attributes using .get() for robustness and providing defaults from constants.
        company.revenue = float(data.get("revenue", 0.0))
        company.costs = float(data.get("costs", 0.0))
        company.profit = float(data.get("profit", 0.0))
        company.profit_margin = float(data.get("profit_margin", 0.0))
        company.roi = float(data.get("roi", 0.0))
        company.quality_control = float(data.get("quality_control", INITIAL_QUALITY_CONTROL))
        company.market_share = float(data.get("market_share", 0.0))
        company.customer_satisfaction = float(data.get("customer_satisfaction", INITIAL_CUSTOMER_SATISFACTION))
        company.patent_portfolio = float(data.get("patent_portfolio", 0.0))
        company.innovation_index = float(data.get("innovation_index", INITIAL_INNOVATION_INDEX))
        company.r_d_effectiveness = float(data.get("r_d_effectiveness", INITIAL_RD_EFFECTIVENESS))
        company.environmental_impact = float(data.get("environmental_impact", INITIAL_ENVIRONMENTAL_IMPACT))
        company.csr_rating = float(data.get("csr_rating", INITIAL_CSR_RATING))
        company.employee_satisfaction = float(data.get("employee_satisfaction", INITIAL_EMPLOYEE_SATISFACTION))
        
        # Products: deep copy from data, or use default if not present/empty.
        products_data = data.get("products")
        if products_data: # Check if products_data is not None and not empty
            company.products = copy.deepcopy(products_data)
        else:
            company.products = copy.deepcopy(DEFAULT_PRODUCTS_CONFIG)
            
        # Decisions history: ensure it's a dict, default to empty dict.
        decisions_hist_data = data.get("decisions_history", {})
        company.decisions_history = decisions_hist_data.copy() if isinstance(decisions_hist_data, dict) else {}
        
        company.score = float(data.get("score", 0.0))
        company.financial_score = float(data.get("financial_score", 0.0))
        company.market_score = float(data.get("market_score", 0.0))
        company.innovation_score = float(data.get("innovation_score", 0.0))
        company.sustainability_score = float(data.get("sustainability_score", 0.0))
        
        return company
