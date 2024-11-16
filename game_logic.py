import os
import time
import random
import keyboard

BOARD_WIDTH = 10
BOARD_HEIGHT = 10

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

# Render game board
def render_board(player, obstacles, missiles, score, lives, fuel):
    board = [[" " for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

    # Set player
    board[player["y"]][player["x"]] = "P"

    # Set obstacles
    for obs in obstacles:
        if 0 <= obs["y"] < BOARD_HEIGHT:
            board[obs["y"]][obs["x"]] = "O"

    # Set missiles
    for missile in missiles:
        if 0 <= missile["y"] < BOARD_HEIGHT:
            board[missile["y"]][missile["x"]] = "|"

    clear_screen()
    for row in board:
        print("".join(row))
    print(f"Score: {score} | Lives: {lives} | Fuel: {fuel}")

def main():
    # Game variables
    player = {"x": BOARD_WIDTH // 2, "y": BOARD_HEIGHT - 1}
    obstacles = []
    missiles = []
    score = 0
    lives = 3
    fuel = 100
    tick_rate = 0.2
    game_running = True

    clear_screen()
    print("Welcome to River Raid!")
    print("\nControls:")
    print("- Left Arrow: Move Left")
    print("- Right Arrow: Move Right")
    print("- Spacebar: Shoot")
    print("- Q: Quit")
    print("\nPress any key to start!")
    keyboard.wait("space")

    while game_running:
        # Handle input
        if keyboard.is_pressed("left") and player["x"] > 0:
            player["x"] -= 1
        if keyboard.is_pressed("right") and player["x"] < BOARD_WIDTH - 1:
            player["x"] += 1
        if keyboard.is_pressed("space"):
            if not missiles or missiles[-1]["y"] < player["y"] - 2:  # Prevent spam
                missiles.append({"x": player["x"], "y": player["y"] - 1})
        if keyboard.is_pressed("q"):
            print("\nYou quit the game.")
            break

        # Add obstacles
        if random.random() < 0.2:  # Adjust frequency
            obstacles.append({"x": random.randint(0, BOARD_WIDTH - 1), "y": 0})

        # Move obstacles
        for obs in obstacles:
            obs["y"] += 1

        # Move missiles
        for missile in missiles:
            missile["y"] -= 1

        # Check collisions
        for obs in obstacles:
            if obs["x"] == player["x"] and obs["y"] == player["y"]:
                lives -= 1
                obstacles.remove(obs)
                print("\nYou crashed!")
                time.sleep(1)
                if lives == 0:
                    game_running = False
                break

        # Handle hits
        for missile in missiles:
            for obs in obstacles:
                if missile["x"] == obs["x"] and missile["y"] == obs["y"]:
                    score += 10
                    obstacles.remove(obs)
                    missiles.remove(missile)
                    break

        # Remove objects
        obstacles = [obs for obs in obstacles if obs["y"] < BOARD_HEIGHT]
        missiles = [missile for missile in missiles if missile["y"] >= 0]

        # Decrease fuel
        fuel -= 1
        if fuel <= 0:
            lives -= 1
            fuel = 100
            print("\nOut of fuel!")
            time.sleep(1)
            if lives == 0:
                game_running = False

        # Score
        score += 1

        render_board(player, obstacles, missiles, score, lives, fuel)

        # Check for game over
        if lives <= 0:
            print("\nGame Over!")
            print(f"Final Score: {score}")
            break

        # Add delay
        time.sleep(tick_rate)

if __name__ == "__main__":
    main()
