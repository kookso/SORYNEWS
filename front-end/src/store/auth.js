import { defineStore } from 'pinia'
import axios from '@/utils/axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: null,
    refreshToken: null,
    user: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
  },

  actions: {
    async register({ username, email, password1, password2 }) {
      const response = await axios.post('/api/v1/auth/registration/', {
        username,
        email,
        password1,
        password2,
      })
      return response.data
    },

    async login({ email, password }) {
      const response = await axios.post('/api/v1/auth/login/', {
        email,
        password,
      })

      this.accessToken = response.data.access
      this.refreshToken = response.data.refresh
      this.user = response.data.user || null

      axios.defaults.headers.common['Authorization'] = `Bearer ${this.accessToken}`
    },

    async logout() {
      try {
        await axios.post('/api/v1/auth/logout/')
      } finally {
        this.clearAuth()
      }
    },

    async refreshTokenIfNeeded() {
      if (!this.refreshToken) return

      try {
        const response = await axios.post('/api/v1/auth/token/refresh/', {
          refresh: this.refreshToken,
        })

        this.accessToken = response.data.access
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.accessToken}`
      } catch (error) {
        this.clearAuth()
      }
    },

    clearAuth() {
      this.accessToken = null
      this.refreshToken = null
      this.user = null

      delete axios.defaults.headers.common['Authorization']
    },

    initAuth() {
      if (this.accessToken) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.accessToken}`
      }
    },
  },

  persist: {
    storage: localStorage,
    paths: ['accessToken', 'refreshToken', 'user'],
  },
})
