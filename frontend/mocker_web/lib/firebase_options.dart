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
    apiKey: "AIzaSyD_SVRmsjPDNxs7q_pYj0QNFXIrqnqkSDE",
    authDomain: "aiview-fa69f.firebaseapp.com",
    projectId: "aiview-fa69f",
    storageBucket: "aiview-fa69f.firebasestorage.app",
    messagingSenderId: "1022761324834",
    appId: "1:1022761324834:web:d966d33a386efb9192157b",
    measurementId: "G-R4BK02VM8F",
  );
}
