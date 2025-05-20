/**
 * Game Engine for StrategyMasters: The Smartphone Industry Challenge
 * Handles core game logic, state management, and API interactions
 */

class GameEngine {
    constructor(gameId, role, id, accessCode) {
        // Game identification
        this.gameId = gameId;
        this.role = role; // 'admin' or 'team'
        this.id = id; // team_id if role is 'team'
        this.accessCode = accessCode;
        
        // Game state
        this.gameState = null;
        this.currentRound = 0;
        this.totalRounds = 0;
        this.isFinished = false;
        
        // Decision tracking
        this.currentDecisions = {};
        this.hasSubmitted = false;
        
        // Polling
        this.pollingInterval = null;
        this.pollingDelay = 5000; // 5 seconds
        
        // Initialize
        this.init();
    }
    
    async init() {
        // Show loading indicator
        this.showLoading();
        
        // Fetch initial game state
        await this.fetchGameState();
        
        // Setup UI based on role
        if (this.role === 'admin') {
            this.setupAdminUI();
        } else {
            this.setupTeamUI();
        }
        
        // Start polling for updates
        this.startPolling();
        
        // Hide loading indicator
        this.hideLoading();
    }
    
    async fetchGameState() {
        try {
            let url;
            if (this.role === 'admin') {
                url = `/api/admin/game_state/${this.gameId}?admin_code=${this.accessCode}`;
            } else {
                url = `/api/team/game_state/${this.gameId}/${this.id}?team_code=${this.accessCode}`;
            }
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            this.gameState = data;
            // Support both team and admin responses
            this.currentRound = data.current_round || data.round;
            this.totalRounds = data.total_rounds;
            this.isFinished = data.finished || false;
            
            // Update UI with new state
            this.updateUI();
            
            return data;
        } catch (error) {
            console.error('Error fetching game state:', error);
            this.showError('Failed to fetch game state. Please check your connection and try again.');
        }
    }
    
    startPolling() {
        // Clear any existing polling
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }
        
