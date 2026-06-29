<template>
  <div class="min-h-screen bg-wordle-bg dark:bg-wordle-darkBg transition-colors">
    <header class="bg-white dark:bg-gray-900 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div class="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
        <router-link to="/" class="text-xl font-bold text-gray-800 dark:text-white">
          Wordle Game
        </router-link>
        <nav class="flex gap-4">
          <router-link to="/" class="text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white">首页</router-link>
          <router-link to="/stats" class="text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white">统计</router-link>
          <router-link to="/settings" class="text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white">设置</router-link>
        </nav>
      </div>
    </header>
    <main class="max-w-7xl mx-auto px-4 py-6">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import { onMounted } from 'vue'

const userStore = useUserStore()

onMounted(() => {
  // Check dark mode preference
  if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    document.documentElement.classList.add('dark')
  }
})
</script>