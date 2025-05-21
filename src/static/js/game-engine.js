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
        this.currentDecisions = { // Initialize with the full new structure
            products: {
                premium: { active: true, price: 0, quality: 0, features: 0, production_volume: 0, marketing_budget: 0 },
                mid_range: { active: true, price: 0, quality: 0, features: 0, production_volume: 0, marketing_budget: 0 },
                budget: { active: true, price: 0, quality: 0, features: 0, production_volume: 0, marketing_budget: 0 }
            },
            r_d: {
                budget: 0,
                focus: { camera: 0, battery: 0, processor: 0, display: 0, software: 0 }
            },
            operations: { capacity_investment: 0, quality_investment: 0 },
            corporate: { brand_investment: 0, sustainability_investment: 0, csr_investment: 0, employee_investment: 0 }
        };
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
            
            console.log(`Fetching game state from: ${url}`);
            
            const response = await fetch(url);
            
            if (!response.ok) {
                console.error(`HTTP error! Status: ${response.status}, Url: ${url}`);
                const errorText = await response.text();
                console.error(`Error response: ${errorText}`);
                throw new Error(`HTTP error! Status: ${response.status}, Response: ${errorText}`);
            }
            
            const responseText = await response.text();
            
            let data;
            try {
                data = JSON.parse(responseText);
                console.log('Game state data received:', data);
            } catch (e) {
                console.error('Failed to parse JSON response:', responseText);
                throw new Error('Invalid JSON response from server');
            }
            
            if (!data || typeof data !== 'object') {
                console.error('Invalid game state data:', data);
                throw new Error('Invalid game state data received');
            }
            
            // Store full game state data
            this.gameState = data;
            
            // Parse key information with fallbacks
            this.currentRound = parseInt(data.round || data.current_round) || 1;
            this.totalRounds = parseInt(data.total_rounds) || 10;
            this.isFinished = Boolean(data.finished || data.is_finished);
            
            console.log(`Game state updated - Round: ${this.currentRound}, Total Rounds: ${this.totalRounds}, Finished: ${this.isFinished}`);
            console.log('Round results:', data.round_results);
            
            // Update UI with new state (wrapped in try/catch for safety)
            try {
                this.updateUI();
            } catch (uiError) {
                console.error('Error during UI update:', uiError);
                this.showError('Error updating the UI. Details: ' + uiError.message);
            }
            
            return data;
        } catch (error) {
            console.error('Error fetching game state:', error);
            this.stopPolling(); // Stop polling to avoid repeated error messages
            this.showError(`Failed to fetch game state. ${error.message}`);
            return null;
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
        const submitButton = document.getElementById('submitDecisionsBtn');
        if (submitButton) {
            submitButton.addEventListener('click', () => this.submitDecisions());
        }
        
        // Setup product segment toggles - with improved handling
        document.querySelectorAll('.segment-toggle').forEach(toggle => {
            toggle.addEventListener('change', (e) => {
                if (this.hasSubmitted) {
                    e.preventDefault();
                    e.target.checked = !e.target.checked; // Revert the change
                    this.showError('Cannot change decisions after submission for this round.');
                    return;
                }
                
                const segmentId = e.target.getAttribute('data-segment');
                const isActive = e.target.checked;
                
                const segmentDetails = document.querySelector(`.segment-details[data-segment="${segmentId}"]`);
                if (segmentDetails) {
                    segmentDetails.style.display = isActive ? 'block' : 'none';
                }
                
                // Ensure product segment exists in currentDecisions
                if (!this.currentDecisions.products[segmentId]) {
                    // If not, initialize from gameState or defaults (already handled by initial currentDecisions structure)
                    // This part might need refinement if gameState.company.products isn't immediately available
                    // For now, relying on the pre-initialized structure of this.currentDecisions
                     this.currentDecisions.products[segmentId] = { 
                        ...this.currentDecisions.products[segmentId], // spread existing defaults
                        active: isActive 
                    }; 
                } else {
                    this.currentDecisions.products[segmentId].active = isActive;
                }
                
                console.log(`Segment ${segmentId} active state changed to: ${isActive}`);
                console.log('Current decisions:', JSON.stringify(this.currentDecisions, null, 2));
            });
        });
        
        // Setup numeric input handlers with improved error handling
        document.querySelectorAll('input[type="number"]').forEach(input => {
            // Initial population of this.currentDecisions from form defaults OR gameState will be handled by updateTeamUI
            // Here, we just set up the change listeners.

            input.addEventListener('change', (e) => {
                if (this.hasSubmitted) {
                    // Attempt to restore previous value if submission has occurred
                    // This part is tricky as the "original" value needs to be sourced correctly
                    // For simplicity, we just show an error and prevent change. A better UX would revert.
                    e.preventDefault(); 
                    this.showError('Cannot change decisions after submission for this round.');
                    // To revert, you'd need to store the pre-change value or re-fetch from gameState.
                    // e.g., e.target.value = previousValue; 
                    return;
                }
                
                const category = e.target.getAttribute('data-category');
                const field = e.target.getAttribute('data-field');
                const value = parseFloat(e.target.value) || 0; // Ensure numeric conversion
                
                if (!category || !field) return;

                if (category === 'product') {
                    const segment = e.target.getAttribute('data-segment');
                    if (!segment) return;
                    // Ensure segment and product structures exist
                    if (!this.currentDecisions.products[segment]) {
                        this.currentDecisions.products[segment] = { active: true, price: 0, quality: 0, features: 0, production_volume: 0, marketing_budget: 0 };
                    }
                    this.currentDecisions.products[segment][field] = value;
                } else if (category === 'r_d') { // For rdBudget (data-category="r_d", data-field="budget")
                    this.currentDecisions.r_d[field] = value;
                } else if (category === 'r_d_focus') { // For rdFocusCamera etc. (data-category="r_d_focus", data-field="camera")
                    // Ensure r_d.focus structure exists
                    if (!this.currentDecisions.r_d.focus) {
                        this.currentDecisions.r_d.focus = { camera: 0, battery: 0, processor: 0, display: 0, software: 0 };
                    }
                    this.currentDecisions.r_d.focus[field] = value;
                } else if (category === 'operations') { // data-category="operations"
                    this.currentDecisions.operations[field] = value;
                } else if (category === 'corporate') { // data-category="corporate"
                    this.currentDecisions.corporate[field] = value;
                }
                
                console.log(`Updated ${category}.${field} (segment: ${e.target.getAttribute('data-segment') || 'N/A'}) to ${value}`);
                console.log('Current decisions:', JSON.stringify(this.currentDecisions, null, 2)); // For debugging
            });
        });
        
        // Setup tabs with proper identification
        document.querySelectorAll('.nav-link').forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Get the target from data-bs-target attribute
                const targetId = e.target.getAttribute('data-bs-target');
                if (!targetId) return;
                
                const targetPane = document.querySelector(targetId);
                if (!targetPane) return;
                
                // Hide all tab contents
                document.querySelectorAll('.tab-pane').forEach(pane => {
                    pane.classList.remove('show', 'active');
                });
                
                // Show selected tab content
                targetPane.classList.add('show', 'active');
                
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
        
        // Handle potential errors that might occur during UI updates
        try {
            if (this.role === 'admin') {
                this.updateAdminUI();
            } else {
                this.updateTeamUI();
            }
        } catch (error) {
            console.error('Error updating UI:', error);
            this.showError('Error updating the game display. Please reload the page.');
        }
    }
    
    updateAdminUI() {
        try {
            // Safeguard against missing data
            if (!this.gameState) {
                console.error('No game state available for UI update');
                this.showError('Game state unavailable. Please reload the page.');
                return;
            }
            
            // Update admin-specific UI elements
            const teamsBody = document.getElementById('teamsTableBody');
            
            if (!teamsBody) {
                console.error('Teams table body element not found');
                return;
            }
            
            // Clear the table body
            teamsBody.innerHTML = '';
            
            if (!this.gameState.teams) {
                console.error('Missing teams data in game state:', this.gameState);
                const row = document.createElement('tr');
                row.innerHTML = `<td colspan="6" class="text-center">Error loading team data</td>`;
                teamsBody.appendChild(row);
                return;
            }
            
            // Get submission data
            const currentRoundStr = this.currentRound.toString();
            const roundResults = this.gameState.round_results || {};
            const submissions = roundResults[currentRoundStr]?.submissions || [];

            console.log(`Current round: ${this.currentRound}, Round data:`, roundResults[currentRoundStr]);
            console.log(`Submissions:`, submissions);

            // Add team rows
            let allSubmitted = true;
            const teamIds = Object.keys(this.gameState.teams);
            
            for (const teamId of teamIds) {
                const team = this.gameState.teams[teamId];
                if (!team) continue;
                
                const row = document.createElement('tr');
                
                // Check if team has submitted for current round
                const hasSubmitted = submissions.includes(teamId);
                if (!hasSubmitted) {
                    allSubmitted = false;
                }
                
                if (hasSubmitted) {
                    row.classList.add('decision-submitted');
                }
                
                // Handle missing fields with defaults
                const capital = team?.financial?.capital || 0;
                const marketShare = team?.market?.market_share || 0;
                const score = team?.scores?.total || 0;
                
                row.innerHTML = `
                    <td>${teamId}</td>
                    <td>${team?.name || teamId}</td>
                    <td>$${Math.round(capital / 1000000)}M</td>
                    <td>${(marketShare * 100).toFixed(1)}%</td>
                    <td>${score.toFixed(1)}</td>
                    <td>${hasSubmitted ? 
                        '<span class="badge bg-success">Submitted</span>' : 
                        '<span class="badge bg-warning">Pending</span>'}</td>
                `;
                
                teamsBody.appendChild(row);
            }
            
            // Update round control buttons
            const startRoundBtn = document.getElementById('startRoundBtn');
            const forceAdvanceBtn = document.getElementById('forceAdvanceBtn');
            
            if (!startRoundBtn || !forceAdvanceBtn) {
                console.error('Round control buttons not found');
                return;
            }
            
            // Get the container class to set the button styles
            const startRoundContainer = startRoundBtn.parentElement;
            const forceAdvanceContainer = forceAdvanceBtn.parentElement;
            
            if (this.isFinished) {
                startRoundBtn.disabled = true;
                forceAdvanceBtn.disabled = true;
                startRoundBtn.textContent = 'Game Finished';
                forceAdvanceBtn.textContent = 'Game Finished';
                
                if (startRoundContainer) startRoundContainer.classList.add('btn-secondary');
                if (forceAdvanceContainer) forceAdvanceContainer.classList.add('btn-secondary');
            } else {
                console.log(`All submitted: ${allSubmitted}. Teams: ${teamIds.length}, Submissions: ${submissions.length}`);
                
                // Update the Start Round button
                startRoundBtn.disabled = !allSubmitted;
                
                if (allSubmitted) {
                    startRoundBtn.textContent = 'Start Next Round';
                    startRoundBtn.classList.remove('btn-secondary');
                    startRoundBtn.classList.add('btn-success');
                    
                    if (startRoundContainer) {
                        startRoundContainer.classList.remove('bg-secondary');
                        startRoundContainer.classList.add('bg-success');
                    }
                } else {
                    startRoundBtn.textContent = `Waiting for Teams (${submissions.length}/${teamIds.length})`;
                    startRoundBtn.classList.remove('btn-success');
                    startRoundBtn.classList.add('btn-secondary');
                    
                    if (startRoundContainer) {
                        startRoundContainer.classList.remove('bg-success');
                        startRoundContainer.classList.add('bg-secondary');
                    }
                }
                
                // Update the Force Advance button
                forceAdvanceBtn.disabled = false;
                forceAdvanceBtn.textContent = 'Force Advance to Round ' + (this.currentRound + 1);
                
                if (forceAdvanceContainer) {
                    forceAdvanceContainer.classList.add('bg-warning');
                }
            }
            
            // Update round display
            const roundDisplay = document.getElementById('roundDisplay');
            if (roundDisplay) {
                roundDisplay.textContent = `Round ${this.currentRound} of ${this.totalRounds}`;
                roundDisplay.classList.remove('alert-warning', 'alert-danger', 'alert-success');
                
                if (this.isFinished) {
                    roundDisplay.classList.add('alert-success');
                    roundDisplay.textContent += ' (Game Complete)';
                } else if (allSubmitted) {
                    roundDisplay.classList.add('alert-success');
                    roundDisplay.textContent += ' (Ready to Advance)';
                } else {
                    roundDisplay.classList.add('alert-warning');
                    roundDisplay.textContent += ` (${submissions.length}/${teamIds.length} Submitted)`;
                }
            }
            
            // Safely update other UI sections
            try {
                this.updateMarketOverview();
            } catch (error) {
                console.error('Error updating market overview:', error);
            }
            
            try {
                this.updateEventsList();
            } catch (error) {
                console.error('Error updating events list:', error);
            }
            
            try {
                this.updateRankings();
            } catch (error) {
                console.error('Error updating rankings:', error);
            }
        } catch (error) {
            console.error('Error in updateAdminUI:', error);
            this.showError('Error updating the game display. Please reload the page.');
        }
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
        
        // Check if team has already submitted for this round
        const currentRoundStr = this.currentRound.toString();
        const roundResults = this.gameState.round_results || {};
        const submissions = roundResults[currentRoundStr]?.submissions || [];
        this.hasSubmitted = submissions.includes(this.id);
        
        // Update form submission status before updating inputs to prevent data loss
        const submitBtn = document.getElementById('submitDecisionsBtn');
        const decisionForm = document.getElementById('decisionForm');
        
        if (this.hasSubmitted) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Decisions Submitted for Round ' + this.currentRound;
            decisionForm.classList.add('decision-submitted');
            
            // Disable all form inputs when submitted
            decisionForm.querySelectorAll('input').forEach(input => {
                input.disabled = true;
            });
        } else {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Decisions for Round ' + this.currentRound;
            decisionForm.classList.remove('decision-submitted');
            
            // Enable all form inputs when not submitted
            decisionForm.querySelectorAll('input').forEach(input => {
                input.disabled = false;
            });
        }
        
        // Update product segments with current values from state
        // Also, initialize this.currentDecisions with these values if not already set by a more recent interaction.
        for (const [segmentKey, productData] of Object.entries(company.products)) {
            const segmentToggle = document.querySelector(`.segment-toggle[data-segment="${segmentKey}"]`);
            const segmentDetails = document.querySelector(`.segment-details[data-segment="${segmentKey}"]`);
            
            if (segmentToggle && segmentDetails) {
                segmentToggle.checked = productData.active;
                segmentDetails.style.display = productData.active ? 'block' : 'none';

                // Populate form fields and this.currentDecisions.products[segmentKey]
                // This ensures that if currentDecisions was just initialized with zeros, it gets actual values.
                // If currentDecisions already has values (e.g. from user input), this won't overwrite them unless hasSubmitted is false.
                // The event listeners in setupTeamUI handle updating currentDecisions on user input.
                // This block primarily ensures the form VISUALLY reflects the gameState.
                
                // Product fields
                document.querySelector(`input[data-category="product"][data-segment="${segmentKey}"][data-field="price"]`).value = productData.price;
                document.querySelector(`input[data-category="product"][data-segment="${segmentKey}"][data-field="quality"]`).value = productData.quality;
                document.querySelector(`input[data-category="product"][data-segment="${segmentKey}"][data-field="features"]`).value = productData.features;
                document.querySelector(`input[data-category="product"][data-segment="${segmentKey}"][data-field="production_volume"]`).value = productData.production_volume;
                document.querySelector(`input[data-category="product"][data-segment="${segmentKey}"][data-field="marketing_budget"]`).value = productData.marketing_budget; // Full value

                // Initialize/update currentDecisions for products if not already done or if not submitted
                // This logic should be careful not to overwrite fresh user input.
                // The primary update of currentDecisions happens in the event listeners.
                // Here, we're aligning the initial state of currentDecisions if it's still default.
                if (!this.hasSubmitted) { // Only populate if decisions are not final
                    this.currentDecisions.products[segmentKey] = {
                        active: productData.active,
                        price: parseFloat(productData.price),
                        quality: parseFloat(productData.quality),
                        features: parseFloat(productData.features),
                        production_volume: parseFloat(productData.production_volume),
                        marketing_budget: parseFloat(productData.marketing_budget)
                    };
                }
            }
        }

        // Populate R&D, Operations, Corporate strategy fields
        // These values should come from the company's current state (end of last round or initial)
        // or from decisions_history if a decision for the current round was already made.
        // For simplicity, we'll assume `company` object reflects the state to populate from.
        // A more sophisticated approach would check `decisions_history[this.currentRound]`.

        if (!this.hasSubmitted) { // Only populate if decisions are not final
            // R&D
            if (company.r_d) { // Assuming r_d structure exists in company state
                document.getElementById('rdBudget').value = company.r_d.budget || 0;
                this.currentDecisions.r_d.budget = parseFloat(company.r_d.budget || 0);
                if (company.r_d.focus) {
                    for (const [focusArea, value] of Object.entries(company.r_d.focus)) {
                        const inputEl = document.getElementById(`rdFocus${focusArea.charAt(0).toUpperCase() + focusArea.slice(1)}`);
                        if (inputEl) inputEl.value = value;
                        this.currentDecisions.r_d.focus[focusArea] = parseFloat(value || 0);
                    }
                }
            } else { // Default if not in company state (e.g. first round)
                 document.getElementById('rdBudget').value = this.currentDecisions.r_d.budget; // Use initialized default
                 for (const [focusArea, value] of Object.entries(this.currentDecisions.r_d.focus)) {
                        const inputEl = document.getElementById(`rdFocus${focusArea.charAt(0).toUpperCase() + focusArea.slice(1)}`);
                        if (inputEl) inputEl.value = value; // Use initialized default
                 }
            }

            // Operations
            if (company.operations) {
                document.getElementById('opsCapacityInvestment').value = company.operations.capacity_investment || 0;
                document.getElementById('opsQualityInvestment').value = company.operations.quality_investment || 0;
                this.currentDecisions.operations.capacity_investment = parseFloat(company.operations.capacity_investment || 0);
                this.currentDecisions.operations.quality_investment = parseFloat(company.operations.quality_investment || 0);
            } else {
                document.getElementById('opsCapacityInvestment').value = this.currentDecisions.operations.capacity_investment;
                document.getElementById('opsQualityInvestment').value = this.currentDecisions.operations.quality_investment;
            }

            // Corporate Strategy
            if (company.corporate) {
                document.getElementById('corpBrandInvestment').value = company.corporate.brand_investment || 0;
                document.getElementById('corpSustainabilityInvestment').value = company.corporate.sustainability_investment || 0;
                document.getElementById('corpCsrInvestment').value = company.corporate.csr_investment || 0;
                document.getElementById('corpEmployeeInvestment').value = company.corporate.employee_investment || 0;

                this.currentDecisions.corporate.brand_investment = parseFloat(company.corporate.brand_investment || 0);
                this.currentDecisions.corporate.sustainability_investment = parseFloat(company.corporate.sustainability_investment || 0);
                this.currentDecisions.corporate.csr_investment = parseFloat(company.corporate.csr_investment || 0);
                this.currentDecisions.corporate.employee_investment = parseFloat(company.corporate.employee_investment || 0);
            } else {
                 document.getElementById('corpBrandInvestment').value = this.currentDecisions.corporate.brand_investment;
                 document.getElementById('corpSustainabilityInvestment').value = this.currentDecisions.corporate.sustainability_investment;
                 document.getElementById('corpCsrInvestment').value = this.currentDecisions.corporate.csr_investment;
                 document.getElementById('corpEmployeeInvestment').value = this.currentDecisions.corporate.employee_investment;
            }
        } else {
            // If submitted, populate form from company.decisions_history[this.currentRound] if available
            // This ensures that after submission, the form shows the submitted values, not editable ones.
            // This logic requires that `decisions_history` has the same structure as `currentDecisions`.
            const submittedDecisions = company.decisions_history ? company.decisions_history[this.currentRound.toString()] : null;
            if (submittedDecisions) {
                 // Products (already handled by the loop above and input disabling)
                 // R&D
                 document.getElementById('rdBudget').value = submittedDecisions.r_d.budget;
                 for (const [focusArea, value] of Object.entries(submittedDecisions.r_d.focus)) {
                    const inputEl = document.getElementById(`rdFocus${focusArea.charAt(0).toUpperCase() + focusArea.slice(1)}`);
                    if (inputEl) inputEl.value = value;
                 }
                 // Operations
                 document.getElementById('opsCapacityInvestment').value = submittedDecisions.operations.capacity_investment;
                 document.getElementById('opsQualityInvestment').value = submittedDecisions.operations.quality_investment;
                 // Corporate
                 document.getElementById('corpBrandInvestment').value = submittedDecisions.corporate.brand_investment;
                 document.getElementById('corpSustainabilityInvestment').value = submittedDecisions.corporate.sustainability_investment;
                 document.getElementById('corpCsrInvestment').value = submittedDecisions.corporate.csr_investment;
                 document.getElementById('corpEmployeeInvestment').value = submittedDecisions.corporate.employee_investment;
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
            console.log(`Starting new round for game ${this.gameId}`);
            
            const response = await fetch(`/api/admin/advance_round/${this.gameId}?admin_code=${this.accessCode}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ force: false }),
            });
            
            console.log('Response status:', response.status);
            
            const responseText = await response.text();
            console.log('Response text:', responseText);
            
            let result;
            try {
                result = JSON.parse(responseText);
            } catch (e) {
                throw new Error(`Invalid JSON response: ${responseText}`);
            }
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}, Message: ${result.error || 'Unknown error'}`);
            }
            
            if (result.success) {
                // Show success message
                this.showSuccess(`Advanced to round ${result.round || result.current_round || 'next'}`);
                
                // Refresh game state
                await this.fetchGameState();
            } else {
                throw new Error(result.error || 'Unknown error');
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
        
        if (!confirm(`Are you sure you want to force advance to round ${this.currentRound + 1}? Any teams that have not submitted decisions will miss their turn.`)) {
            return;
        }
        
        // Show loading indicator
        this.showLoading();
        
        try {
            console.log(`Forcing advance to next round for game ${this.gameId}`);
            
            const response = await fetch(`/api/admin/advance_round/${this.gameId}?admin_code=${this.accessCode}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ force: true }),
            });
            
            console.log('Response status:', response.status);
            
            const responseText = await response.text();
            console.log('Response text:', responseText);
            
            let result;
            try {
                result = JSON.parse(responseText);
            } catch (e) {
                throw new Error(`Invalid JSON response: ${responseText}`);
            }
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}, Message: ${result.error || 'Unknown error'}`);
            }
            
            if (result.success) {
                // Show success message
                this.showSuccess(`Forced advance to round ${result.round || result.current_round || 'next'}`);
                
                // Refresh game state
                await this.fetchGameState();
            } else {
                throw new Error(result.error || 'Unknown error');
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