        // Start new polling
        this.pollingInterval = setInterval(() => {
            this.fetchGameState();
        }, this.pollingDelay);
    }
    
    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }
    
    setupAdminUI() {
        // Admin-specific UI setup
        document.getElementById('startRoundBtn').addEventListener('click', () => this.startNewRound());
        document.getElementById('forceAdvanceBtn').addEventListener('click', () => this.forceAdvanceRound());
        
        // Setup tabs
        document.querySelectorAll('.nav-link').forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                const target = e.target.getAttribute('href');
                
                // Hide all tab contents
                document.querySelectorAll('.tab-pane').forEach(pane => {
                    pane.classList.remove('show', 'active');
                });
                
                // Show selected tab content
                document.querySelector(target).classList.add('show', 'active');
                
                // Update active tab
                document.querySelectorAll('.nav-link').forEach(t => {
                    t.classList.remove('active');
                });
                e.target.classList.add('active');
            });
        });
    }
    
    setupTeamUI() {
        // Team-specific UI setup
        document.getElementById('submitDecisionsBtn').addEventListener('click', () => this.submitDecisions());
        
        // Setup product segment toggles
        document.querySelectorAll('.segment-toggle').forEach(toggle => {
            toggle.addEventListener('change', (e) => {
                const segmentId = e.target.getAttribute('data-segment');
                const isActive = e.target.checked;
                
                // Update UI to show/hide segment details
                const segmentDetails = document.querySelector(`.segment-details[data-segment="${segmentId}"]`);
                if (segmentDetails) {
                    segmentDetails.style.display = isActive ? 'block' : 'none';
                }
                
                // Update current decisions
                if (!this.currentDecisions.products) {
                    this.currentDecisions.products = {};
                }
                
                if (!this.currentDecisions.products[segmentId]) {
                    this.currentDecisions.products[segmentId] = {};
                }
                
                this.currentDecisions.products[segmentId].active = isActive;
            });
        });
        
        // Setup numeric input handlers
        document.querySelectorAll('input[type="number"]').forEach(input => {
            input.addEventListener('change', (e) => {
                const category = e.target.getAttribute('data-category');
                const field = e.target.getAttribute('data-field');
                const value = parseFloat(e.target.value);
                
                if (category === 'product') {
                    const segment = e.target.getAttribute('data-segment');
                    
                    if (!this.currentDecisions.products) {
                        this.currentDecisions.products = {};
                    }
                    
                    if (!this.currentDecisions.products[segment]) {
                        this.currentDecisions.products[segment] = {};
                    }
                    
                    this.currentDecisions.products[segment][field] = value;
                } else {
                    if (!this.currentDecisions[category]) {
                        this.currentDecisions[category] = {};
                    }
                    
                    this.currentDecisions[category][field] = value;
                }
            });
        });
        
        // Setup tabs
        document.querySelectorAll('.nav-link').forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                const target = e.target.getAttribute('href');
                
                // Hide all tab contents
                document.querySelectorAll('.tab-pane').forEach(pane => {
                    pane.classList.remove('show', 'active');
                });
                
                // Show selected tab content
                document.querySelector(target).classList.add('show', 'active');
                
                // Update active tab
                document.querySelectorAll('.nav-link').forEach(t => {
                    t.classList.remove('active');
                });
                e.target.classList.add('active');
            });
        });
    }
    
    updateUI() {
        // Common UI updates
        document.getElementById('roundDisplay').textContent = `Round ${this.currentRound} of ${this.totalRounds}`;
        
        if (this.role === 'admin') {
            this.updateAdminUI();
        } else {
            this.updateTeamUI();
        }
    }
    
    updateAdminUI() {
        // Update admin-specific UI elements
        const teamsTable = document.getElementById('teamsTable');
        const teamsBody = document.getElementById('teamsTableBody');
        teamsBody.innerHTML = '';
        
        // Add team rows
        for (const [teamId, team] of Object.entries(this.gameState.teams)) {
            const row = document.createElement('tr');
            
            // Check if team has submitted for current round
            const hasSubmitted = this.gameState.round_results[this.currentRound]?.submissions?.includes(teamId) || false;
            if (hasSubmitted) {
                row.classList.add('decision-submitted');
            }
            
            row.innerHTML = `
                <td>${teamId}</td>
                <td>${team.name}</td>
                <td>$${Math.round(team.financial.capital / 1000000)}M</td>
                <td>${(team.market.market_share * 100).toFixed(1)}%</td>
                <td>${team.scores.total.toFixed(1)}</td>
                <td>${hasSubmitted ? '<span class="badge bg-success">Submitted</span>' : '<span class="badge bg-warning">Pending</span>'}</td>
            `;
            
            teamsBody.appendChild(row);
        }
        
        // Update round control buttons
        const startRoundBtn = document.getElementById('startRoundBtn');
        const forceAdvanceBtn = document.getElementById('forceAdvanceBtn');
        
        if (this.isFinished) {
            startRoundBtn.disabled = true;
            forceAdvanceBtn.disabled = true;
            startRoundBtn.textContent = 'Game Finished';
        } else {
            // Check if all teams have submitted
            const currentRoundStr = this.currentRound.toString();
            const submissions = this.gameState.round_results[currentRoundStr]?.submissions || [];
            const allSubmitted = Object.keys(this.gameState.teams).every(teamId => submissions.includes(teamId));
            
            startRoundBtn.disabled = !allSubmitted;
            forceAdvanceBtn.disabled = false;
            
            if (allSubmitted) {
                startRoundBtn.textContent = 'Start Next Round';
            } else {
                startRoundBtn.textContent = 'Waiting for All Teams';
            }
        }
        
        // Update market overview
        this.updateMarketOverview();
        
        // Update events list
        this.updateEventsList();
        
        // Update rankings
        this.updateRankings();
    }
    
    updateTeamUI() {
        // Update team-specific UI elements
        const company = this.gameState.company;
        
        // Update company stats
        document.getElementById('capitalValue').textContent = `$${Math.round(company.financial.capital / 1000000)}M`;
        document.getElementById('marketShareValue').textContent = `${(company.market.market_share * 100).toFixed(1)}%`;
        document.getElementById('brandStrengthValue').textContent = company.operational.brand_strength.toFixed(1);
        document.getElementById('rdCapabilityValue').textContent = company.operational.r_d_capability.toFixed(1);
        document.getElementById('scoreValue').textContent = company.scores.total.toFixed(1);
        
        // Update product segments
        for (const [segment, product] of Object.entries(company.products)) {
            const segmentToggle = document.querySelector(`.segment-toggle[data-segment="${segment}"]`);
            const segmentDetails = document.querySelector(`.segment-details[data-segment="${segment}"]`);
            
            if (segmentToggle && segmentDetails) {
                segmentToggle.checked = product.active;
                segmentDetails.style.display = product.active ? 'block' : 'none';
                
                // Update product fields
                document.querySelector(`input[data-category="product"][data-segment="${segment}"][data-field="price"]`).value = product.price;
                document.querySelector(`input[data-category="product"][data-segment="${segment}"][data-field="quality"]`).value = product.quality;
                document.querySelector(`input[data-category="product"][data-segment="${segment}"][data-field="features"]`).value = product.features;
                document.querySelector(`input[data-category="product"][data-segment="${segment}"][data-field="production_volume"]`).value = product.production_volume;
                document.querySelector(`input[data-category="product"][data-segment="${segment}"][data-field="marketing_budget"]`).value = product.marketing_budget;
            }
        }
        
        // Update market overview
        this.updateMarketOverview();
        
        // Update events list
        this.updateEventsList();
        
        // Update competitors overview
        this.updateCompetitorsOverview();
        
        // Update previous results if available
        if (this.gameState.previous_results) {
            this.updatePreviousResults();
        }
        
        // Check if team has already submitted for this round
        // Determine if this team has already submitted decisions for the
        // current round. The backend may provide a `submitted` flag or the
        // round results. Check both for robustness.
        const currentRoundStr = this.currentRound.toString();
        if (typeof this.gameState.submitted !== 'undefined') {
            this.hasSubmitted = this.gameState.submitted;
        } else {
            const submissions = this.gameState.round_results?.[currentRoundStr]?.submissions || [];
            this.hasSubmitted = submissions.includes(this.id);
        }
        
        const submitBtn = document.getElementById('submitDecisionsBtn');
        if (this.hasSubmitted) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Decisions Submitted';
            document.getElementById('decisionForm').classList.add('decision-submitted');
        } else {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Decisions';
            document.getElementById('decisionForm').classList.remove('decision-submitted');
        }
    }
    
    updateMarketOverview() {
        // Update market overview section for both admin and team views
        const market = this.gameState.market;
        
        document.getElementById('marketSizeValue').textContent = `${Math.round(market.total_market_size / 1000000)}M units`;
        document.getElementById('marketGrowthValue').textContent = `${(market.market_growth_rate * 100).toFixed(1)}%`;
        
        // Update segment sizes
        for (const [segment, data] of Object.entries(market.segments)) {
            const sizeElement = document.getElementById(`${segment}SizeValue`);
            if (sizeElement) {
                sizeElement.textContent = `${(data.size * 100).toFixed(1)}%`;
            }
        }
        
        // Update market insights
        const insightsList = document.getElementById('marketInsights');
        if (insightsList) {
            insightsList.innerHTML = '';
            market.insights.forEach(insight => {
                const li = document.createElement('li');
                li.className = 'list-group-item';
                li.textContent = insight;
                insightsList.appendChild(li);
            });
        }
    }
    
    updateEventsList() {
        // Update events list for both admin and team views
        const eventsList = document.getElementById('eventsList');
        if (eventsList) {
            eventsList.innerHTML = '';
            
            const events = this.role === 'admin' 
                ? this.gameState.events.filter(e => e.round === this.currentRound)
                : this.gameState.events;
                
            if (events.length === 0) {
                const noEvents = document.createElement('div');
                noEvents.className = 'alert alert-info';
                noEvents.textContent = 'No events for this round.';
                eventsList.appendChild(noEvents);
            } else {
                events.forEach(event => {
                    const eventCard = document.createElement('div');
                    eventCard.className = 'card event-card mb-3';
                    eventCard.innerHTML = `
                        <div class="card-header bg-danger text-white">
                            <h5 class="mb-0">${event.title}</h5>
                        </div>
                        <div class="card-body">
                            <p>${event.description}</p>
                        </div>
                    `;
                    eventsList.appendChild(eventCard);
                });
            }
        }
    }
    
    updateCompetitorsOverview() {
        // Update competitors overview for team view
        const competitorsList = document.getElementById('competitorsList');
        if (competitorsList && this.gameState.competitors) {
            competitorsList.innerHTML = '';
            
            for (const [teamId, competitor] of Object.entries(this.gameState.competitors)) {
                const competitorCard = document.createElement('div');
                competitorCard.className = 'card competitor-card mb-3';
                competitorCard.innerHTML = `
                    <div class="card-header bg-success text-white">
                        <h5 class="mb-0">${competitor.name}</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-6">
                                <p><strong>Market Share:</strong> ${(competitor.market_share * 100).toFixed(1)}%</p>
                            </div>
                            <div class="col-6">
                                <p><strong>Brand Strength:</strong> ${competitor.brand_strength.toFixed(1)}</p>
                            </div>
                        </div>
                    </div>
                `;
                competitorsList.appendChild(competitorCard);
            }
        }
    }
    
    updatePreviousResults() {
        // Update previous results for team view
        const results = this.gameState.previous_results;
        const resultsSection = document.getElementById('previousResults');
        
        if (resultsSection && results) {
            resultsSection.innerHTML = '';
            
            const resultsCard = document.createElement('div');
            resultsCard.className = 'card mb-3';
            resultsCard.innerHTML = `
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0">Previous Round Results</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Financial Results</h6>
                            <p><strong>Revenue:</strong> $${Math.round(results.company_state.financial.revenue / 1000000)}M</p>
                            <p><strong>Costs:</strong> $${Math.round(results.company_state.financial.costs / 1000000)}M</p>
                            <p><strong>Profit:</strong> $${Math.round(results.company_state.financial.profit / 1000000)}M</p>
                            <p><strong>Profit Margin:</strong> ${results.company_state.financial.profit_margin.toFixed(1)}%</p>
                        </div>
                        <div class="col-md-6">
                            <h6>Market Results</h6>
                            <p><strong>Market Share:</strong> ${(results.company_state.market.market_share * 100).toFixed(1)}%</p>
                            <p><strong>Customer Satisfaction:</strong> ${results.company_state.market.customer_satisfaction.toFixed(1)}</p>
                        </div>
                    </div>
                    
                    <h6 class="mt-3">Sales by Segment</h6>
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Segment</th>
                                    <th>Units Sold</th>
                                    <th>Revenue</th>
                                    <th>Market Share</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${Object.entries(results.market_results.sales || {}).map(([segment, data]) => `
                                    <tr>
                                        <td>${segment}</td>
                                        <td>${data.units_sold.toLocaleString()}</td>
                                        <td>$${Math.round(data.revenue / 1000000)}M</td>
                                        <td>${(data.market_share * 100).toFixed(1)}%</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
            
            resultsSection.appendChild(resultsCard);
        }
    }
    
    updateRankings() {
        // Update rankings for admin view
        if (this.role === 'admin') {
            fetch(`/api/rankings/${this.gameId}`)
                .then(response => response.json())
                .then(rankings => {
                    const rankingsBody = document.getElementById('rankingsTableBody');
                    if (rankingsBody) {
                        rankingsBody.innerHTML = '';
                        
                        rankings.forEach(team => {
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${team.rank}</td>
                                <td>${team.name}</td>
                                <td>${team.score.toFixed(1)}</td>
                                <td>${team.financial_score.toFixed(1)}</td>
                                <td>${team.market_score.toFixed(1)}</td>
                                <td>${team.innovation_score.toFixed(1)}</td>
                                <td>${team.sustainability_score.toFixed(1)}</td>
                            `;
                            rankingsBody.appendChild(row);
                        });
                    }
                })
                .catch(error => {
                    console.error('Error fetching rankings:', error);
                });
        }
    }
    
    async submitDecisions() {
        // Submit team decisions
        if (this.role !== 'team' || this.hasSubmitted) {
            return;
        }
        
        // Show loading indicator
        this.showLoading();
        
        try {
            const response = await fetch(`/api/team/submit_decisions/${this.gameId}/${this.id}?team_code=${this.accessCode}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.currentDecisions),
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                // Update UI to reflect submission
                this.hasSubmitted = true;
                document.getElementById('submitDecisionsBtn').disabled = true;
                document.getElementById('submitDecisionsBtn').textContent = 'Decisions Submitted';
                document.getElementById('decisionForm').classList.add('decision-submitted');
                
                // Show success message
                this.showSuccess('Decisions submitted successfully! Waiting for other teams and next round.');
                
                // Refresh game state
                await this.fetchGameState();
            } else {
                throw new Error(result.error || 'Unknown error');
            }
        } catch (error) {
            console.error('Error submitting decisions:', error);
            this.showError(`Failed to submit decisions: ${error.message}`);
        } finally {
            // Hide loading indicator
            this.hideLoading();
        }
    }
    
    async startNewRound() {
        // Start a new round (admin only)
        if (this.role !== 'admin') {
            return;
        }
        
        // Show loading indicator
        this.showLoading();
        
        try {
            const response = await fetch(`/api/admin/advance_round/${this.gameId}?admin_code=${this.accessCode}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ force: false }),
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                // Show success message using returned round number
                const newRound = result.current_round || result.round;
                this.showSuccess(`Advanced to round ${newRound}`);
                
                // Refresh game state
                await this.fetchGameState();
            } else {
                throw new Error(result.message || 'Unknown error');
            }
        } catch (error) {
            console.error('Error starting new round:', error);
            this.showError(`Failed to start new round: ${error.message}`);
        } finally {
            // Hide loading indicator
            this.hideLoading();
        }
    }
    
    async forceAdvanceRound() {
        // Force advance to next round (admin only)
        if (this.role !== 'admin') {
            return;
        }
        
        if (!confirm('Are you sure you want to force advance to the next round? Any teams that have not submitted decisions will miss their turn.')) {
            return;
        }
        
        // Show loading indicator
        this.showLoading();
        
        try {
            const response = await fetch(`/api/admin/advance_round/${this.gameId}?admin_code=${this.accessCode}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ force: true }),
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                // Show success message with returned round number
                const newRound = result.current_round || result.round;
                this.showSuccess(`Forced advance to round ${newRound}`);
                
                // Refresh game state
                await this.fetchGameState();
            } else {
                throw new Error(result.message || 'Unknown error');
            }
        } catch (error) {
            console.error('Error forcing round advance:', error);
            this.showError(`Failed to force round advance: ${error.message}`);
        } finally {
            // Hide loading indicator
            this.hideLoading();
        }
    }
    
    showLoading() {
        // Show loading overlay
        let loadingOverlay = document.getElementById('loadingOverlay');
        
        if (!loadingOverlay) {
            loadingOverlay = document.createElement('div');
            loadingOverlay.id = 'loadingOverlay';
            loadingOverlay.className = 'loading-overlay';
            loadingOverlay.innerHTML = `
                <div class="spinner-container">
                    <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Processing...</p>
                </div>
            `;
            document.body.appendChild(loadingOverlay);
        } else {
            loadingOverlay.style.display = 'flex';
        }
    }
    
    hideLoading() {
        // Hide loading overlay
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
    }
    
    showSuccess(message) {
        // Show success toast
        this.showToast(message, 'success');
    }
    
    showError(message) {
        // Show error toast
        this.showToast(message, 'danger');
    }
    
    showToast(message, type = 'info') {
        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('toastContainer');
        
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast
        const toastId = `toast-${Date.now()}`;
        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        // Show toast
        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: 5000
        });
        bsToast.show();
        
        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
}

// Initialize game engine when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Extract game parameters from URL
    const urlParams = new URLSearchParams(window.location.search);
    const pathParts = window.location.pathname.split('/');
    
    let gameId, role, id, accessCode;
    
    if (pathParts.includes('admin')) {
        role = 'admin';
        gameId = pathParts[pathParts.indexOf('admin') + 1];
        id = null;
        accessCode = urlParams.get('admin_code');
    } else if (pathParts.includes('team')) {
        role = 'team';
        gameId = pathParts[pathParts.indexOf('team') + 1];
        id = pathParts[pathParts.indexOf('team') + 2];
        accessCode = urlParams.get('team_code');
    }
    
    if (gameId && accessCode) {
        // Initialize game engine
        window.gameEngine = new GameEngine(gameId, role, id, accessCode);
    } else {
        console.error('Missing required parameters');
        alert('Missing required parameters. Please check the URL and try again.');
    }
});
