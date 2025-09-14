#!/usr/bin/env python3
"""
Simple MQTT Subscriber Test Script
Subscribes to the robot control topic and displays received messages
"""

import paho.mqtt.client as mqtt
import json
from datetime import datetime

# MQTT Configuration (same as your app.py)
HIVEMQ_HOST = "a2016a11d3614243aeb27bda75dd2204.s1.eu.hivemq.cloud"
HIVEMQ_PORT = 8883
MQTT_TOPIC = "robot"
HIVEMQ_USERNAME = "kushal"
HIVEMQ_PASSWORD = "Hackthenorth25"

def on_connect(client, userdata, flags, rc):
    """Callback when MQTT client connects"""
    if rc == 0:
        print(f"✅ Connected to HiveMQ Cloud!")
        print(f"📡 Subscribing to topic: {MQTT_TOPIC}")
        client.subscribe(MQTT_TOPIC)
        print("🔄 Waiting for messages... (Press Ctrl+C to exit)")
        print("-" * 50)
    else:
        print(f"❌ Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    """Callback when a message is received"""
    try:
        # Get timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Parse JSON message
        payload = json.loads(msg.payload.decode())
        
        # Pretty print the received data
        print(f"📨 [{timestamp}] Received robot state:")
        print(f"   🛑 Stopped: {payload.get('stopped', 'N/A')}")
        
        if 'hand' in payload:
            hand = payload['hand']
            if 'right' in hand:
                right = hand['right']
                print(f"   👉 Right Hand: {right.get('horizontal', 'N/A')} (Active: {right.get('active', 'N/A')})")
            
            if 'left' in hand:
                left = hand['left']
                print(f"   👈 Left Hand: H:{left.get('horizontal', 'N/A')} V:{left.get('vertical', 'N/A')} (Active: {left.get('active', 'N/A')})")
        
        print("-" * 50)
        
    except json.JSONDecodeError:
        print(f"📨 [{timestamp}] Raw message: {msg.payload.decode()}")
        print("-" * 50)
    except Exception as e:
        print(f"❌ Error processing message: {e}")

def on_disconnect(client, userdata, rc):
    """Callback when MQTT client disconnects"""
    print("🔌 Disconnected from HiveMQ Cloud")

def main():
    print("🚀 Starting MQTT Subscriber Test")
    print(f"🌐 Connecting to: {HIVEMQ_HOST}:{HIVEMQ_PORT}")
    
    # Create MQTT client
    client = mqtt.Client()
    
    # Set credentials
    client.username_pw_set(HIVEMQ_USERNAME, HIVEMQ_PASSWORD)
    
    # Set TLS for secure connection
    client.tls_set()
    
    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    try:
        # Connect to broker
        client.connect(HIVEMQ_HOST, HIVEMQ_PORT, 60)
        
        # Start the loop to process network traffic
        client.loop_forever()
        
    except KeyboardInterrupt:
        print("\n👋 Stopping subscriber...")
        client.disconnect()
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    main()