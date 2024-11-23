import threading
import queue
from game_state import GameState
from game_loops import GameLoops

class GameManager:
    def __init__(self):
        # Initialize shared state and control flags
        self.shared_state = GameState()
        self.running = True
        self.input_queue = queue.Queue()
        
        # Create and configure threads
        self._setup_threads()
        
    def _setup_threads(self):
        """Initialize all game threads"""
        self.game_loops = GameLoops(self.shared_state)
        self.enemy_thread = threading.Thread(target=self.game_loops.enemy_loop, args=(self._running,))
        self.collision_thread = threading.Thread(target=self.game_loops.collision_loop, args=(self._running,))
        self.state_thread = threading.Thread(target=self.game_loops.state_loop, args=(self._running,))
        self.input_thread = threading.Thread(target=self._input_loop)
        
        # Make threads daemon so they exit when main program exits
        self.enemy_thread.daemon = True
        self.collision_thread.daemon = True
        self.state_thread.daemon = True
        self.input_thread.daemon = True

    def start(self):
        """Start all game threads"""
        self.enemy_thread.start()
        self.collision_thread.start()
        self.state_thread.start()
        self.input_thread.start()

    def stop(self):
        """Stop all game threads"""
        self.running = False

    def _input_loop(self):
        """Main input processing loop"""
        while self.running:
            try:
                message = self.input_queue.get(timeout=0.1)
                with self.shared_state.state_lock:
                    if message["action"] == "move":
                        self.shared_state.player.move(message["direction"])
                    elif message["action"] == "shoot":
                        missile = self.shared_state.player.shoot()
                        self.shared_state.add_missile(missile)
                    elif message["action"] == "reset_game":
                        self.shared_state.reset()
            except queue.Empty:
                continue

    def process_message(self, message):
        """Process incoming messages from client"""
        self.input_queue.put(message)
        return {"status": "ok", "game_state": self.shared_state.get_state()}

    def _running(self):
        """Getter to determine if the game is still running"""
        return self.running