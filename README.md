# 320-fa24-final-task
This is the final task project for my Intro to operating system classes

How to Play:
Move Left/Right: Use the arrow keys to move.
Shoot: Press Spacebar to fire missiles.
Quit: Press Q to exit the game.

Game Features:
Obstacles: Avoid randomly spawning obstacles to stay alive.
Fuel Management: Your fuel decreases over time.
Score System: Gain points for surviving and hitting obstacles.
Lives: Start with 3 lives. Collisions or running out of fuel will cost you a life.

Requirements
keyboard library

# Client Application

This repository contains the client-side code for the game.

## Setup
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run the application: `python app/main.py`.

## Structure
- **app/**: Main application logic.
- **gui/**: Handles the graphical user interface.
- **entities.py**: Game entities like Player, Obstacle, etc.
- **game_logic.py**: Core game logic.
- **utils.py**: Utility functions and helpers.