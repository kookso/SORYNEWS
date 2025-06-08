<script setup>
import { reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  username: '',
  email: '',
  password1: '',
  password2: '',
})

const error = ref('')

// 회원가입 처리
const handleRegister = async () => {
  if (form.password1 !== form.password2) {
    error.value = '비밀번호가 일치하지 않습니다.'
    return
  }

  try {
    await authStore.register(form)
    router.push('/login')
  } catch (err) {
    error.value = '회원가입에 실패했습니다. 입력 정보를 확인해주세요.'
    console.error(err)
  }
}

const isFormValid = computed(() =>
  form.username && form.email && form.password1 && form.password2
)
</script>

<template>
  <div class="auth-wrapper">
    <div class="auth-box">
      <h2>회원가입</h2>
      <form @submit.prevent="handleRegister">
        <input v-model="form.username" type="text" placeholder="사용자명" required />
        <input v-model="form.email" type="email" placeholder="이메일" required />
        <input v-model="form.password1" type="password" placeholder="비밀번호" required />
        <input v-model="form.password2" type="password" placeholder="비밀번호 확인" required />
        <button type="submit" :disabled="!isFormValid">가입하기</button>
        <p v-if="error" class="error">{{ error }}</p>
      </form>

      <div class="login-link">
        계정이 있으신가요?
        <router-link to="/login">로그인</router-link>
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
  padding: 20px;
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

.login-link {
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
