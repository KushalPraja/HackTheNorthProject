from flask import Flask, render_template, request, jsonify
from flask_sock import Sock
from datetime import datetime
import json
import paho.mqtt.client as mqtt
import ssl
import time
import threading

app = Flask(__name__)
sock = Sock(app)

# MQTT Configuration for HiveMQ Cloud
HIVEMQ_HOST = "a2016a11d3614243aeb27bda75dd2204.s1.eu.hivemq.cloud"
HIVEMQ_PORT = 8883
MQTT_TOPIC = "robot"
HIVEMQ_USERNAME = "kushal"
HIVEMQ_PASSWORD = "Hackthenorth25"

# Global variables for MQTT status
mqtt_connected = False
mqtt_client = None

def on_connect(client, userdata, flags, rc):
    """Callback when MQTT client connects"""
    global mqtt_connected
    if rc == 0:
        mqtt_connected = True
        print(f"✅ Connected to HiveMQ Cloud! Result code: {rc}")
    else:
        mqtt_connected = False
        print(f"❌ Failed to connect to HiveMQ, return code: {rc}")
        # Connection result codes:
        # 0: Connection successful
        # 1: Connection refused - incorrect protocol version
        # 2: Connection refused - invalid client identifier
        # 3: Connection refused - server unavailable
        # 4: Connection refused - bad username or password
        # 5: Connection refused - not authorised

def on_publish(client, userdata, mid):
    """Callback when message is published"""
    print(f"📡 Message published successfully! Message ID: {mid}")

def on_disconnect(client, userdata, rc):
    """Callback when MQTT client disconnects"""
    global mqtt_connected
    mqtt_connected = False
    print(f"🔌 Disconnected from HiveMQ Cloud. Result code: {rc}")

def on_log(client, userdata, level, buf):
    """Callback for MQTT client logging"""
    print(f"🔍 MQTT Log: {buf}")

def init_mqtt():
    """Initialize MQTT client with proper configuration"""
    global mqtt_client
    
    try:
        # Create client with unique ID
        client_id = f"flask_robot_{int(time.time())}"
        mqtt_client = mqtt.Client(client_id=client_id, clean_session=True)
        
        # Set callbacks
        mqtt_client.on_connect = on_connect
        mqtt_client.on_publish = on_publish
        mqtt_client.on_disconnect = on_disconnect
        mqtt_client.on_log = on_log  # Enable logging for debugging
        
        # Set credentials
        mqtt_client.username_pw_set(HIVEMQ_USERNAME, HIVEMQ_PASSWORD)
        
        # Configure TLS for secure connection
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        mqtt_client.tls_set_context(context)
        
        # Alternative TLS setup (try this if above doesn't work)
        # mqtt_client.tls_set(ca_certs=None, certfile=None, keyfile=None,
        #                    cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS,
        #                    ciphers=None)
        
        print(f"🔄 Attempting to connect to {HIVEMQ_HOST}:{HIVEMQ_PORT}")
        
        # Connect with timeout
        mqtt_client.connect(HIVEMQ_HOST, HIVEMQ_PORT, 60)
        mqtt_client.loop_start()
        
        # Wait a bit for connection
        time.sleep(2)
        
        if mqtt_connected:
            print(f"✅ MQTT initialization successful")
        else:
            print(f"⚠️ MQTT connection may still be in progress...")
            
    except Exception as e:
        print(f"❌ MQTT initialization failed: {e}")
        return False
    
    return True

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

def publish_to_mqtt(data):
    """Publish robot state to HiveMQ Cloud"""
    global mqtt_client, mqtt_connected
    
    if not mqtt_client:
        print("❌ MQTT client not initialized")
        return False
    
    try:
        # Check if connected
        if not mqtt_connected:
            print("❌ MQTT not connected, attempting reconnect...")
            try:
                mqtt_client.reconnect()
                time.sleep(1)  # Give it a moment
            except Exception as e:
                print(f"❌ Reconnection failed: {e}")
                return False
        
        # Prepare payload
        payload = json.dumps(data, indent=2)
        
        # Publish with QoS 1 for guaranteed delivery
        result = mqtt_client.publish(MQTT_TOPIC, payload, qos=1, retain=False)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"📡 Published to MQTT topic '{MQTT_TOPIC}':")
            print(f"    {payload}")
            return True
        else:
            print(f"❌ MQTT publish failed with return code: {result.rc}")
            return False
            
    except Exception as e:
        print(f"❌ MQTT publish exception: {e}")
        return False

@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'ok', 
        'message': 'Robot control server is running',
        'mqtt_connected': mqtt_connected
    })

@app.route('/mqtt-status')
def mqtt_status():
    """Check MQTT connection status"""
    return jsonify({
        'connected': mqtt_connected,
        'client_initialized': mqtt_client is not None,
        'host': HIVEMQ_HOST,
        'port': HIVEMQ_PORT,
        'topic': MQTT_TOPIC
    })

@app.route('/test-publish')
def test_publish():
    """Test MQTT publishing"""
    test_data = {
        'test': True,
        'timestamp': datetime.now().isoformat(),
        'message': 'Test message from Flask app'
    }
    
    success = publish_to_mqtt(test_data)
    
    return jsonify({
        'success': success,
        'mqtt_connected': mqtt_connected,
        'test_data': test_data
    })

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

        # Publish to MQTT
        mqtt_success = publish_to_mqtt(robot_state)

        # Broadcast to dashboard clients
        broadcast_state()

        return jsonify({
            'status': 'ok',
            'mqtt_published': mqtt_success,
            'mqtt_connected': mqtt_connected
        }), 200

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
                
                print(f"🤖 Robot State Updated via WebSocket: {json.dumps(robot_state, indent=2)}")
                
                # Publish to MQTT
                publish_to_mqtt(robot_state)
                
                # Broadcast updated state to all connected clients
                broadcast_state()
                
            except json.JSONDecodeError:
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
    print("🚀 Starting Robot Control Server...")
    print("🔄 Initializing MQTT connection...")
    
    # Initialize MQTT
    init_mqtt()
    
    # Give MQTT a moment to connect
    time.sleep(3)
    
    print("\n📋 Available endpoints:")
    print("  - Dashboard: http://localhost:5000")
    print("  - Health check: http://localhost:5000/health")
    print("  - MQTT status: http://localhost:5000/mqtt-status")
    print("  - Test publish: http://localhost:5000/test-publish")
    print("  - WebSocket endpoint: /ws")
    
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)