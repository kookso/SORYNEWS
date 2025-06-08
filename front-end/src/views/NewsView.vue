<script setup>
defineOptions({ name: "NewsList" });

import { ref, computed, watch, onMounted, nextTick } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "@/utils/axios";
import { useAuthStore } from "@/store/auth";
import { useNewsFilterStore } from "@/store/newsFilter";

import ContentBox from "@/common/ContentBox.vue";
import NewsCard from "@/components/NewsCard.vue";
import { tabs } from "@/assets/data/tabs";
import PaginationButton from "@/common/PaginationButton.vue";
import StateButton from "@/common/StateButton.vue";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const filterStore = useNewsFilterStore();

const newsList = ref([]);
const totalPages = ref(1);
const username = computed(() => authStore.user?.username);
const selectedCategory = computed(() => {
  return tabs.find(tab => tab.id === filterStore.activeTab)?.value || "";
});

const authHeader = computed(() => {
  return authStore.accessToken
    ? {
        Authorization: `Bearer ${authStore.accessToken}`,
      }
    : {};
});

const currentSearch = ref("");

const fetchNews = async () => {
  try {
    const searchQuery = route.query.q;

    if (searchQuery) {
      currentSearch.value = searchQuery;
      const res = await api.get("/api/v1/search/", {
        params: { q: searchQuery },
        headers: authHeader.value,
      });

      newsList.value = [];
      newsList.value = [...(res.data.data ?? [])];
      totalPages.value = 1;
      return;
    }

    if (!authStore.accessToken && filterStore.sortBy === "recommend") {
      filterStore.sortBy = "latest";
    }

    const config = {
      params: {
        sort: filterStore.sortBy,
        page: filterStore.currentPage,
        category: selectedCategory.value,
      },
      headers: authHeader.value,
    };

    const res = await api.get("/api/v1/article/", config);

    newsList.value = [];
    newsList.value = [...(res.data.results ?? [])];
    totalPages.value = res.data.total_pages ?? 1;
  } catch (err) {
    console.error("뉴스 목록 불러오기 실패:", err);
  }
};

const fetchNewsTrigger = () => {
  fetchNews();
};

onMounted(() => {
  nextTick(() => {
    setTimeout(() => {
      window.scrollTo({ top: 0, behavior: "auto" });
    }, 50);
  });

  fetchNewsTrigger();
});

watch(() => filterStore.currentPage, fetchNewsTrigger);
watch(() => filterStore.sortBy, () => {
  filterStore.setPage(1);
  fetchNewsTrigger();
});
watch(() => filterStore.activeTab, () => {
  filterStore.setPage(1);
  fetchNewsTrigger();
});
watch(() => route.query.q, () => {
  filterStore.setPage(1);
  fetchNewsTrigger();
});
</script>

<template>
  <div class="news">
    <div>
      <h1 class="news__title">🤖 AI 맞춤 추천 뉴스</h1>
      <p class="news__description">
        당신이 원하는 뉴스, 이제 AI가 직접 추천해드립니다!<br />
        나만의 취향을 기반으로, 맞춤형 뉴스만 쏙쏙 골라주는<br />
        뉴스 큐레이팅 서비스 <strong>DAESORY NEWS</strong>에 빠져보세요.<br />
        AI 챗봇과 기사에 대해 대화하며 궁금한 점을 물어보고, <br />
        한눈에 보기 쉬운 대시보드를 통해 나의 뉴스 소비 패턴도 확인할 수 있습니다.
      </p>

      <ContentBox class="news__tabs">
        <StateButton
          v-for="tab in tabs"
          :key="tab.id"
          type="state"
          :is-active="filterStore.activeTab === tab.id"
          @click="filterStore.setTab(tab.id)"
        >
          {{ tab.label }}
        </StateButton>
      </ContentBox>
    </div>

    <ContentBox class="news__box">
      <div class="news__box__title-container">
        <div class="news__box__username">
          {{ username ? `${username}님을 위한 뉴스 피드` : "뉴스 피드" }}
        </div>

        <div class="filters__container">
          <select class="filters" v-model="filterStore.sortBy">
            <option value="latest">최신순</option>
            <option v-if="authStore.accessToken" value="recommend">추천순</option>
          </select>
        </div>
      </div>

      <div class="news__box__cards">
        <NewsCard
          v-for="news in newsList"
          :key="`${news.id}-${news.title}`"
          :data="news"
        />
      </div>

      <PaginationButton
        v-if="!route.query.q"
        v-model="filterStore.currentPage"
        :totalPages="totalPages"
      />
    </ContentBox>
  </div>
</template>

<style scoped lang="scss">
.news {
  display: flex;
  flex-direction: column;
  gap: 40px;
  margin: 0 auto 0;
  max-width: 1200px;
  padding: 0 32px;
  background: #f8fafc;

  &__title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #3182f6;
    margin-bottom: 10px;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 14px;
    letter-spacing: -1px;
  }

  &__description {
    font-size: 1.15rem;
    color: #555;
    margin-bottom: 28px;
    line-height: 1.7;
    strong { color: #3182f6; }
  }

  &__tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 14px;
    background: #fff;
    border-radius: 18px;
    padding: 18px 36px;
    box-shadow: 0 2px 12px 0 rgba(0,0,0,0.04);
  }

  &__box {
    background: #fff;
    border-radius: 26px;
    box-shadow: 0 4px 24px 0 rgba(0,0,0,0.07);
    padding: 48px 96px 48px 96px;
    margin-bottom: 28px;

    &__title-container {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 18px;
    }

    &__username {
      font-size: 1.25rem;
      font-weight: 700;
      color: #222;
    }

    .filters__container {
      select.filters {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 10px 18px;
        font-size: 1.05rem;
        background: #f8fafc;
        color: #222;
        transition: border 0.2s;
        &:focus {
          border: 1.5px solid #3182f6;
          outline: none;
        }
      }
    }

    &__cards {
      display: flex;
      flex-direction: column;
    }
  }
}
</style>
