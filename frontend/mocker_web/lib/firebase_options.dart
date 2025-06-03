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
    apiKey: 'AIxxxxxxAlBxxxebVO8Ck',
    appId: '1:346xxx29:web:67xxx3c6xxxa8',
    messagingSenderId: '3xx9xxx2xxxxx9',
    projectId: 'mock-interview-app-2025',
    authDomain: 'mock-interview-app-2025.firebaseapp.com',
    storageBucket: 'mock-interview-app-2025.firebasestorage.app',
    measurementId: 'G-xxxxxQxxxD6',
  );
}