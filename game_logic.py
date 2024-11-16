import os
import time
import random
import keyboard

BOARD_WIDTH = 10
BOARD_HEIGHT = 10

# Render game board
def render_board(player, obstacles, missiles, fuel_depots, score, lives, fuel):
    board = [[" " for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

    # Place player
    board[player["y"]][player["x"]] = "P"

    # Place obstacles
    for obs in obstacles:
        if 0 <= obs["y"] < BOARD_HEIGHT:
            board[obs["y"]][obs["x"]] = "O"

    # Place fuel depots
    for depot in fuel_depots:
        if 0 <= depot["y"] < BOARD_HEIGHT:
            board[depot["y"]][depot["x"]] = "F"

    # Place missiles
    for missile in missiles:
        if 0 <= missile["y"] < BOARD_HEIGHT:
            board[missile["y"]][missile["x"]] = "|"

    # Render entire board as string
    board_output = "\n".join("".join(row) for row in board)
    stats = f"Score: {score} | Lives: {lives} | Fuel: {fuel}\n"
    return stats + board_output

def main():
    player = {"x": BOARD_WIDTH // 2, "y": BOARD_HEIGHT - 1}
    obstacles = []
    missiles = []
    fuel_depots = []
    score = 0
    lives = 3
    fuel = 100
    tick_rate = 0.2
    game_running = True

    # Instructions
    os.system("cls" if os.name == "nt" else "clear")
    print("Welcome to River Raid!")
    print("\nControls:")
    print("- Left Arrow: Move Left")
    print("- Right Arrow: Move Right")
    print("- Spacebar: Shoot")
    print("- Q: Quit")
    print("\nPress Enter to start!")
    input()

    while game_running:
        # Handle input
        if keyboard.is_pressed("left") and player["x"] > 0:
            player["x"] -= 1
        if keyboard.is_pressed("right") and player["x"] < BOARD_WIDTH - 1:
            player["x"] += 1
        if keyboard.is_pressed("space"):
            if not missiles or missiles[-1]["y"] < player["y"] - 2:
                missiles.append({"x": player["x"], "y": player["y"] - 1})
        if keyboard.is_pressed("q"):
            print("\nYou quit the game.")
            break

        # Add new obstacles
        if random.random() < 0.2:
            obstacles.append({"x": random.randint(0, BOARD_WIDTH - 1), "y": 0})

        # Add new fuel depots
        if random.random() < 0.05:
            fuel_depots.append({"x": random.randint(0, BOARD_WIDTH - 1), "y": 0})

        # Move obstacles
        for obs in obstacles:
            obs["y"] += 1

        # Move fuel
        for depot in fuel_depots:
            depot["y"] += 1

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

        # Handle fuel collection
        for depot in fuel_depots:
            if depot["x"] == player["x"] and depot["y"] == player["y"]:
                fuel = min(100, fuel + 50)
                fuel_depots.remove(depot)

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
        fuel_depots = [depot for depot in fuel_depots if depot["y"] < BOARD_HEIGHT]

        # Decrease fuel
        fuel -= 1
        if fuel <= 0:
            lives -= 1
            fuel = 100
            print("\nOut of fuel!")
            time.sleep(1)
            if lives == 0:
                game_running = False

        score += 1

        # Render the game
        board_output = render_board(player, obstacles, missiles, fuel_depots, score, lives, fuel)
        os.system("cls" if os.name == "nt" else "clear")
        print(board_output)

        if lives <= 0:
            print("\nGame Over!")
            print(f"Final Score: {score}")
            break

        # Add delay
        time.sleep(tick_rate)

if __name__ == "__main__":
    main()
