class PlayerProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.bufferQueue = [];
    this.port.onmessage = (event) => {
      this.bufferQueue.push(new Float32Array(event.data));
    };
  }

  process(inputs, outputs) {
    const output = outputs[0];
    const channel = output[0];

    if (this.bufferQueue.length === 0) {
      channel.fill(0);
    } else {
      const nextBuffer = this.bufferQueue.shift();
      for (let i = 0; i < channel.length; i++) {
        channel[i] = nextBuffer[i] || 0;
      }
    }

    return true;
  }
}

registerProcessor('player.worklet', PlayerProcessor);

export async function startAudioPlayerWorklet() {
  const context = new AudioContext();
  await context.audioWorklet.addModule('./audio-player-worklet.js');

  const node = new AudioWorkletNode(context, 'player.worklet');
  node.connect(context.destination);

  return [node, context];
}

