import threading
import queue
import time

class GameState:
    def __init__(self, client):
        self.client = client
        self.update_queue = queue.Queue(maxsize=2)
        self.message_queue = queue.Queue(maxsize=10)
        self.running = True
        self.last_update = time.time()
        self.update_interval = 0.05
        self.lock = threading.Lock()  # Add a lock for shared state
        
        self._start_threads()

    def _start_threads(self):
        self.message_thread = threading.Thread(target=self._message_handler)
        self.message_thread.daemon = True
        self.message_thread.start()
        
        self.update_thread = threading.Thread(target=self._state_updater)
        self.update_thread.daemon = True
        self.update_thread.start()

    def _message_handler(self):
        while self._is_running():
            try:
                message = self.message_queue.get_nowait()
                print(message)
                self.client.send_message(message)
                response = self.client.receive_message()
                
                if response.get('status') == 'ok' and 'game_state' in response:
                    self._update_queue_put(response['game_state'])
            except queue.Empty:
                time.sleep(0.01)
            except Exception as e:
                print(f"Message handling error: {e}")
                time.sleep(0.1)

    def _state_updater(self):
        while self._is_running():
            try:
                current_time = time.time()
                if current_time - self._get_last_update() >= self.update_interval:
                    self.client.send_message({"action": "get_game_state"})
                    response = self.client.receive_message()
                    
                    if response.get('status') == 'ok':
                        self._update_queue_put(response['game_state'])
                        self._set_last_update(current_time)
            except Exception as e:
                print(f"State update error: {e}")
                time.sleep(0.1)
            time.sleep(0.01)

    def _update_queue_put(self, state):
        try:
            if self.update_queue.full():
                try:
                    self.update_queue.get_nowait()
                except queue.Empty:
                    pass
            self.update_queue.put_nowait(state)
        except queue.Full:
            pass

    def send_action(self, action_data):
        try:
            if not self.message_queue.full():
                self.message_queue.put_nowait(action_data)
        except queue.Full:
            pass

    def get_state_updates(self):
        updates = []
        try:
            while True:
                updates.append(self.update_queue.get_nowait())
        except queue.Empty:
            pass
        return updates

    def stop(self):
        with self.lock:
            self.running = False
        try:
            self.send_action({"action": "quit_game"})
            time.sleep(0.1)
        except:
            pass

    def _is_running(self):
        with self.lock:
            return self.running

    def _get_last_update(self):
        with self.lock:
            return self.last_update

    def _set_last_update(self, current_time):
        with self.lock:
            self.last_update = current_time
