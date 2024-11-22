# client/game/game_state_updater.py
import threading
import queue
import time

class GameStateUpdater(threading.Thread):
    def __init__(self, game_logic, client):
        threading.Thread.__init__(self)
        self.game_logic = game_logic
        self.client = client
        self.running = True
        self.update_queue = queue.Queue()
        self.daemon = True  # Allow thread to exit when main program exits

    def run(self):
        while self.running:
            try:
                self.client.send_message({"action": "get_game_state"})
                #print("message sent")
                response = self.client.receive_message()
                #print(f"message received: {response['game_state']}")
                if response.get('status') == 'ok':
                    self.update_queue.put(response['game_state'])
            except Exception as e:
                print(f"Game state update error: {e}")
                time.sleep(1)  # Prevent rapid error retries
            time.sleep(0.1)  # Adjust update frequency

    def stop(self):
        self.running = False