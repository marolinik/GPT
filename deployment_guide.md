# StrategyMasters: The Smartphone Industry Challenge - Deployment Guide

This document provides instructions for deploying and running the StrategyMasters simulation game.

## Local Development Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the test suite**:
   ```bash
   python -m unittest discover -s src
   ```
   Ensure all tests pass before running the application.

4. **Run the application locally**:
   ```bash
   python src/main.py
   ```
   The application will be available at http://localhost:5000

## Production Deployment Options

### Option 1: Deploy to a Cloud Platform

The application is designed to work with various cloud platforms that support Python/Flask applications:

1. **Heroku**:
   - Install the Heroku CLI
   - Login to Heroku: `heroku login`
   - Create a new app: `heroku create`
   - Deploy: `git push heroku main`

2. **Google Cloud Run**:
   - Build a container: `gcloud builds submit --tag gcr.io/PROJECT_ID/strategymaster`
   - Deploy: `gcloud run deploy --image gcr.io/PROJECT_ID/strategymaster --platform managed`

3. **AWS Elastic Beanstalk**:
   - Install the EB CLI
   - Initialize: `eb init`
   - Create environment: `eb create`
   - Deploy: `eb deploy`

### Option 2: Deploy with Docker

1. **Build the Docker image**:
   ```bash
   docker build -t strategymaster .
   ```

2. **Run the container**:
   ```bash
   docker run -p 5000:5000 strategymaster
   ```

## Troubleshooting Common Issues

### Game State Persistence Issues

The application uses a file-based persistence system that simulates Redis functionality. If you encounter issues with game state persistence:

1. Ensure the application has write permissions to the `/tmp/strategy_masters_data` directory
2. For production, consider modifying the `redis_persistence.py` file to use an actual Redis instance or another database

### Team Not Found Errors

If users encounter "Team not found" errors:

1. Check that the game ID and team code are correct
2. Verify that the persistence layer is working correctly
3. Check server logs for any errors related to game state loading

### Deployment Failures

If deployment fails:

1. Check that all dependencies are correctly specified in requirements.txt
2. Ensure the application is configured to listen on the port provided by the environment (PORT environment variable)
3. Verify that the hosting platform supports the file-based persistence approach or modify to use a cloud-compatible database

## Architecture Overview

The application consists of several key components:

1. **Flask Web Application** (`main.py`): Handles HTTP requests and serves web pages
2. **Game State Model** (`models/game_state.py`): Manages the core game logic and state
3. **Persistence Layer** (`models/redis_persistence.py`): Provides reliable state storage
4. **Company Model** (`models/company.py`): Represents team companies in the simulation
5. **Market Model** (`models/market.py`): Simulates the smartphone market
6. **Events Model** (`models/events.py`): Generates strategic events during gameplay

## Customization

To customize the simulation:

1. Modify market parameters in `models/market.py`
2. Adjust scoring weights in the `calculate_score` method in `models/company.py`
3. Add or modify strategic events in `models/events.py`
4. Change the UI appearance by editing the templates and CSS files

## Support

For additional support or questions, please contact the developer.
