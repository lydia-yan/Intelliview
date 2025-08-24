## Intelliview iOS Run Guide

### Prerequisites
1) Xcode (with iOS Simulator)
2) CocoaPods (`pod --version`)
3) Flutter SDK (`flutter --version`)
4) Firebase CLI (logged in) and FlutterFire CLI

### One-time setup (already configured in this branch)
- `ios/Runner/GoogleService-Info.plist` is present
- `lib/firebase_options.dart` includes iOS & Web configs
- iOS deployment target set to 15.0 in `ios/Podfile`

### Run on iOS Simulator
1) Get packages
```
flutter pub get
```
2) Install CocoaPods (from `frontend/mocker_web/ios`)
```
cd ios && pod install && cd ..
```
3) Start a simulator
```
open -a Simulator
```
4) List devices and run
```
flutter devices
flutter run -d "iPhone 16 Pro"
```

### Run on a physical device
1) Open `ios/Runner.xcworkspace` in Xcode
2) Set your Team & unique Bundle Identifier
3) Trust your developer certificate on device if needed
4) From Flutter:
```
flutter run -d <your_device_id>
```

### Troubleshooting
- Build cache issues:
```
flutter clean && rm -rf .dart_tool build
flutter pub get
cd ios && pod install --repo-update && cd ..
```
- Google Sign-In callback:
  - Ensure `Info.plist` contains CFBundleURLTypes with the `REVERSED_CLIENT_ID` from `GoogleService-Info.plist`.
- CocoaPods base config warning:
  - Can be ignored, or set the target base config in Xcode to Pods-Runner `.xcconfig`.
- Missing Firebase login:
```
firebase login
```

