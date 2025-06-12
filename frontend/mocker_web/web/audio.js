// web/audio.js
let audioContext;
let mediaStream;
let processor;
let isRecording = false;

window.startRecording = async function (sampleRate = 16000) {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    return { success: false, error: "getUserMedia not supported" };
  }

  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate });
    
    const source = audioContext.createMediaStreamSource(mediaStream);
    processor = audioContext.createScriptProcessor(4096, 1, 1);

    processor.onaudioprocess = (e) => {
      if (!isRecording) return;
      const inputData = e.inputBuffer.getChannelData(0);
      // Convert float32 to 16-bit PCM
      const pcmData = new Int16Array(inputData.length);
      for (let i = 0; i < inputData.length; i++) {
        pcmData[i] = Math.max(-32768, Math.min(32767, inputData[i] * 32768));
      }
      // Send PCM data to Dart via callback
      if (window.onAudioData) {
        window.onAudioData(new Uint8Array(pcmData.buffer));
      }
    };

    source.connect(processor);
    processor.connect(audioContext.destination);
    isRecording = true;
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

window.stopRecording = function () {
  if (isRecording) {
    isRecording = false;
    if (processor) processor.disconnect();
    if (mediaStream) {
      mediaStream.getTracks().forEach(track => track.stop());
    }
    if (audioContext) audioContext.close();
  }
};

window.playPcm = function (pcmData) {
  try {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
    const buffer = audioCtx.createBuffer(1, pcmData.length / 2, 16000);
    const channelData = buffer.getChannelData(0);

    // Convert 16-bit PCM (Int16Array) to float32
    const int16Data = new Int16Array(pcmData.buffer);
    for (let i = 0; i < int16Data.length; i++) {
      channelData[i] = int16Data[i] / 32768.0;
    }

    const source = audioCtx.createBufferSource();
    source.buffer = buffer;
    source.connect(audioCtx.destination);
    source.start();
  } catch (error) {
    console.error('Error playing PCM audio:', error);
  }
};