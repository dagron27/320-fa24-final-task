import threading
import queue
import time
from game.game_state import GameState
from game.game_loops import GameLoops

class GameManager:
    def __init__(self):
        # Initialize shared state and control flags
        self.shared_state = GameState()
        self.running = True
        self.game_running = False  # Separate flag for game state
        self.input_queue = queue.Queue()

        # Create and configure threads
        self._setup_threads()

    def _setup_threads(self):
        """Initialize all game threads except input thread"""
        self.game_loops = GameLoops(self.shared_state)
        self.enemy_thread = threading.Thread(target=self.game_loops.enemy_loop, args=(self._is_game_running,))
        self.collision_thread = threading.Thread(target=self.game_loops.collision_loop, args=(self._is_game_running,))
        self.state_thread = threading.Thread(target=self.game_loops.state_loop, args=(self._is_game_running,))
        self.input_thread = threading.Thread(target=self._input_loop)

        # Make threads daemon so they exit when main program exits
        self.enemy_thread.daemon = True
        self.collision_thread.daemon = True
        self.state_thread.daemon = True
        self.input_thread.daemon = True

    def start(self):
        """Start all game threads and main game loop"""
        if not self.running:
            self.running = True
            self.input_thread.start()  # Start input thread
            self.start_game_threads()

    def stop(self):
        # """Clean shutdown of game manager"""
        # print("Stopping game manager...")
        # self.running = False
        # self.game_running = False
        
        # # Stop game threads
        # self.stop_game_threads()
        
        # # Cleanup any resources
        # self.shared_state.reset()
        print("Stopped")

    def start_game_threads(self):
        """Start game threads and main game loop"""
        if not self.game_running:
            self.game_running = True
            self.enemy_thread.start()
            self.collision_thread.start()
            self.state_thread.start()
            
            # Start the main game loop thread
            self.game_loop_thread = threading.Thread(target=self.game_loop)
            self.game_loop_thread.daemon = True
            self.game_loop_thread.start()

    def stop_game_threads(self):
        """Stop game threads but keep input loop running"""
        self.game_running = False
        if self.enemy_thread.is_alive():
            self.enemy_thread.join()
        if self.collision_thread.is_alive():
            self.collision_thread.join()
        if self.state_thread.is_alive():
            self.state_thread.join()
        #if self.game_loop_thread.is_alive():
            #self.game_loop_thread.join()

    def _input_loop(self):
        """Main input processing loop"""
        while self.running:
            try:
                message = self.input_queue.get(timeout=0.1)
                with self.shared_state.state_lock:
                    if message["action"] == "reset_game":
                        self.reset_game()
                    elif self.shared_state.game_state == GameState.STATE_RUNNING:
                        if message["action"] == "move":
                            self.shared_state.player.move(message["direction"])
                        elif message["action"] == "shoot":
                            missile = self.shared_state.player.shoot()
                            self.shared_state.add_missile(missile)
            except queue.Empty:
                continue

    def process_message(self, message):
        """Process incoming messages from client"""
        if message == {'action': 'reset_game'}:
            self.reset_game()
        else:
            self.input_queue.put(message)
        return {"status": "ok", "game_state": self.shared_state.get_state()}

    def _running(self):
        """Getter to determine if the game is still running"""
        return self.running

    def _is_game_running(self):
        """Determine if the game threads should keep running"""
        return self.game_running

    def game_loop(self):
        """Main game loop that coordinates game state and timing"""
        TICK_RATE = 60  # Target FPS
        TICK_TIME = 1.0 / TICK_RATE
        
        while self.game_running:
            start_time = time.time()
            
            with self.shared_state.state_lock:
                # Check if the game is over
                if self.shared_state.game_state == GameState.STATE_GAME_OVER:
                    self.stop_game_threads()
                    break

            # Control tick rate
            end_time = time.time()
            elapsed_time = end_time - start_time
            sleep_time = max(0, TICK_TIME - elapsed_time)
            if(sleep_time):
                time.sleep(sleep_time)

    def reset_game(self):
        """Reset the game state and restart threads"""
        self.stop_game_threads()
        self.shared_state.reset()
        self._setup_threads()  # Reinitialize game threads
        self.start_game_threads()  # Restart game threads
