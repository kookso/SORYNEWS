<script setup>
import { onMounted } from "vue";
import { useRoute } from "vue-router";
import TheHeader from "./components/TheHeader.vue";
import TheFooter from "./components/TheFooter.vue";
import { useAuthStore } from "@/store/auth";

const route = useRoute();
const authStore = useAuthStore();

onMounted(() => {
  authStore.initAuth();
});
</script>

<template>
  <TheHeader v-if="route.path !== '/login' && route.path !== '/register'" />
  <main>
    <RouterView />
  </main>
  <TheFooter v-if="route.path !== '/login' && route.path !== '/register'" />
</template>

<style lang="scss">
main {
  max-width: 1280px;
  min-width: 360px;
  min-height: 100vh;
  margin: 0 auto;
  padding: 50px 15px;
}
</style>
