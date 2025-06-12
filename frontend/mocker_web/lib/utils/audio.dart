// lib/utils/audio_interop.dart
import 'dart:js' as js;
import 'dart:typed_data';
import 'dart:js_interop' as js_interop;
import 'dart:convert';
import 'package:js/js_util.dart' as js_util;

// Check if audio interop functions are available
bool checkAudioInteropFunctions() {
  return js.context.hasProperty('startRecording'.toJS) &&
      js.context.hasProperty('stopRecording'.toJS) &&
      js.context.hasProperty('playPcm'.toJS);
}

// Test audio interop (for debugging)
bool testAudioInterop(void Function(Uint8List) callback) {
  try {
    // Create a test callback
    js.context['testCallback'] = js.allowInterop((
      js_interop.JSUint8Array data,
    ) {
      callback(data.toDart);
    });
    // Simulate a test call (you can modify this based on your JS implementation)
    return true;
  } catch (e) {
    print('Test audio interop failed: $e');
    return false;
  }
}

// Start audio recording
void startAudioInterop(void Function(Uint8List) callback) {
  // Register the callback for audio data
  js.context['onAudioData'] = js.allowInterop((js_interop.JSUint8Array data) {
    callback(data.toDart);
  });
  // Call startRecording with default sample rate (16kHz)
  js.context.callMethod('startRecording', [16000]);
}

// Stop audio recording
void stopAudioInterop() {
  js.context.callMethod('stopRecording', []);
}

// Play PCM audio
void playPcm(String base64Audio) {
  final audioData = base64Decode(base64Audio);
  final jsArray = js_util.jsify(audioData);
  js.context.callMethod('playPcm', [jsArray]);
}
