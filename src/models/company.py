"""
Company Model for StrategyMasters: The Smartphone Industry Challenge
Represents each team's company with all relevant attributes and decision processing
"""

class Company:
    def __init__(self, team_id, name, capital=500000000, r_d_capability=50, 
                 production_capacity=500000, brand_strength=50):
        """Initialize a new company"""
        # Basic information
        self.team_id = team_id
        self.name = name
        
        # Financial attributes
        self.capital = capital  # Cash reserves
        self.revenue = 0
        self.costs = 0
        self.profit = 0
        self.profit_margin = 0
        self.roi = 0
        
        # Operational attributes
        self.r_d_capability = r_d_capability  # Scale 0-100
        self.production_capacity = production_capacity  # Units per quarter
        self.brand_strength = brand_strength  # Scale 0-100
        self.quality_control = 50  # Scale 0-100
        
        # Market attributes
        self.market_share = 0
        self.customer_satisfaction = 50  # Scale 0-100
        
        # Innovation attributes
        self.patent_portfolio = 0
        self.innovation_index = 50  # Scale 0-100
        self.r_d_effectiveness = 50  # Scale 0-100
        
        # Sustainability attributes
        self.environmental_impact = 50  # Scale 0-100 (higher is better)
        self.csr_rating = 50  # Corporate Social Responsibility, scale 0-100
        self.employee_satisfaction = 50  # Scale 0-100
        
        # Product portfolio
        self.products = {
            "premium": {
                "active": False,
                "price": 0,
                "quality": 0,
                "features": 0,
                "production_volume": 0,
                "marketing_budget": 0
            },
            "mid_range": {
                "active": True,
                "price": 499,
                "quality": 60,
                "features": 60,
                "production_volume": 200000,
                "marketing_budget": 20000000
            },
            "budget": {
                "active": False,
                "price": 0,
                "quality": 0,
                "features": 0,
                "production_volume": 0,
                "marketing_budget": 0
            }
        }
        
        # Decision history
        self.decisions_history = {}
        
        # Scoring
        self.score = 0
        self.financial_score = 0
        self.market_score = 0
        self.innovation_score = 0
        self.sustainability_score = 0
        
    def process_decisions(self, decisions, market):
        """Process decisions submitted by the team for the current round"""
        # Store decisions in history
        round_num = market.current_round
        self.decisions_history[round_num] = decisions
        
        # Process R&D decisions
        if "r_d" in decisions:
            r_d_budget = decisions["r_d"].get("budget", 0)
            r_d_focus = decisions["r_d"].get("focus", {})
            
            # Ensure budget doesn't exceed available capital
            if r_d_budget > self.capital:
                r_d_budget = self.capital
                
            # Allocate budget
            self.capital -= r_d_budget
            
            # Update R&D capability based on investment
            r_d_improvement = (r_d_budget / 50000000) * 5  # 5 points per $50M
            self.r_d_capability = min(100, self.r_d_capability + r_d_improvement)
            
            # Update innovation index based on R&D focus
            innovation_boost = 0
            for area, allocation in r_d_focus.items():
                if area in ["camera", "battery", "processor", "display", "software"]:
                    innovation_boost += allocation * 0.1
            
            self.innovation_index = min(100, self.innovation_index + innovation_boost)
            
            # Patent portfolio grows with R&D investment
            patent_gain = r_d_budget / 100000000  # 1 patent per $100M
            self.patent_portfolio += patent_gain
        
        # Process product portfolio decisions
        if "products" in decisions:
            for segment, product_decisions in decisions["products"].items():
                if segment in self.products:
                    # Update product attributes
                    self.products[segment]["active"] = product_decisions.get("active", 
                                                      self.products[segment]["active"])
                    
                    if self.products[segment]["active"]:
                        self.products[segment]["price"] = product_decisions.get("price", 
                                                         self.products[segment]["price"])
                        self.products[segment]["quality"] = product_decisions.get("quality", 
                                                          self.products[segment]["quality"])
                        self.products[segment]["features"] = product_decisions.get("features", 
                                                           self.products[segment]["features"])
                        self.products[segment]["production_volume"] = product_decisions.get("production_volume", 
                                                                    self.products[segment]["production_volume"])
                        self.products[segment]["marketing_budget"] = product_decisions.get("marketing_budget", 
                                                                   self.products[segment]["marketing_budget"])
                        
                        # Ensure production volume doesn't exceed capacity
                        total_production = sum(p["production_volume"] for p in self.products.values() if p["active"])
                        if total_production > self.production_capacity:
                            # Scale back proportionally
                            scale_factor = self.production_capacity / total_production
                            for p in self.products.values():
                                if p["active"]:
                                    p["production_volume"] *= scale_factor
                        
                        # Deduct marketing budget from capital
                        marketing_cost = self.products[segment]["marketing_budget"]
                        if marketing_cost > self.capital:
                            self.products[segment]["marketing_budget"] = self.capital
                            marketing_cost = self.capital
                        
                        self.capital -= marketing_cost
        
        # Process operations decisions
        if "operations" in decisions:
            ops_decisions = decisions["operations"]
            
            # Production capacity investment
            capacity_investment = ops_decisions.get("capacity_investment", 0)
            if capacity_investment > self.capital:
                capacity_investment = self.capital
                
            self.capital -= capacity_investment
            capacity_increase = capacity_investment / 10000  # $10K per unit of capacity
            self.production_capacity += capacity_increase
            
            # Quality control investment
            quality_investment = ops_decisions.get("quality_investment", 0)
            if quality_investment > self.capital:
                quality_investment = self.capital
                
            self.capital -= quality_investment
            quality_improvement = (quality_investment / 10000000) * 5  # 5 points per $10M
            self.quality_control = min(100, self.quality_control + quality_improvement)
            
            # Supplier selection affects costs and quality
            supplier_quality = ops_decisions.get("supplier_quality", 50)  # Default medium quality
            # This will be used in financial calculations
        
        # Process corporate strategy decisions
        if "corporate" in decisions:
            corp_decisions = decisions["corporate"]
            
            # Sustainability initiatives
            sustainability_investment = corp_decisions.get("sustainability_investment", 0)
            if sustainability_investment > self.capital:
                sustainability_investment = self.capital
                
            self.capital -= sustainability_investment
            sustainability_improvement = (sustainability_investment / 5000000) * 5  # 5 points per $5M
            self.environmental_impact = min(100, self.environmental_impact + sustainability_improvement)
            
            # CSR initiatives
            csr_investment = corp_decisions.get("csr_investment", 0)
            if csr_investment > self.capital:
                csr_investment = self.capital
                
            self.capital -= csr_investment
            csr_improvement = (csr_investment / 5000000) * 5  # 5 points per $5M
            self.csr_rating = min(100, self.csr_rating + csr_improvement)
            
            # Employee programs
            employee_investment = corp_decisions.get("employee_investment", 0)
            if employee_investment > self.capital:
                employee_investment = self.capital
                
            self.capital -= employee_investment
            employee_improvement = (employee_investment / 5000000) * 5  # 5 points per $5M
            self.employee_satisfaction = min(100, self.employee_satisfaction + employee_improvement)
            
            # Brand building
            brand_investment = corp_decisions.get("brand_investment", 0)
            if brand_investment > self.capital:
                brand_investment = self.capital
                
            self.capital -= brand_investment
            brand_improvement = (brand_investment / 20000000) * 5  # 5 points per $20M
            self.brand_strength = min(100, self.brand_strength + brand_improvement)
    
    def update_financials(self, market_results):
        """Update company financials based on market results"""
        # Reset financial metrics for this round
        self.revenue = 0
        self.costs = 0
        
        # Calculate revenue from each product segment
        for segment, results in market_results.get("sales", {}).items():
            if segment in self.products and self.products[segment]["active"]:
                units_sold = results.get("units_sold", 0)
                price = self.products[segment]["price"]
                segment_revenue = units_sold * price
                self.revenue += segment_revenue
                
                # Calculate production costs
                unit_cost = self._calculate_unit_cost(segment)
                production_cost = units_sold * unit_cost
                self.costs += production_cost
        
        # Add fixed costs
        fixed_costs = 10000000  # $10M base fixed costs
        self.costs += fixed_costs
        
        # Calculate profit
        self.profit = self.revenue - self.costs
        
        # Update capital
        self.capital += self.profit
        
        # Calculate profit margin
        if self.revenue > 0:
            self.profit_margin = (self.profit / self.revenue) * 100
        else:
            self.profit_margin = 0
            
        # Calculate ROI
        total_investment = sum(p["marketing_budget"] for p in self.products.values() if p["active"])
        if total_investment > 0:
            self.roi = (self.profit / total_investment) * 100
        else:
            self.roi = 0
            
        # Update market share
        self.market_share = market_results.get("market_share", 0)
        
        # Update customer satisfaction
        satisfaction_change = market_results.get("customer_satisfaction_change", 0)
        self.customer_satisfaction = max(0, min(100, self.customer_satisfaction + satisfaction_change))
        
    def _calculate_unit_cost(self, segment):
        """Calculate the unit cost for a product segment"""
        base_costs = {
            "premium": 300,
            "mid_range": 200,
            "budget": 100
        }
        
        # Base cost for segment
        unit_cost = base_costs.get(segment, 200)
        
        # Quality increases cost
        quality_factor = self.products[segment]["quality"] / 50  # 1.0 at quality 50
        unit_cost *= quality_factor
        
        # Features increase cost
        feature_factor = self.products[segment]["features"] / 50  # 1.0 at features 50
        unit_cost *= feature_factor
        
        # R&D capability can reduce costs through efficiency
        r_d_efficiency = (self.r_d_capability - 50) / 100  # -0.5 to 0.5
        unit_cost *= (1 - (r_d_efficiency * 0.2))  # Up to 20% reduction
        
        return unit_cost
        
    def calculate_score(self):
        """Calculate the overall score based on the balanced scorecard approach"""
        # Financial Performance (40%)
        if self.revenue > 0:
            revenue_score = min(100, self.revenue / 10000000)  # $1B = 100 points
            profit_score = min(100, max(0, self.profit_margin * 5))  # 20% margin = 100 points
            roi_score = min(100, max(0, self.roi))  # 100% ROI = 100 points
            capital_score = min(100, self.capital / 10000000)  # $1B = 100 points
            
            self.financial_score = (revenue_score * 0.3 + profit_score * 0.3 + 
                                   roi_score * 0.2 + capital_score * 0.2)
        else:
            self.financial_score = 0
            
        # Market Position (30%)
        market_share_score = self.market_share * 100  # 100% market share = 100 points
        brand_score = self.brand_strength
        satisfaction_score = self.customer_satisfaction
        
        # Calculate portfolio strength
        active_products = sum(1 for p in self.products.values() if p["active"])
        portfolio_score = (active_products / len(self.products)) * 100
        
        self.market_score = (market_share_score * 0.4 + brand_score * 0.3 + 
                            satisfaction_score * 0.2 + portfolio_score * 0.1)
        
        # Innovation & Growth (20%)
        patent_score = min(100, self.patent_portfolio * 10)  # 10 patents = 100 points
        innovation_score = self.innovation_index
        r_d_score = self.r_d_effectiveness
        growth_potential = min(100, (self.r_d_capability + self.innovation_index) / 2)
        
        self.innovation_score = (patent_score * 0.3 + innovation_score * 0.3 + 
                                r_d_score * 0.2 + growth_potential * 0.2)
        
        # Sustainability (10%)
        environmental_score = self.environmental_impact
        csr_score = self.csr_rating
        employee_score = self.employee_satisfaction
        
        # Calculate long-term viability based on multiple factors
        viability_factors = [
            self.profit_margin > 0,  # Profitable
            self.capital > 100000000,  # Adequate capital
            self.market_share > 0.05,  # Significant market presence
            self.innovation_index > 50,  # Above average innovation
            self.customer_satisfaction > 60  # Good customer satisfaction
        ]
        viability_score = (sum(viability_factors) / len(viability_factors)) * 100
        
        self.sustainability_score = (environmental_score * 0.3 + csr_score * 0.3 + 
                                   employee_score * 0.2 + viability_score * 0.2)
        
        # Calculate total score with weightings
        self.score = (self.financial_score * 0.4 + 
                     self.market_score * 0.3 + 
                     self.innovation_score * 0.2 + 
                     self.sustainability_score * 0.1)
                     
        return self.score
        
    def get_state(self):
        """Get the current state of the company"""
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
            "products": self.products,
            "scores": {
                "total": self.score,
                "financial": self.financial_score,
                "market": self.market_score,
                "innovation": self.innovation_score,
                "sustainability": self.sustainability_score
            }
        }
        
    def to_dict(self):
        """Convert company to dictionary for serialization"""
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
            "products": self.products,
            "decisions_history": self.decisions_history,
            "score": self.score,
            "financial_score": self.financial_score,
            "market_score": self.market_score,
            "innovation_score": self.innovation_score,
            "sustainability_score": self.sustainability_score
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create a company instance from dictionary data"""
        company = cls(
            team_id=data["team_id"],
            name=data["name"],
            capital=data["capital"],
            r_d_capability=data["r_d_capability"],
            production_capacity=data["production_capacity"],
            brand_strength=data["brand_strength"]
        )
        
        # Restore all attributes
        company.revenue = data["revenue"]
        company.costs = data["costs"]
        company.profit = data["profit"]
        company.profit_margin = data["profit_margin"]
        company.roi = data["roi"]
        company.quality_control = data["quality_control"]
        company.market_share = data["market_share"]
        company.customer_satisfaction = data["customer_satisfaction"]
        company.patent_portfolio = data["patent_portfolio"]
        company.innovation_index = data["innovation_index"]
        company.r_d_effectiveness = data["r_d_effectiveness"]
        company.environmental_impact = data["environmental_impact"]
        company.csr_rating = data["csr_rating"]
        company.employee_satisfaction = data["employee_satisfaction"]
        company.products = data["products"]
        company.decisions_history = data["decisions_history"]
        company.score = data["score"]
        company.financial_score = data["financial_score"]
        company.market_score = data["market_score"]
        company.innovation_score = data["innovation_score"]
        company.sustainability_score = data["sustainability_score"]
        
        return company
