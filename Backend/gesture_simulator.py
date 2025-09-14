"""
Gesture Data Simulator for testing the Flask WebSocket server
This script simulates gesture data that would come from the Lens Studio app
"""

import socketio
import time
import random
import json
from datetime import datetime

# Create a Socket.IO client
sio = socketio.Client()

@sio.event
def connect():
    print("✅ Connected to Flask server!")
    print("Starting gesture data simulation...")

@sio.event
def disconnect():
    print("❌ Disconnected from Flask server")

@sio.event
def response(data):
    print(f"Server response: {data}")

def generate_gesture_data():
    """Generate random gesture data for testing"""
    gesture_types = ['pinch_down', 'pinch_up', 'targeting', 'grab_begin']
    hands = ['left', 'right']
    
    gesture_type = random.choice(gesture_types)
    hand = random.choice(hands)
    
    base_data = {
        'type': gesture_type,
        'hand': hand,
        'timestamp': datetime.now().isoformat()
    }
    
    # Add specific data based on gesture type
    if gesture_type == 'pinch_down':
        base_data.update({
            'confidence': round(random.uniform(0.7, 1.0), 2),
            'palmOrientation': f"({random.uniform(-1, 1):.2f}, {random.uniform(-1, 1):.2f}, {random.uniform(-1, 1):.2f})"
        })
    elif gesture_type == 'pinch_up':
        base_data.update({
            'palmOrientation': f"({random.uniform(-1, 1):.2f}, {random.uniform(-1, 1):.2f}, {random.uniform(-1, 1):.2f})"
        })
    elif gesture_type == 'targeting':
        base_data.update({
            'isValid': random.choice([True, False]),
            'rayOrigin': f"({random.uniform(-5, 5):.2f}, {random.uniform(-5, 5):.2f}, {random.uniform(-5, 5):.2f})",
            'rayDirection': f"({random.uniform(-1, 1):.2f}, {random.uniform(-1, 1):.2f}, {random.uniform(-1, 1):.2f})"
        })
    
    return base_data

def simulate_state_change():
    """Simulate robot state changes"""
    states = ['ACTIVE', 'STOP']
    return {
        'type': 'state_change',
        'state': random.choice(states),
        'timestamp': datetime.now().isoformat()
    }

def main():
    try:
        # Connect to the Flask-SocketIO server
        print("Connecting to Flask server at localhost:5000...")
        sio.connect('http://localhost:5000')
        
        # Send initial connection message
        time.sleep(1)
        
        gesture_count = 0
        while True:
            # Generate and send gesture data
            if random.random() < 0.8:  # 80% chance for gesture data
                gesture_data = generate_gesture_data()
            else:  # 20% chance for state change
                gesture_data = simulate_state_change()
            
            sio.emit('gesture_data', gesture_data)
            gesture_count += 1
            
            print(f"📤 Sent gesture #{gesture_count}: {gesture_data['type']} ({gesture_data.get('hand', 'N/A')})")
            
            # Wait before sending next gesture (1-3 seconds)
            time.sleep(random.uniform(1, 3))
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping gesture simulation...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        sio.disconnect()

if __name__ == "__main__":
    main()