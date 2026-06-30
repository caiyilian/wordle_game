// Web Speech API pronunciation + Web Audio API sound effects
const audioCtx = (() => {
  try { return new (window.AudioContext || (window as any).webkitAudioContext)() } catch { return null }
})()

function isSoundEnabled(): boolean {
  return localStorage.getItem('wordle_sound') !== 'false'
}

function playTone(freq: number, duration: number, type: OscillatorType = 'sine') {
  if (!audioCtx || !isSoundEnabled()) return
  const osc = audioCtx.createOscillator()
  const gain = audioCtx.createGain()
  osc.type = type
  osc.frequency.value = freq
  gain.gain.setValueAtTime(0.3, audioCtx.currentTime)
  gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + duration)
  osc.connect(gain)
  gain.connect(audioCtx.destination)
  osc.start()
  osc.stop(audioCtx.currentTime + duration)
}

export function useWordSound() {
  function speakWord(word: string) {
    if (!isSoundEnabled()) return
    try {
      const utterance = new SpeechSynthesisUtterance(word)
      utterance.lang = 'en-US'
      utterance.rate = 0.9
      speechSynthesis.cancel()
      speechSynthesis.speak(utterance)
    } catch { /* speech not available */ }
  }

  function playKeyClick() {
    playTone(800, 0.05, 'square')
  }

  function playCorrect() {
    playTone(523, 0.15)
    setTimeout(() => playTone(659, 0.15), 150)
    setTimeout(() => playTone(784, 0.3), 300)
  }

  function playWrong() {
    playTone(200, 0.3, 'sawtooth')
  }

  function playWin() {
    const notes = [523, 587, 659, 784, 880, 1047]
    notes.forEach((freq, i) => {
      setTimeout(() => playTone(freq, 0.2), i * 120)
    })
  }

  function playLose() {
    playTone(400, 0.3, 'sawtooth')
    setTimeout(() => playTone(300, 0.4, 'sawtooth'), 300)
  }

  return { speakWord, playKeyClick, playCorrect, playWrong, playWin, playLose }
}
