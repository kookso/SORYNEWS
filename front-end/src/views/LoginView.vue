<script setup>
import { reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  email: '',
  password: '',
})

const error = ref('')

const handleLogin = async () => {
  error.value = ''
  try {
    await authStore.login({ email: form.email, password: form.password })
    router.push('/news')
  } catch (err) {
    error.value = '이메일 또는 비밀번호가 잘못되었습니다.'
    console.error(err)
  }
}

const isFormValid = computed(() => form.email && form.password)
</script>

<template>
  <div class="auth-wrapper">
    <div class="auth-box">
      <h2>로그인</h2>
      <form @submit.prevent="handleLogin">
        <input v-model="form.email" type="email" placeholder="이메일" required />
        <input v-model="form.password" type="password" placeholder="비밀번호" required />
        <button type="submit" :disabled="!isFormValid">로그인</button>
        <p v-if="error" class="error">{{ error }}</p>
      </form>

      <div class="signup-link">
        계정이 없으신가요?
        <router-link to="/register">가입하기</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: #f8fafc;
  display: flex;
  justify-content: center;
  align-items: center;
}

.auth-box {
  background: #fff;
  border-radius: 26px;
  padding: 48px 40px 40px 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 24px 0 rgba(0,0,0,0.07);
  text-align: center;
  border: 1.5px solid #e2e8f0;
}

.auth-box h2 {
  margin-bottom: 28px;
  font-size: 2rem;
  font-weight: 900;
  color: #3182f6;
  letter-spacing: -1px;
}

.auth-box input {
  width: 100%;
  padding: 14px 18px;
  margin-bottom: 18px;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  font-size: 15px;
  outline: none;
  background: #f8fafc;
  transition: border 0.2s;
}

.auth-box input:focus {
  border-color: #3182f6;
}

.auth-box button {
  width: 100%;
  padding: 14px;
  background-color: #3182f6;
  color: white;
  font-weight: 700;
  font-size: 16px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  line-height: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: background-color 0.2s;
  margin-bottom: 8px;
}

.auth-box button:disabled {
  background-color: #b0b0b0;
  cursor: not-allowed;
}

.auth-box button:hover:enabled {
  background-color: #2563c6;
}

.error {
  color: #e74c3c;
  font-size: 15px;
  margin-top: 10px;
  margin-bottom: 0;
}

.signup-link {
  margin-top: 22px;
  font-size: 15px;
  color: #666;

  a {
    margin-left: 5px;
    font-weight: 700;
    color: #3182f6;
    text-decoration: none;
    transition: text-decoration 0.2s;
    &:hover {
      text-decoration: underline;
    }
  }
}
</style>
