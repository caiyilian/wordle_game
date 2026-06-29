import { ref, onMounted, onUnmounted } from 'vue'

export function useKeyboard(onKey: (key: string) => void) {
  const currentInput = ref('')

  function handleKeydown(e: KeyboardEvent) {
    const key = e.key.toUpperCase()
    if (key === 'BACKSPACE') {
      onKey('BACKSPACE')
    } else if (key === 'ENTER') {
      onKey('ENTER')
    } else if (/^[A-Z]$/.test(key)) {
      onKey(key)
    }
  }

  onMounted(() => window.addEventListener('keydown', handleKeydown))
  onUnmounted(() => window.removeEventListener('keydown', handleKeydown))

  return { currentInput }
}