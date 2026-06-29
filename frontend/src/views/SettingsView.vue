<template>
  <div class="max-w-xl mx-auto">
    <h1 class="text-3xl font-bold mb-8 text-center">设置</h1>
    
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 space-y-4">
      <div class="flex justify-between items-center">
        <span>暗色模式</span>
        <button @click="toggleDark" class="px-4 py-2 rounded bg-gray-200 dark:bg-gray-600">
          {{ darkMode ? '关闭' : '开启' }}
        </button>
      </div>
      
      <div class="flex justify-between items-center">
        <span>语言</span>
        <select class="px-4 py-2 border rounded dark:bg-gray-700">
          <option>中文</option>
          <option>English</option>
        </select>
      </div>
      
      <div v-if="userStore.token" class="flex justify-between items-center">
        <span>用户</span>
        <button @click="logout" class="px-4 py-2 rounded bg-red-500 text-white hover:bg-red-600">
          退出登录
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const darkMode = ref(document.documentElement.classList.contains('dark'))

function toggleDark() {
  darkMode.value = !darkMode.value
  document.documentElement.classList.toggle('dark')
}

function logout() {
  userStore.logout()
  window.location.href = '/'
}

onMounted(() => {
  darkMode.value = document.documentElement.classList.contains('dark')
})
</script>