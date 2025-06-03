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
    apiKey: 'AIzaSyAlBCWpQhnOxo8j9GNqv6OBebVSZZBO8Ck',
    appId: '1:346901812089:web:44b67dd6b2d43c64b9d5a8',
    messagingSenderId: '346901812089',
    projectId: 'mock-interview-app-2025',
    authDomain: 'mock-interview-app-2025.firebaseapp.com',
    storageBucket: 'mock-interview-app-2025.firebasestorage.app',
    measurementId: 'G-RY4Q7B46D6',
  );
}