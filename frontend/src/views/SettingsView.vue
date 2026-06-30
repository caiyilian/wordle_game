<template>
  <div class="max-w-xl mx-auto">
    <h1 class="text-2xl font-bold mb-6 text-center text-gray-800 dark:text-gray-100">Settings</h1>

    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 space-y-6">
      <!-- Dark Mode -->
      <div class="flex justify-between items-center">
        <div>
          <p class="font-medium text-gray-700 dark:text-gray-200">Dark Mode</p>
          <p class="text-sm text-gray-500">{{ uiStore.darkMode ? 'On' : 'Off' }}</p>
        </div>
        <button @click="uiStore.toggleDark()"
                class="relative w-12 h-6 rounded-full transition-colors"
                :class="uiStore.darkMode ? 'bg-wordle-green' : 'bg-gray-300'">
          <span class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="uiStore.darkMode ? 'translate-x-6' : ''"></span>
        </button>
      </div>

      <!-- Language -->
      <div class="flex justify-between items-center">
        <div>
          <p class="font-medium text-gray-700 dark:text-gray-200">Language</p>
          <p class="text-sm text-gray-500">{{ uiStore.language }}</p>
        </div>
        <select v-model="uiStore.language"
                class="px-3 py-1.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 text-sm">
          <option value="zh">中文</option>
          <option value="en">English</option>
        </select>
      </div>

      <!-- Sound -->
      <div class="flex justify-between items-center">
        <div>
          <p class="font-medium text-gray-700 dark:text-gray-200">Sound Effects</p>
          <p class="text-sm text-gray-500">{{ soundEnabled ? 'On' : 'Off' }}</p>
        </div>
        <button @click="soundEnabled = !soundEnabled"
                class="relative w-12 h-6 rounded-full transition-colors"
                :class="soundEnabled ? 'bg-wordle-green' : 'bg-gray-300'">
          <span class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="soundEnabled ? 'translate-x-6' : ''"></span>
        </button>
      </div>

      <!-- Logout -->
      <div v-if="userStore.token" class="pt-4 border-t border-gray-200 dark:border-gray-700">
        <p class="text-sm text-gray-500 mb-2">Logged in as <strong>{{ userStore.user?.nickname }}</strong></p>
        <button @click="logout" class="w-full bg-red-500 text-white py-2 rounded-lg hover:bg-red-600 font-medium">
          Logout
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useUserStore } from '@/stores/user'
import { useUiStore } from '@/stores/ui'

const userStore = useUserStore()
const uiStore = useUiStore()

const soundEnabled = ref(localStorage.getItem('wordle_sound') !== 'false')

import { watch } from 'vue'
watch(soundEnabled, (val) => localStorage.setItem('wordle_sound', String(val)))

function logout() {
  userStore.logout()
  window.location.href = '/'
}
</script>