# shared/network_utils.py
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - [network_utils] - %(message)s')

def serialize_message(message):
    try:
        serialized_message = json.dumps(message)
        # logging.info(f"[network_utils] Serialized message: {serialized_message}")
        return serialized_message
    except (TypeError, ValueError) as e:
        logging.error(f"[network_utils] Serialization error: {e}")
        return None

def deserialize_message(message_json):
    try:
        deserialized_message = json.loads(message_json)
        # logging.info(f"[network_utils] Deserialized message: {deserialized_message}")
        return deserialized_message
    except (json.JSONDecodeError, TypeError) as e:
        logging.error(f"[network_utils] Deserialization error: {e}, message_json: {message_json}")
        return None
