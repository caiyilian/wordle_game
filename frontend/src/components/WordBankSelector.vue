<template>
  <select :value="modelValue" @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
    class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-blue-400 outline-none">
    <option v-for="bank in banks" :key="bank.name" :value="bank.name">
      {{ bank.name }} ({{ bank.word_count ?? '-' }} words)
    </option>
  </select>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

defineProps<{ modelValue: string }>()
defineEmits<{ (e: 'update:modelValue', value: string): void }>()

const banks = ref<Array<{ name: string; word_count: number }>>([
  { name: 'CET4', word_count: 0 },
  { name: 'CET6', word_count: 0 },
  { name: '考研', word_count: 0 },
  { name: 'TOEFL', word_count: 0 },
  { name: 'IELTS', word_count: 0 },
  { name: 'GRE', word_count: 0 },
  { name: 'GMAT', word_count: 0 },
  { name: 'SAT', word_count: 0 },
  { name: '专四', word_count: 0 },
  { name: '专八', word_count: 0 },
])

onMounted(async () => {
  try {
    const resp = await axios.get('/api/wordbanks')
    if (resp.data && Array.isArray(resp.data)) {
      const serverBanks = new Map(resp.data.map((b: any) => [b.name || b.word_bank, b]))
      for (const bank of banks.value) {
        const server = serverBanks.get(bank.name)
        if (server) {
          bank.word_count = server.word_count || server.total || 0
        }
      }
    }
  } catch {
    // silently use defaults
  }
})
</script>
