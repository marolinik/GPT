# StrategyMasters: The Smartphone Industry Challenge
## User Guide for MBA Lectures

### Overview

StrategyMasters: The Smartphone Industry Challenge is a multiplayer business strategy simulation designed specifically for MBA lectures. This simulation allows students to apply strategic management concepts in a realistic competitive environment, making decisions as executives of smartphone manufacturing companies.

The simulation supports up to 5 competing teams and runs for 10 rounds, with each round representing a business quarter. The entire simulation is designed to be completed within a 1.5-hour lecture session.

### Key Features

- **Realistic Industry Simulation**: Based on the smartphone industry with authentic market dynamics
- **Strategic Framework Application**: Incorporates Porter's Five Forces, Generic Strategies, Resource-Based View, and Balanced Scorecard
- **Multiplayer Competition**: Teams compete directly in the same market
- **Dynamic Market Conditions**: Market segments evolve and strategic events occur throughout gameplay
- **Comprehensive Performance Metrics**: Teams are evaluated across financial, market, innovation, and sustainability dimensions

### Setup Instructions

1. **Installation**:
   - Ensure you have Python 3.8+ installed
   - Install required packages: `pip install flask`
   - Navigate to the application directory: `cd strategy_game/app`
   - Start the server: `python main.py`
   - Access the application at: `http://localhost:5000`

2. **Game Creation (Facilitator)**:
   - Click "Create New Game" on the landing page
   - Select the number of teams (2-5) and rounds (default: 10)
   - Save the generated Game ID, Admin Code, and Team Codes
   - Share the appropriate Team Codes with each participating group

3. **Team Participation**:
   - Teams join using the Game ID and their assigned Team Code
   - Each team manages their own smartphone manufacturing company
   - Teams make strategic decisions each round through their dashboard

### Facilitator Guide

#### Before the Session
- Test the application on your lecture room computer
- Prepare a brief introduction to the smartphone industry and strategic concepts
- Consider dividing students into teams of 3-5 members each

#### During the Session
1. **Introduction (10 minutes)**:
   - Explain the simulation objectives and basic mechanics
   - Introduce the smartphone industry context
   - Review key strategic frameworks students should apply

2. **Game Setup (5 minutes)**:
   - Create a new game and distribute team codes
   - Have teams join the simulation

3. **Gameplay (60-75 minutes)**:
   - Allow 5-7 minutes per round for team decisions
   - Use the admin dashboard to monitor team submissions
   - Advance rounds when all teams have submitted (or use force advance if necessary)
   - Provide strategic guidance as needed, but avoid direct advice

4. **Debrief (15-20 minutes)**:
   - Review final results and rankings
   - Discuss strategic approaches used by different teams
   - Connect simulation outcomes to course concepts
   - Use the reflection questions provided on the results page

#### Admin Controls
- **Start Next Round**: Advances to the next round when all teams have submitted decisions
- **Force Advance Round**: Moves to the next round even if some teams haven't submitted
- **Teams Tab**: Shows team status and submission status
- **Market Overview**: Displays current market conditions and trends
- **Events Tab**: Shows strategic events affecting the current round
- **Rankings Tab**: Displays current team rankings and performance metrics

### Team Guide

#### Decision Categories

1. **Product Portfolio**:
   - **Segments**: Premium, Mid-Range, Budget
   - **Decisions**: Price, Quality, Features, Production Volume, Marketing Budget

2. **Research & Development**:
   - R&D Budget
   - Focus Area (Camera, Battery, Processor, Display, Software)

3. **Operations**:
   - Production Capacity Investment
   - Quality Control Investment
   - Supplier Quality

4. **Corporate Strategy**:
   - Sustainability Investment
   - CSR Investment
   - Employee Programs
   - Brand Building

#### Strategic Considerations

- **Market Segmentation**: Different segments have different price sensitivities and preferences
- **Resource Allocation**: Balance investments across different areas
- **Competitive Positioning**: Differentiate from competitors or compete on cost
- **Long-term vs. Short-term**: Balance immediate profits with capability building
- **Adaptation**: Respond to market trends and strategic events

### Learning Objectives

This simulation helps students develop and apply the following strategic management skills:

1. **Strategic Analysis**: Using frameworks to analyze industry and competitive dynamics
2. **Strategic Positioning**: Developing clear positioning in a competitive market
3. **Resource Allocation**: Making trade-offs in resource deployment
4. **Adaptation**: Responding to changing market conditions and events
5. **Performance Evaluation**: Using balanced metrics to assess business success

### Troubleshooting

- **Connection Issues**: Ensure all teams are on the same network
- **Team Can't Join**: Verify the Game ID and Team Code are correct
- **Decision Submission Fails**: Check that all required fields have valid values
- **Round Won't Advance**: Use the Force Advance feature if a team is unresponsive

For additional support or questions, please contact the simulation developer.
