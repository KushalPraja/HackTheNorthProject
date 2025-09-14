#!/usr/bin/env python3
"""
MQTT Connection Debug Script
Tests various connection scenarios and provides detailed diagnostics
"""

import paho.mqtt.client as mqtt
import json
import time
import ssl
import socket
from datetime import datetime

# Configuration
HIVEMQ_HOST = "a2016a11d3614243aeb27bda75dd2204.s1.eu.hivemq.cloud"
HIVEMQ_PORT = 8883
MQTT_TOPIC = "robot"
HIVEMQ_USERNAME = "kushal"
HIVEMQ_PASSWORD = "Hackthenorth25"

def test_dns_resolution():
    """Test if we can resolve the HiveMQ hostname"""
    print("🔍 Testing DNS resolution...")
    try:
        import socket
        ip = socket.gethostbyname(HIVEMQ_HOST)
        print(f"✅ DNS resolution successful: {HIVEMQ_HOST} -> {ip}")
        return True
    except Exception as e:
        print(f"❌ DNS resolution failed: {e}")
        return False

def test_tcp_connection():
    """Test basic TCP connection to HiveMQ"""
    print(f"🔍 Testing TCP connection to {HIVEMQ_HOST}:{HIVEMQ_PORT}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((HIVEMQ_HOST, HIVEMQ_PORT))
        sock.close()
        
        if result == 0:
            print("✅ TCP connection successful")
            return True
        else:
            print(f"❌ TCP connection failed with error code: {result}")
            return False
    except Exception as e:
        print(f"❌ TCP connection error: {e}")
        return False

def test_ssl_connection():
    """Test SSL/TLS connection"""
    print(f"🔍 Testing SSL/TLS connection...")
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection((HIVEMQ_HOST, HIVEMQ_PORT), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=HIVEMQ_HOST) as ssock:
                print("✅ SSL/TLS connection successful")
                print(f"   SSL version: {ssock.version()}")
                print(f"   Cipher: {ssock.cipher()}")
                return True
    except Exception as e:
        print(f"❌ SSL/TLS connection failed: {e}")
        return False

class MQTTTestClient:
    def __init__(self):
        self.connected = False
        self.connection_result = None
        self.published_messages = []
        self.received_messages = []
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback for connection"""
        self.connection_result = rc
        if rc == 0:
            self.connected = True
            print(f"✅ MQTT Connected! Result code: {rc}")
            print(f"   Session present: {flags['session present']}")
            # Subscribe to our topic
            client.subscribe(MQTT_TOPIC)
            print(f"📡 Subscribed to topic: {MQTT_TOPIC}")
        else:
            self.connected = False
            error_messages = {
                1: "Connection refused - incorrect protocol version",
                2: "Connection refused - invalid client identifier",
                3: "Connection refused - server unavailable",
                4: "Connection refused - bad username or password",
                5: "Connection refused - not authorised"
            }
            print(f"❌ MQTT Connection failed: {error_messages.get(rc, f'Unknown error code {rc}')}")
    
    def on_publish(self, client, userdata, mid):
        """Callback for publish"""
        self.published_messages.append(mid)
        print(f"📡 Message published successfully! Message ID: {mid}")
    
    def on_message(self, client, userdata, msg):
        """Callback for received messages"""
        try:
            payload = json.loads(msg.payload.decode())
            self.received_messages.append(payload)
            print(f"📨 Received message on {msg.topic}:")
            print(f"   {json.dumps(payload, indent=2)}")
        except:
            print(f"📨 Received raw message: {msg.payload.decode()}")
    
    def on_disconnect(self, client, userdata, rc):
        """Callback for disconnect"""
        self.connected = False
        print(f"🔌 Disconnected with result code: {rc}")
    
    def on_log(self, client, userdata, level, buf):
        """Callback for logging"""
        print(f"🔍 MQTT Log [{level}]: {buf}")

def test_mqtt_connection():
    """Test MQTT connection with detailed logging"""
    print("🔍 Testing MQTT connection...")
    
    test_client = MQTTTestClient()
    
    # Create client
    client_id = f"debug_test_{int(time.time())}"
    client = mqtt.Client(client_id=client_id, clean_session=True)
    
    # Set callbacks
    client.on_connect = test_client.on_connect
    client.on_publish = test_client.on_publish
    client.on_message = test_client.on_message
    client.on_disconnect = test_client.on_disconnect
    client.on_log = test_client.on_log
    
    # Set credentials
    client.username_pw_set(HIVEMQ_USERNAME, HIVEMQ_PASSWORD)
    
    # Configure TLS
    try:
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        client.tls_set_context(context)
        print("✅ TLS configured successfully")
    except Exception as e:
        print(f"❌ TLS configuration failed: {e}")
        return False
    
    # Connect
    try:
        print(f"🔄 Connecting to {HIVEMQ_HOST}:{HIVEMQ_PORT} as {client_id}...")
        client.connect(HIVEMQ_HOST, HIVEMQ_PORT, 60)
        client.loop_start()
        
        # Wait for connection
        timeout = 10
        start_time = time.time()
        while test_client.connection_result is None and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        if test_client.connected:
            print("✅ MQTT connection established!")
            
            # Test publishing
            test_message = {
                "test": True,
                "timestamp": datetime.now().isoformat(),
                "client_id": client_id,
                "message": "Debug test message"
            }
            
            print("🔄 Publishing test message...")
            result = client.publish(MQTT_TOPIC, json.dumps(test_message), qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print("✅ Test message queued for publishing")
                
                # Wait a bit to see if we receive our own message
                time.sleep(2)
                
                if len(test_client.received_messages) > 0:
                    print("✅ Message successfully received back!")
                else:
                    print("⚠️ Message published but not received back (this might be normal)")
                
            else:
                print(f"❌ Failed to publish test message, return code: {result.rc}")
            
            # Cleanup
            client.loop_stop()
            client.disconnect()
            return True
            
        else:
            print(f"❌ MQTT connection failed with code: {test_client.connection_result}")
            client.loop_stop()
            return False
            
    except Exception as e:
        print(f"❌ MQTT connection exception: {e}")
        return False

def main():
    """Main diagnostic function"""
    print("🚀 Starting MQTT Connection Diagnostics")
    print("=" * 60)
    
    # Test 1: DNS Resolution
    dns_ok = test_dns_resolution()
    print()
    
    # Test 2: TCP Connection
    tcp_ok = test_tcp_connection()
    print()
    
    # Test 3: SSL/TLS Connection
    ssl_ok = test_ssl_connection()
    print()
    
    # Test 4: MQTT Connection
    if dns_ok and tcp_ok and ssl_ok:
        mqtt_ok = test_mqtt_connection()
    else:
        print("⚠️ Skipping MQTT test due to previous failures")
        mqtt_ok = False
    
    print()
    print("=" * 60)
    print("🏁 DIAGNOSTIC SUMMARY:")
    print(f"   DNS Resolution: {'✅' if dns_ok else '❌'}")
    print(f"   TCP Connection: {'✅' if tcp_ok else '❌'}")
    print(f"   SSL/TLS Connection: {'✅' if ssl_ok else '❌'}")
    print(f"   MQTT Connection: {'✅' if mqtt_ok else '❌'}")
    
    if not mqtt_ok:
        print("\n🔧 TROUBLESHOOTING SUGGESTIONS:")
        if not dns_ok:
            print("   • Check your internet connection")
            print("   • Try using a different DNS server")
        if not tcp_ok:
            print("   • Check if firewall is blocking the connection")
            print("   • Verify the hostname and port are correct")
        if not ssl_ok:
            print("   • SSL/TLS connection failed - this might be a certificate issue")
        if dns_ok and tcp_ok and ssl_ok and not mqtt_ok:
            print("   • Check your HiveMQ Cloud credentials")
            print("   • Verify your HiveMQ cluster is running")
            print("   • Check HiveMQ access control settings")
            print("   • Try creating a new HiveMQ cluster")
    
    print("=" * 60)

if __name__ == "__main__":
    main()