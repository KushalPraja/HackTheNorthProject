@component
export class GestureController extends BaseScriptComponent {
  private gestureModule: GestureModule = require("LensStudio:GestureModule");
  private internetModule: InternetModule = require("LensStudio:InternetModule");
  private stopped: boolean = false; // Track if robot is stopped

  // Server connection properties
  private serverUrl: string = "http://172.20.10.5:5000"; // Change to your server URL
  private heartbeatIntervalMs: number = 500; // Send updates every 500ms
  private lastHeartbeatTime: number = 0;
  private lastSentState: string = "";

  // Hand direction tracking
  private rightHandHorizontal: string = "not active";
  private rightHandActive: boolean = true;
  private leftHandHorizontal: string = "not active";
  private leftHandVertical: string = "not active";
  private leftHandActive: boolean = true;

  onAwake() {
    print("🤖 Starting Robot Control System");
    this.setupGestures();
    this.setupHeartbeat();
    // Send initial status
    this.sendRobotStatus();
  }

  private setupGestures() {
    print("Setting up gesture recognition...");

    // Grab gestures to toggle active state per hand
    this.gestureModule.getGrabBeginEvent(GestureModule.HandType.Right).add(() => {
      this.toggleHandActive("right");
    });

    this.gestureModule.getGrabBeginEvent(GestureModule.HandType.Left).add(() => {
      this.toggleHandActive("left");
    });

    // Targeting gestures for direction
    this.gestureModule.getTargetingDataEvent(GestureModule.HandType.Right).add((targetArgs: TargetingDataArgs) => {
      if (targetArgs.isValid && this.rightHandActive) {
        this.rightHandHorizontal = this.calculateHorizontalDirection(targetArgs.rayDirectionInWorld);
      } else {
        this.rightHandHorizontal = "not active";
      }
    });

    this.gestureModule.getTargetingDataEvent(GestureModule.HandType.Left).add((targetArgs: TargetingDataArgs) => {
      if (targetArgs.isValid && this.leftHandActive) {
        this.leftHandHorizontal = this.calculateHorizontalDirection(targetArgs.rayDirectionInWorld);
        this.leftHandVertical = this.calculateVerticalDirection(targetArgs.rayDirectionInWorld);
      } else {
        this.leftHandHorizontal = "not active";
        this.leftHandVertical = "not active";
      }
    });
  }

  private calculateHorizontalDirection(rayDirection: any): string {
    if (!rayDirection) return "not active";

    try {
      // Parse the vector - assuming it's a Vec3 or similar with x property
      const x = rayDirection.x;

      if (x < -0.2) return "left";
      else if (x > 0.2) return "right";
      else return "straight";
    } catch (e) {
      return "straight";
    }
  }

  private calculateVerticalDirection(rayDirection: any): string {
    if (!rayDirection) return "not active";

    try {
      // Parse the vector - assuming it's a Vec3 or similar with y property
      const y = rayDirection.y;

      if (y > 0.2) return "up";
      else if (y < -0.2) return "down";
      else return "neutral";
    } catch (e) {
      return "neutral";
    }
  }

  private toggleHandActive(hand: string) {
    if (hand === "right") {
      this.rightHandActive = !this.rightHandActive;
      print(`🤖 Right Hand ${this.rightHandActive ? "ACTIVE" : "INACTIVE"}`);
      if (!this.rightHandActive) {
        this.rightHandHorizontal = "not active";
      }
    } else if (hand === "left") {
      this.leftHandActive = !this.leftHandActive;
      print(`🤖 Left Hand ${this.leftHandActive ? "ACTIVE" : "INACTIVE"}`);
      if (!this.leftHandActive) {
        this.leftHandHorizontal = "not active";
        this.leftHandVertical = "not active";
      }
    }
    this.sendRobotStatus();
  }

  private setupHeartbeat() {
    // Use update event to send periodic updates (debounced)
    const updateEvent = this.createEvent("UpdateEvent") as UpdateEvent;
    updateEvent.bind(() => {
      this.onUpdate();
    });
  }

  private onUpdate() {
    const currentTime = getTime();
    if (currentTime - this.lastHeartbeatTime >= this.heartbeatIntervalMs / 1000) {
      this.sendRobotStatus();
      this.lastHeartbeatTime = currentTime;
    }
  }

  private sendRobotStatus() {
    const data = {
      stopped: this.stopped,
      hand: {
        right: {
          horizontal: this.rightHandHorizontal,
          active: this.rightHandActive,
        },
        left: {
          horizontal: this.leftHandHorizontal,
          vertical: this.leftHandVertical,
          active: this.leftHandActive,
        },
      },
    };

    // Debounce: Only send if state changed or on interval
    const stateStr = JSON.stringify(data);
    if (stateStr === this.lastSentState) {
      return;
    }
    this.lastSentState = stateStr;

    try {
      const request = RemoteServiceHttpRequest.create();
      request.url = this.serverUrl + "/api/robot-status";
      request.method = RemoteServiceHttpRequest.HttpRequestMethod.Post;
      request.setHeader("Content-Type", "application/json");
      request.body = stateStr;

      this.internetModule.performHttpRequest(request, (response) => {
        if (response.statusCode >= 200 && response.statusCode < 300) {
          // Success
        } else {
          print(`❌ Failed to send robot status. Status: ${response.statusCode}`);
        }
      });
    } catch (error) {
      print("❌ Error sending robot status: " + error);
    }
  }
}
