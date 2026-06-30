<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 flex flex-col h-full">
    <h3 class="font-semibold mb-3 text-gray-700 dark:text-gray-200">Chat</h3>

    <!-- Messages -->
    <div ref="msgListRef" class="flex-1 overflow-y-auto space-y-2 mb-3 text-sm min-h-[12rem] max-h-80 scroll-smooth">
      <div v-if="messages.length === 0" class="text-center text-gray-400 py-8">No messages yet</div>
      <div
        v-for="msg in messages"
        :key="msg.id"
        class="p-2 rounded-lg leading-relaxed"
        :class="{
          'bg-yellow-50 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-200': msg.type === 'system',
          'bg-gray-50 dark:bg-gray-700/50 text-gray-700 dark:text-gray-200': msg.type !== 'system',
        }"
      >
        <!-- System message -->
        <template v-if="msg.type === 'system'">
          <span class="text-xs">{{ msg.content }}</span>
        </template>
        <!-- Chat message -->
        <template v-else>
          <span class="font-semibold text-gray-800 dark:text-gray-100">{{ msg.nickname || 'Unknown' }}:</span>
          <span class="ml-1 text-gray-600 dark:text-gray-300">{{ msg.content }}</span>
        </template>
      </div>
    </div>

    <!-- Input -->
    <div class="flex gap-2">
      <input
        v-model="inputText"
        :placeholder="placeholder"
        class="flex-1 px-3 py-1.5 border border-gray-300 dark:border-gray-600 rounded-lg text-sm dark:bg-gray-700 dark:text-gray-200 outline-none focus:ring-2 focus:ring-blue-400"
        @keyup.enter="send"
        :disabled="!canSend"
      />
      <button
        @click="send"
        :disabled="!canSend || !inputText.trim()"
        class="bg-blue-500 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-blue-600 disabled:opacity-50"
      >
        Send
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'

export interface ChatMessage {
  id: number
  type?: string
  userId?: string
  nickname?: string
  content: string
}

const props = defineProps<{
  messages: ChatMessage[]
  canSend?: boolean
  placeholder?: string
}>()

const emit = defineEmits<{
  (e: 'send', text: string): void
}>()

const inputText = ref('')
const msgListRef = ref<HTMLElement>()

function send() {
  if (!inputText.value.trim() || !props.canSend) return
  emit('send', inputText.value.trim())
  inputText.value = ''
}

// Auto-scroll when new messages arrive
watch(() => props.messages.length, async () => {
  await nextTick()
  if (msgListRef.value) {
    msgListRef.value.scrollTop = msgListRef.value.scrollHeight
  }
})
</script>
