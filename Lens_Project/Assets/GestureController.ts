@component
export class GestureController extends BaseScriptComponent {
  private gestureModule: GestureModule = require("LensStudio:GestureModule");
  private internetModule: InternetModule = require("LensStudio:InternetModule");
  private isActive: boolean = true; // Track the current state (true = ACTIVE, false = STOP)

  // HTTP connection properties
  private serverUrl: string = "http://172.20.10.5:5000"; // Change to your server URL
  private isConnected: boolean = false;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;

  onAwake() {
    this.setupWebSocket();
    this.setupPinchGestures();
    this.setupTargetingGestures();
    this.setupGrabGestures();
  }

  private setupWebSocket() {
    try {
      print("HTTP connection setup initiated - connecting to gesture server");
      this.connectToServer();
    } catch (error) {
      print("HTTP connection setup failed: " + error);
    }
  }

  private connectToServer() {
    try {
      // Simple connection test - set connected to true for now
      this.isConnected = true;
      print("✅ HTTP client ready for gesture analysis server at " + this.serverUrl);
      this.reconnectAttempts = 0;
    } catch (error) {
      print("Failed to connect to server: " + error);
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      print(`🔄 Attempting reconnection ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
    } else {
      print("❌ Max reconnection attempts reached. Please check server status.");
    }
  }

  private sendGestureData(gestureData: any) {
    if (!this.isConnected) {
      print("⚠️ Cannot send gesture data - not connected to server");
      return;
    }

    try {
      // Create HTTP request using InternetModule
      const request = RemoteServiceHttpRequest.create();
      request.url = this.serverUrl + "/api/gesture";
      request.method = RemoteServiceHttpRequest.HttpRequestMethod.Post;
      request.setHeader("Content-Type", "application/json");
      request.body = JSON.stringify(gestureData);

      this.internetModule.performHttpRequest(request, (response) => {
        if (response.statusCode >= 200 && response.statusCode < 300) {
          print("📤 Gesture data sent successfully: " + gestureData.type + " (" + gestureData.hand + ")");
        } else {
          print("❌ Failed to send gesture data. Status: " + response.statusCode);
          if (response.statusCode >= 500) {
            this.isConnected = false;
            this.scheduleReconnect();
          }
        }
      });
    } catch (error) {
      print("❌ Error sending gesture data: " + error);
      // Don't disconnect on send errors, just log them
    }
  }

  private setupPinchGestures() {
    this.gestureModule.getPinchDownEvent(GestureModule.HandType.Right).add((pinchDownArgs: PinchDownArgs) => {
      print("GESTURE: Right Hand Pinch DOWN - Confidence: " + pinchDownArgs);
      print("Palm Orientation: " + pinchDownArgs.palmOrientation);

      // Send gesture data to server
      this.sendGestureData({
        type: "pinch_down",
        hand: "right",
        confidence: pinchDownArgs.toString(),
        palmOrientation: pinchDownArgs.palmOrientation?.toString() || "N/A",
        timestamp: new Date().toISOString(),
      });
    });

    this.gestureModule.getPinchUpEvent(GestureModule.HandType.Right).add((pinchUpArgs: PinchUpArgs) => {
      print("GESTURE: Right Hand Pinch UP");
      print("Palm Orientation: " + pinchUpArgs.palmOrientation);

      this.sendGestureData({
        type: "pinch_up",
        hand: "right",
        palmOrientation: pinchUpArgs.palmOrientation?.toString() || "N/A",
        timestamp: new Date().toISOString(),
      });
    });

    this.gestureModule.getPinchStrengthEvent(GestureModule.HandType.Right).add((pinchStrengthArgs: PinchStrengthArgs) => {
      print("GESTURE: Right Hand Pinch Strength: " + pinchStrengthArgs);

      this.sendGestureData({
        type: "pinch_strength",
        hand: "right",
        strength: pinchStrengthArgs.toString(),
        timestamp: new Date().toISOString(),
      });
    });

    this.gestureModule.getPinchDownEvent(GestureModule.HandType.Left).add((pinchDownArgs: PinchDownArgs) => {
      print("GESTURE: Left Hand Pinch DOWN - Confidence: " + pinchDownArgs);
      print("Palm Orientation: " + pinchDownArgs.palmOrientation);

      this.sendGestureData({
        type: "pinch_down",
        hand: "left",
        confidence: pinchDownArgs.toString(),
        palmOrientation: pinchDownArgs.palmOrientation?.toString() || "N/A",
        timestamp: new Date().toISOString(),
      });
    });

    this.gestureModule.getPinchUpEvent(GestureModule.HandType.Left).add((pinchUpArgs: PinchUpArgs) => {
      print("GESTURE: Left Hand Pinch UP");
      print("Palm Orientation: " + pinchUpArgs.palmOrientation);

      this.sendGestureData({
        type: "pinch_up",
        hand: "left",
        palmOrientation: pinchUpArgs.palmOrientation?.toString() || "N/A",
        timestamp: new Date().toISOString(),
      });
    });

    this.gestureModule.getPinchStrengthEvent(GestureModule.HandType.Left).add((pinchStrengthArgs: PinchStrengthArgs) => {
      print("GESTURE: Left Hand Pinch Strength: " + pinchStrengthArgs);

      this.sendGestureData({
        type: "pinch_strength",
        hand: "left",
        strength: pinchStrengthArgs.toString(),
        timestamp: new Date().toISOString(),
      });
    });
  }

  private setupTargetingGestures() {
    // Right Hand Targeting
    this.gestureModule.getTargetingDataEvent(GestureModule.HandType.Right).add((targetArgs: TargetingDataArgs) => {
      if (targetArgs.isValid) {
        print("GESTURE: Right Hand Targeting ACTIVE");
        print("Ray Origin: " + targetArgs.rayOriginInWorld);
        print("Ray Direction: " + targetArgs.rayDirectionInWorld);

        this.sendGestureData({
          type: "targeting",
          hand: "right",
          isValid: true,
          rayOrigin: targetArgs.rayOriginInWorld?.toString() || "N/A",
          rayDirection: targetArgs.rayDirectionInWorld?.toString() || "N/A",
          timestamp: new Date().toISOString(),
        });
      } else {
        // Uncomment the line below if you want to see when targeting is invalid
        // print('GESTURE: Right Hand Targeting INVALID');

        this.sendGestureData({
          type: "targeting",
          hand: "right",
          isValid: false,
          timestamp: new Date().toISOString(),
        });
      }
    });

    // Left Hand Targeting
    this.gestureModule.getTargetingDataEvent(GestureModule.HandType.Left).add((targetArgs: TargetingDataArgs) => {
      if (targetArgs.isValid) {
        print("GESTURE: Left Hand Targeting ACTIVE");
        print("Ray Origin: " + targetArgs.rayOriginInWorld);
        print("Ray Direction: " + targetArgs.rayDirectionInWorld);

        this.sendGestureData({
          type: "targeting",
          hand: "left",
          isValid: true,
          rayOrigin: targetArgs.rayOriginInWorld?.toString() || "N/A",
          rayDirection: targetArgs.rayDirectionInWorld?.toString() || "N/A",
          timestamp: new Date().toISOString(),
        });
      } else {
        // Uncomment the line below if you want to see when targeting is invalid
        // print('GESTURE: Left Hand Targeting INVALID');

        this.sendGestureData({
          type: "targeting",
          hand: "left",
          isValid: false,
          timestamp: new Date().toISOString(),
        });
      }
    });
  }

  private setupGrabGestures() {
    // Right Hand Grab - Toggle functionality
    this.gestureModule.getGrabBeginEvent(GestureModule.HandType.Right).add((grabBeginArgs: GrabBeginArgs) => {
      this.toggleGestureState();

      this.sendGestureData({
        type: "grab_begin",
        hand: "right",
        timestamp: new Date().toISOString(),
      });
    });

    // Left Hand Grab - Toggle functionality
    this.gestureModule.getGrabBeginEvent(GestureModule.HandType.Left).add((grabBeginArgs: GrabBeginArgs) => {
      this.toggleGestureState();

      this.sendGestureData({
        type: "grab_begin",
        hand: "left",
        timestamp: new Date().toISOString(),
      });
    });
  }

  private toggleGestureState() {
    this.isActive = !this.isActive;
    const state = this.isActive ? "ACTIVE" : "STOP";
    print(state);

    // Send state change to server
    this.sendGestureData({
      type: "state_change",
      state: state,
      timestamp: new Date().toISOString(),
    });
  }
}
