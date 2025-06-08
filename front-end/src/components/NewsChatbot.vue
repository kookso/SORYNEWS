<script setup>
import { ref, nextTick, computed } from "vue"
import api from "@/utils/axios"
import { useAuthStore } from "@/store/auth"

const props = defineProps({
  articleId: Number,
  title: String,
  writeDate: String,
  content: String,
})

const authStore = useAuthStore()
const question = ref("")
const chatHistory = ref([])
const isLoggedIn = computed(() => !!authStore.accessToken)

const sendQuestion = async () => {
  if (!question.value.trim()) return

  chatHistory.value.push({ role: "user", message: question.value })

  try {
    const config = {
      headers: {
        Authorization: `Bearer ${authStore.accessToken}`,
      },
    }

    const body = {
      article_id: props.articleId,
      title: props.title,
      write_date: props.writeDate,
      content: props.content,
      question: question.value,
    }

    const { data } = await api.post("/api/v1/chat/", body, config)

    chatHistory.value.push({ role: "bot", message: data.response })
  } catch (err) {
    chatHistory.value.push({
      role: "bot",
      message: "❌ 챗봇 응답에 실패했습니다.",
    })
  } finally {
    question.value = ""
    await nextTick()
    scrollToBottom()
  }
}

const scrollToBottom = () => {
  const chatArea = document.querySelector(".chatbot__window")
  if (chatArea) chatArea.scrollTop = chatArea.scrollHeight
}
</script>

<template>
  <div class="chatbot-card">
    <div v-if="!isLoggedIn" class="overlay">
      <div class="overlay__text">
        로그인 후 챗봇을 이용하실 수 있습니다 😊
      </div>
    </div>

    <div :class="{ blurred: !isLoggedIn }" class="chatbot-content-blur-target">
      <div class="chatbot-title-row">
        🤖 <span class="highlight">AI 뉴스비서 뉴비</span>
      </div>
      <p class="chatbot-subtext">뉴비에게 이 기사에 대해 궁금한 점을 자유롭게 물어보세요!</p>

      <div class="chatbot__window">
        <div
          v-for="(chat, index) in chatHistory"
          :key="index"
          :class="['bubble', chat.role]"
        >
          <span>{{ chat.message }}</span>
        </div>
      </div>

      <div class="chatbot__input-box" :class="{ disabled: !isLoggedIn }">
        <input
          v-model="question"
          placeholder="질문을 입력해주세요"
          @keydown.enter="sendQuestion"
          :disabled="!isLoggedIn"
        />
        <button @click="sendQuestion" :disabled="!isLoggedIn">전송</button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.chatbot-card {
  position: relative;
  background-color: #fff;
  border-radius: 26px;
  box-shadow: 0 4px 24px 0 rgba(0,0,0,0.07);
  padding: 40px 48px 32px 48px;
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  border: 1.5px solid #e2e8f0;
}

.chatbot-content-blur-target {
  transition: filter 0.3s ease;
  display: flex;
  flex-direction: column;
  gap: 20px;

  &.blurred {
    filter: blur(4px);
    pointer-events: none;
    user-select: none;
  }
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
  background-color: rgba(255, 255, 255, 0.7);
  pointer-events: auto;
  border-radius: 26px;

  &__text {
    background: #fff;
    padding: 32px 40px;
    border-radius: 20px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    font-size: 1rem;
    color: #333;
    font-weight: 500;
    white-space: nowrap;
    border: 1.5px solid #e2e8f0;
  }
}

.chatbot-title-row {
  font-size: 1.15rem;
  font-weight: 800;
  color: #222;
  display: flex;
  align-items: center;
  gap: 8px;

  .highlight {
    color: #3182f6;
  }
}

.chatbot-subtext {
  font-size: 1rem;
  color: #666;
  margin: 0;
  margin-top: -4px;
}

.chatbot__window {
  max-height: 320px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 18px 6px;
  background: #f8fafc;
  border-radius: 16px;
  border: 1.5px solid #f0f0f0;
}

.bubble {
  max-width: 85%;
  padding: 13px 18px;
  border-radius: 18px;
  white-space: pre-wrap;
  font-size: 15px;
  line-height: 1.7;
  box-shadow: 0 2px 8px 0 rgba(49,130,246,0.04);
}

.bubble.user {
  align-self: flex-end;
  background-color: #3182f6;
  color: white;
  border-top-right-radius: 0;
}

.bubble.bot {
  align-self: flex-start;
  background-color: #f5f7fa;
  color: #222;
  border-top-left-radius: 0;
  border: 1px solid #e2e8f0;
}

.chatbot__input-box {
  display: flex;
  align-items: center;
  gap: 12px;

  &.disabled {
    opacity: 0.6;
    pointer-events: none;
  }

  input {
    flex: 1;
    padding: 14px 18px;
    border-radius: 12px;
    border: 1.5px solid #e2e8f0;
    font-size: 15px;
    outline: none;
    background: #f8fafc;
    transition: border 0.2s;
    &:focus {
      border: 1.5px solid #3182f6;
    }
  }

  button {
    background-color: #3182f6;
    color: white;
    font-weight: 700;
    padding: 12px 22px;
    border-radius: 12px;
    border: none;
    cursor: pointer;
    font-size: 15px;
    transition: background 0.2s;
    &:hover {
      background: #2563c6;
    }
    &:disabled {
       background-color: #b0b0b0;
       cursor: not-allowed;
    }
  }
}
</style>
