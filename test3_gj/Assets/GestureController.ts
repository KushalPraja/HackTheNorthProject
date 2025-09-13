@component
export class GestureController extends BaseScriptComponent {
  private gestureModule: GestureModule = require("LensStudio:GestureModule");
  private isActive: boolean = true; // Track the current state (true = ACTIVE, false = STOP)

  onAwake() {
    this.setupPinchGestures();
    this.setupTargetingGestures();
    this.setupGrabGestures();
  }

  private setupPinchGestures() {
    this.gestureModule.getPinchDownEvent(GestureModule.HandType.Right).add((pinchDownArgs: PinchDownArgs) => {
      print("GESTURE: Right Hand Pinch DOWN - Confidence: " + pinchDownArgs);
      print("Palm Orientation: " + pinchDownArgs.palmOrientation);
    });

    this.gestureModule.getPinchUpEvent(GestureModule.HandType.Right).add((pinchUpArgs: PinchUpArgs) => {
      print("GESTURE: Right Hand Pinch UP");
      print("Palm Orientation: " + pinchUpArgs.palmOrientation);
    });

    this.gestureModule.getPinchStrengthEvent(GestureModule.HandType.Right).add((pinchStrengthArgs: PinchStrengthArgs) => {
      print("GESTURE: Right Hand Pinch Strength: " + pinchStrengthArgs);
    });

    this.gestureModule.getPinchDownEvent(GestureModule.HandType.Left).add((pinchDownArgs: PinchDownArgs) => {
      print("GESTURE: Left Hand Pinch DOWN - Confidence: " + pinchDownArgs);
      print("Palm Orientation: " + pinchDownArgs.palmOrientation);
    });

    this.gestureModule.getPinchUpEvent(GestureModule.HandType.Left).add((pinchUpArgs: PinchUpArgs) => {
      print("GESTURE: Left Hand Pinch UP");
      print("Palm Orientation: " + pinchUpArgs.palmOrientation);
    });

    this.gestureModule.getPinchStrengthEvent(GestureModule.HandType.Left).add((pinchStrengthArgs: PinchStrengthArgs) => {
      print("GESTURE: Left Hand Pinch Strength: " + pinchStrengthArgs);
    });
  }

  private setupTargetingGestures() {
    // Right Hand Targeting
    this.gestureModule.getTargetingDataEvent(GestureModule.HandType.Right).add((targetArgs: TargetingDataArgs) => {
      if (targetArgs.isValid) {
        print("GESTURE: Right Hand Targeting ACTIVE");
        print("Ray Origin: " + targetArgs.rayOriginInWorld);
        print("Ray Direction: " + targetArgs.rayDirectionInWorld);
      } else {
        // Uncomment the line below if you want to see when targeting is invalid
        // print('GESTURE: Right Hand Targeting INVALID');
      }
    });

    // Left Hand Targeting
    this.gestureModule.getTargetingDataEvent(GestureModule.HandType.Left).add((targetArgs: TargetingDataArgs) => {
      if (targetArgs.isValid) {
        print("GESTURE: Left Hand Targeting ACTIVE");
        print("Ray Origin: " + targetArgs.rayOriginInWorld);
        print("Ray Direction: " + targetArgs.rayDirectionInWorld);
      } else {
        // Uncomment the line below if you want to see when targeting is invalid
        // print('GESTURE: Left Hand Targeting INVALID');
      }
    });
  }

  private setupGrabGestures() {
    // Right Hand Grab - Toggle functionality
    this.gestureModule.getGrabBeginEvent(GestureModule.HandType.Right).add((grabBeginArgs: GrabBeginArgs) => {
      this.toggleGestureState();
    });

    // Left Hand Grab - Toggle functionality
    this.gestureModule.getGrabBeginEvent(GestureModule.HandType.Left).add((grabBeginArgs: GrabBeginArgs) => {
      this.toggleGestureState();
    });
  }

  private toggleGestureState() {
    this.isActive = !this.isActive;
    const state = this.isActive ? "ACTIVE" : "STOP";
    print(state);
  }
}
