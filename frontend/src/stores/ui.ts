import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useUiStore = defineStore('ui', () => {
  const darkMode = ref(false)
  const language = ref('zh')

  // Apply dark mode class on initial load and changes
  watch(darkMode, (val) => {
    if (val) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, { immediate: true })

  watch(language, () => {
    // language change placeholder for future i18n
  })

  function toggleDark() {
    darkMode.value = !darkMode.value
  }

  return { darkMode, language, toggleDark }
}, {
  persist: {
    key: 'wordle_ui_store',
    storage: localStorage,
    pick: ['darkMode', 'language'],
  },
})