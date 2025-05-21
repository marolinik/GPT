/**
 * Charts and Visualizations for StrategyMasters
 * Handles creation and updating of charts for game data visualization
 */

class GameCharts {
    constructor(gameEngine) {
        this.gameEngine = gameEngine;
        this.charts = {};
        
        // Initialize charts if we're on the right page
        this.initCharts();
    }
    
    initCharts() {
        // Market share chart (admin view)
        const marketShareCanvas = document.getElementById('marketShareChart');
        if (marketShareCanvas) {
            this.charts.marketShare = new Chart(marketShareCanvas, {
                type: 'pie',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.7)',
                            'rgba(54, 162, 235, 0.7)',
                            'rgba(255, 206, 86, 0.7)',
                            'rgba(75, 192, 192, 0.7)',
                            'rgba(153, 102, 255, 0.7)'
                        ],
                        borderColor: [
                            'rgba(255, 99, 132, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                        },
                        title: {
                            display: true,
                            text: 'Distribucija tržišnog udela'
                        }
                    }
                }
            });
        }
        
        // Score chart (admin view)
        const scoreCanvas = document.getElementById('scoreChart');
        if (scoreCanvas) {
            this.charts.score = new Chart(scoreCanvas, {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'Finansijski',
                            backgroundColor: 'rgba(255, 99, 132, 0.7)',
                            data: []
                        },
                        {
                            label: 'Tržište',
                            backgroundColor: 'rgba(54, 162, 235, 0.7)',
                            data: []
                        },
                        {
                            label: 'Inovacije',
                            backgroundColor: 'rgba(255, 206, 86, 0.7)',
                            data: []
                        },
                        {
                            label: 'Održivost',
                            backgroundColor: 'rgba(75, 192, 192, 0.7)',
                            data: []
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Učinak tima po kategorijama'
                        },
                        legend: {
                            position: 'top',
                        },
                    },
                    scales: {
                        x: {
                            stacked: false,
                        },
                        y: {
                            stacked: false,
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }
    }
    
    updateCharts() {
        if (!this.gameEngine || !this.gameEngine.gameState) {
            return;
        }
        
        // Update market share chart
        if (this.charts.marketShare && this.gameEngine.role === 'admin') {
            const labels = [];
            const data = [];
            
            for (const [teamId, team] of Object.entries(this.gameEngine.gameState.teams)) {
                labels.push(team.name);
                data.push(team.market.market_share * 100);
            }
            
            this.charts.marketShare.data.labels = labels;
            this.charts.marketShare.data.datasets[0].data = data;
            this.charts.marketShare.update();
        }
        
        // Update score chart
        if (this.charts.score && this.gameEngine.role === 'admin') {
            const labels = [];
            const financialData = [];
            const marketData = [];
            const innovationData = [];
            const sustainabilityData = [];
            
            for (const [teamId, team] of Object.entries(this.gameEngine.gameState.teams)) {
                labels.push(team.name);
                financialData.push(team.scores.financial);
                marketData.push(team.scores.market);
                innovationData.push(team.scores.innovation);
                sustainabilityData.push(team.scores.sustainability);
            }
            
            this.charts.score.data.labels = labels;
            this.charts.score.data.datasets[0].data = financialData;
            this.charts.score.data.datasets[1].data = marketData;
            this.charts.score.data.datasets[2].data = innovationData;
            this.charts.score.data.datasets[3].data = sustainabilityData;
            this.charts.score.update();
        }
    }
}

// Initialize charts when game engine is ready
document.addEventListener('DOMContentLoaded', function() {
    // Wait for game engine to be initialized
    const checkGameEngine = setInterval(() => {
        if (window.gameEngine) {
            window.gameCharts = new GameCharts(window.gameEngine);
            
            // Update charts when game state changes
            const originalUpdateUI = window.gameEngine.updateUI;
            window.gameEngine.updateUI = function() {
                originalUpdateUI.call(window.gameEngine);
                if (window.gameCharts) {
                    window.gameCharts.updateCharts();
                }
            };
            
            clearInterval(checkGameEngine);
        }
    }, 100);
});
