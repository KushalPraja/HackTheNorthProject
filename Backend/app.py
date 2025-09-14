from flask import Flask, render_template, request, jsonify
from flask_sock import Sock
from datetime import datetime
import json

app = Flask(__name__)
sock = Sock(app)

# Store current robot state
robot_state = {
    'stopped': False,
    'hand': {
        'right': {
            'horizontal': 'not active',
            'active': True
        },
        'left': {
            'horizontal': 'not active', 
            'vertical': 'not active',
            'active': True
        }
    }
}

# Track connected websocket clients
clients = set()


@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Robot control server is running'})



# Get current robot state
@app.route('/api/state', methods=['GET'])
def get_robot_state():
    return jsonify(robot_state)

# Receive robot status from GestureController (HTTP POST)
@app.route('/api/robot-status', methods=['POST'])
def update_robot_status():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({'error': 'No data received'}), 400

        print(f"📨 Received robot status: {json.dumps(data, indent=2)}")

        # Validate and update stopped state
        if 'stopped' in data:
            robot_state['stopped'] = bool(data['stopped'])

        # Validate and update hand directions
        if 'hand' in data:
            hand = data['hand']
            if 'right' in hand:
                if isinstance(hand['right'], dict):
                    if 'horizontal' in hand['right']:
                        robot_state['hand']['right']['horizontal'] = str(hand['right']['horizontal'])
                    if 'active' in hand['right']:
                        robot_state['hand']['right']['active'] = bool(hand['right']['active'])
                else:
                    # Legacy support
                    robot_state['hand']['right']['horizontal'] = str(hand['right'])
                    
            if 'left' in hand:
                if isinstance(hand['left'], dict):
                    if 'horizontal' in hand['left']:
                        robot_state['hand']['left']['horizontal'] = str(hand['left']['horizontal'])
                    if 'vertical' in hand['left']:
                        robot_state['hand']['left']['vertical'] = str(hand['left']['vertical'])
                    if 'active' in hand['left']:
                        robot_state['hand']['left']['active'] = bool(hand['left']['active'])
                else:
                    # Legacy support
                    robot_state['hand']['left']['horizontal'] = str(hand['left'])

        print(f"🤖 Updated robot state: {json.dumps(robot_state, indent=2)}")

        # Broadcast to dashboard clients
        broadcast_state()
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        print(f"❌ Error updating robot status: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/')
def dashboard():
    return render_template('dashboard.html')


@sock.route('/ws')
def ws_route(ws):
    """Handle websocket clients from Lens Studio and dashboard"""
    print("WebSocket client connected")
    clients.add(ws)

    # Send current state on connect
    try:
        ws.send(json.dumps(robot_state))
        
        while True:
            data = ws.receive()
            if data is None:
                break

            try:
                received_data = json.loads(data)
                
                # Update robot state with received data
                if 'stopped' in received_data:
                    robot_state['stopped'] = received_data['stopped']
                
                if 'hand' in received_data:
                    if 'right' in received_data['hand']:
                        robot_state['hand']['right'] = received_data['hand']['right']
                    if 'left' in received_data['hand']:
                        robot_state['hand']['left'] = received_data['hand']['left']

                print(f"🤖 Robot State Updated: Stopped={robot_state['stopped']}, Right={robot_state['hand']['right']}, Left={robot_state['hand']['left']}")

                # Broadcast updated state to all connected clients
                broadcast_state()

            except json.JSONDecodeError:
                # Ignore non-JSON messages
                continue
            except Exception as e:
                print(f"Error processing WebSocket message: {e}")

    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        clients.discard(ws)
        print("WebSocket client disconnected")


def broadcast_state():
    """Broadcast current robot state to all connected clients"""
    payload = json.dumps(robot_state)
    to_remove = []
    
    for client in list(clients):
        try:
            client.send(payload)
        except Exception:
            to_remove.append(client)
    
    for client in to_remove:
        clients.discard(client)


if __name__ == '__main__':
    print("Starting Robot Control Server...")
    print("WebSocket endpoint: /ws")
    print("Dashboard: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
