<script setup>
import { ref } from "vue"
import { RouterLink, useRouter } from "vue-router"
import { useAuthStore } from "@/store/auth"

const router = useRouter()
const authStore = useAuthStore()

const searchQuery = ref("")

const refreshPage = (event) => {
  event.preventDefault()
  router.push("/").then(() => {
    window.location.reload()
  })
}

const handleSearch = () => {
  if (!searchQuery.value.trim()) return
  router.push({ path: "/news", query: { q: searchQuery.value.trim() } })
}

const handleAuthAction = async () => {
  if (authStore.isAuthenticated) {
    await authStore.logout()
    router.push("/")
  } else {
    router.push("/login")
  }
}
</script>

<template>
  <div class="header__container">
    <header>
      <router-link to="/" @click="refreshPage">
        <span class="logo">DAESORY NEWS</span>
      </router-link>

      <div class="header__search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="뉴스를 검색하세요"
          @keyup.enter="handleSearch"
        />
        <button class="search-button" @click="handleSearch">🔍</button>
      </div>

      <nav class="menus">
        <router-link to="/news">나만의 뉴스 큐레이팅</router-link>
        <router-link to="/dashboard">대시보드</router-link>
        <span class="menu-item" @click="handleAuthAction">
          {{ authStore.isAuthenticated ? "로그아웃" : "로그인" }}
        </span>
      </nav>
    </header>
  </div>
</template>

<style scoped lang="scss">
.header__container {
  background: #fff;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.04);
  border-bottom: 1.5px solid #e2e8f0;

  header {
    max-width: 1280px;
    margin: 0 auto;
    height: 84px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 36px;
    gap: 32px;
  }

  .logo {
    font-size: 1.7rem;
    font-weight: 900;
    color: #3182f6;
    letter-spacing: -1px;
    white-space: nowrap;
    transition: color 0.2s;
    &:hover { color: #2563c6; }
  }

  .header__search-box {
    flex: 1;
    max-width: 480px;
    background: #f8fafc;
    border-radius: 16px;
    border: 1.5px solid #e2e8f0;
    box-shadow: 0 2px 8px 0 rgba(49,130,246,0.04);
    display: flex;
    align-items: center;
    position: relative;
    margin: 0 32px;

    input {
      flex: 1;
      border: none;
      outline: none;
      font-size: 16px;
      padding: 14px 44px 14px 20px;
      background: transparent;
      color: #222;
      border-radius: 16px;

      &::placeholder {
        color: #b0b0b0;
      }
    }

    .search-button {
      position: absolute;
      right: 14px;
      background: none;
      border: none;
      font-size: 20px;
      cursor: pointer;
      color: #3182f6;
      transition: color 0.2s;
      &:hover { color: #2563c6; }
    }
  }

  .menus {
    display: flex;
    align-items: center;
    gap: 28px;
    white-space: nowrap;

    a,
    .menu-item {
      font-size: 15px;
      color: #222;
      text-decoration: none;
      cursor: pointer;
      font-weight: 600;
      padding: 8px 18px;
      border-radius: 10px;
      transition: background 0.18s, color 0.18s;

      &:hover, &.router-link-active {
        background: #f0f4fa;
        color: #3182f6;
      }
    }
  }

  @media (max-width: 900px) {
    header {
      flex-wrap: wrap;
      justify-content: center;
      height: auto;
      padding: 0 10px;
      gap: 12px;
    }
    .header__search-box {
      order: 2;
      width: 100%;
      margin: 10px 0;
    }
    .menus {
      order: 3;
      justify-content: center;
      gap: 12px;
    }
    .logo {
      order: 1;
    }
  }
}
</style>

