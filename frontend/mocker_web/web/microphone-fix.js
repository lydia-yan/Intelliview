// This script fixes microphone access issues
console.log('Microphone fix script loaded');

// Function to request microphone permission explicitly
function requestMicrophonePermission() {
  return navigator.mediaDevices.getUserMedia({ audio: true })
    .then(function(stream) {
      console.log('Microphone permission granted');
      // Stop all tracks from this test stream
      stream.getTracks().forEach(track => track.stop());
      return true;
    })
    .catch(function(err) {
      console.error('Error accessing microphone:', err.name, err.message);
      return false;
    });
}

// Add a global function to check microphone
window.checkMicrophone = function() {
  return requestMicrophonePermission();
};

// Try to request permission on page load
document.addEventListener('DOMContentLoaded', function() {
  console.log('Requesting microphone permission on page load');
  requestMicrophonePermission();
});