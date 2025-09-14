from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Store gesture data for analysis
gesture_data = []

@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Gesture server is running'})

@app.route('/api/gesture', methods=['POST'])
def receive_gesture():
    """HTTP endpoint to receive gesture data from Lens Studio"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
        
        timestamp = datetime.now().isoformat()
        data['timestamp'] = timestamp
        
        # Store the data for analysis
        gesture_data.append(data)
        
        # Keep only last 100 entries to prevent memory overflow
        if len(gesture_data) > 100:
            gesture_data.pop(0)
        
        print(f"📱 Received from Lens Studio: {data}")
        
        # Broadcast to WebSocket clients (dashboard)
        socketio.emit('gesture_update', data)
        
        # Process gesture for robot control
        process_gesture_for_robot(data)
        
        return jsonify({'status': 'success', 'message': 'Gesture data received'})
        
    except Exception as e:
        print(f"❌ Error processing gesture data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@socketio.on('connect')
def handle_connect():
    print(f'Client connected at {datetime.now()}')
    emit('response', {'data': 'Connected to gesture server'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected at {datetime.now()}')

@socketio.on('gesture_data')
def handle_gesture_data(data):
    """Receive gesture data from client"""
    timestamp = datetime.now().isoformat()
    
    # Add timestamp to the data
    data['timestamp'] = timestamp
    
    # Store the data for analysis
    gesture_data.append(data)
    
    # Keep only last 100 entries to prevent memory overflow
    if len(gesture_data) > 100:
        gesture_data.pop(0)
    
    print(f"Received gesture data: {data}")
    
    # Broadcast to all connected clients (for dashboard updates)
    emit('gesture_update', data, broadcast=True)
    
    # Process gesture for robot control (placeholder)
    process_gesture_for_robot(data)

def process_gesture_for_robot(gesture):
    """Process gesture data for robot control (placeholder function)"""
    gesture_type = gesture.get('type')
    hand = gesture.get('hand')
    
    # Robot control logic would go here
    if gesture_type == 'pinch_down':
        print(f"Robot command: {hand} hand pinch detected - could trigger grip")
    elif gesture_type == 'pinch_up':
        print(f"Robot command: {hand} hand release detected - could release grip")
    elif gesture_type == 'targeting':
        print(f"Robot command: {hand} hand targeting - could move to position")
    elif gesture_type == 'grab_begin':
        print(f"Robot command: {hand} hand grab - toggle action")
    elif gesture_type == 'state_change':
        print(f"Robot command: State changed to {gesture.get('state')}")

@socketio.on('get_gesture_history')
def handle_get_history():
    """Send gesture history to requesting client"""
    emit('gesture_history', gesture_data)

if __name__ == '__main__':
    print("Starting Flask-SocketIO server...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)