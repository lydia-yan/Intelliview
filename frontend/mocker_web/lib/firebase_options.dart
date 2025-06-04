import 'package:firebase_core/firebase_core.dart' show FirebaseOptions;
import 'package:flutter/foundation.dart'
    show defaultTargetPlatform, kIsWeb, TargetPlatform;

class DefaultFirebaseOptions {
  static FirebaseOptions get currentPlatform {
    if (kIsWeb) {
      return web;
    }
    // only support Web platform, other platforms throw error
    throw UnsupportedError(
      'DefaultFirebaseOptions are not supported for this platform.',
    );
  }

  static const FirebaseOptions web = FirebaseOptions(
    apiKey: 'AIzaxxxbVSZZBO8Ck',
    appId: '1:34xxxx901xxxxxxx64b9d5a8',
    messagingSenderId: '346xxxxxxx9',
    projectId: 'mock-interview-app-2025',
    authDomain: 'mock-interview-app-2025.firebaseapp.com',
    storageBucket: 'mock-interviewxxxxxtorage.app',
    measurementId: 'G-Rxxxxx6D6',
  );
}