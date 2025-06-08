<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import router from "@/router";
import api from "@/utils/axios";

import ContentBox from "@/common/ContentBox.vue";
import StateButton from "@/common/StateButton.vue";
import ArticlePreview from "@/components/ArticlePreview.vue";
import NewsChatbot from "@/components/NewsChatbot.vue";
import { useDate } from "@/composables/useDate";
import { useAuthStore } from "@/store/auth";

const route = useRoute();
const articleId = ref(route.params.id);
const authStore = useAuthStore();
const { formatDate } = useDate();

const news = ref(null);
const relatedNews = ref([]);
const liked = ref(false);
const likeCount = ref(0);
const isAnimating = ref(false);

const authHeader = computed(() => {
  return authStore.accessToken
    ? { Authorization: `Bearer ${authStore.accessToken}` }
    : {};
});

const fetchArticle = async () => {
  window.scrollTo({ top: 0, behavior: "auto" });

  try {
    const [articleRes, relatedRes] = await Promise.all([
      api.get(`/api/v1/article/${articleId.value}/`),
      api.get(`/api/v1/article/${articleId.value}/related/`)
    ]);

    news.value = articleRes.data;
    likeCount.value = articleRes.data.article_interaction.likes;
    relatedNews.value = relatedRes.data;

    if (authStore.accessToken) {
      const likeStatus = await api.get(`/api/v1/interaction/like/${articleId.value}/status/`, {
        headers: authHeader.value,
      });
      liked.value = likeStatus.data.liked;
    }
  } catch (err) {
    console.error("상세 기사 불러오기 실패:", err);
  }
};

onMounted(fetchArticle);

watch(() => route.params.id, (newId) => {
  articleId.value = newId;
  fetchArticle();
});

const toggleLike = async () => {
  try {
    const url = `/api/v1/interaction/like/${articleId.value}/`;
    const method = liked.value ? "put" : "post";

    await api[method](url, null, { headers: authHeader.value });

    liked.value = !liked.value;
    likeCount.value += liked.value ? 1 : -1;

    isAnimating.value = true;
    setTimeout(() => {
      isAnimating.value = false;
    }, 600);
  } catch (err) {
    console.error("좋아요 요청 실패:", err);
  }
};
</script>

<template>
  <div class="news-detail-row">
    <button @click="router.back()" class="back-btn">
      <img src="@/components/icon/LeftArrow.svg" alt="뒤로가기" width="20" />
    </button>
    <div class="news-detail">
      <div class="main-area">
        <ContentBox class="main-content" v-if="news">
          <div class="article__header">
            <StateButton type="state" size="sm" isActive disabled>
              {{ news.category }}
            </StateButton>
            <h2 class="article__header-title">{{ news.title }}</h2>
            <div class="article__header-writer">
              <span>{{ news.writer }}</span>
              <span>🕒 {{ formatDate(news.write_date) }}</span>
            </div>
          </div>

          <p class="article__content">{{ news.content }}</p>

          <div class="article__tags">
            <StateButton
              v-for="(tag, index) in news.keywords"
              :key="index"
              type="tag"
              size="sm"
            >
              #{{ tag }}
            </StateButton>
          </div>

          <div class="article__content__footer">
            <div class="article__content__emoji">
              <span class="emoji-btn">
                <span v-if="liked">❤️</span>
                <span v-else>🤍</span>
                {{ likeCount }}
              </span>
              <div class="emoji-btn">
                <span class="content__emoji-eye">👀</span>
                {{ news.article_interaction.read }}
              </div>
              <a :href="news.url" target="_blank">📄</a>
            </div>

            <button
              v-if="authStore.accessToken"
              class="emoji-btn"
              @click="toggleLike"
            >
              <span>{{ liked ? "❤️" : "🤍" }} 좋아요</span>
            </button>

            <transition name="heart-float">
              <span v-if="isAnimating" class="floating-heart">
                {{ liked ? "❤️" : "🤍" }}
              </span>
            </transition>
          </div>
        </ContentBox>
        <NewsChatbot
          v-if="news"
          :article-id="news.id"
          :title="news.title"
          :write-date="news.write_date"
          :content="news.content"
          class="news-chatbot"
        />
      </div>
      <ContentBox class="sidebar" v-if="news">
        <h1 class="sidebar__title">📰 관련 기사</h1>
        <div
          v-for="(n, index) in relatedNews"
          :key="index"
          class="sidebar__article-wrapper"
        >
          <ArticlePreview :to="`/news/${n.id}`" :news="n" />
        </div>
      </ContentBox>
    </div>
  </div>
</template>

<style scoped lang="scss">
.news-detail-row {
  display: flex;
  flex-direction: column;
  gap: 0;
  margin: 16px auto 0;
  max-width: 1260px;
  padding: 0 32px;
}

.back-btn {
  margin-left: 0;
  margin-bottom: 12px;
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 2px 8px 0 rgba(0,0,0,0.06);
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  cursor: pointer;
  transition: box-shadow 0.2s, background 0.2s;

  &:hover, &:focus {
    background: #f0f4fa;
    box-shadow: 0 6px 28px 0 rgba(49,130,246,0.10);
  }

  img {
    width: 22px;
    height: 22px;
  }
}

.news-detail {
  display: flex;
  align-items: flex-start;
  gap: 40px;
  margin: 0;
  flex: 1;
}

.main-area {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.main-content {
  position: relative;
  background: #fff;
  border-radius: 26px;
  box-shadow: 0 4px 24px 0 rgba(0,0,0,0.07);
  padding: 56px 48px 48px 48px;
  margin-bottom: 0;
}

.main-content .article__header {
  color: #888;
  font-size: 1.05rem;
  margin-bottom: 16px;
}

.main-content .article__header-title {
  margin: 16px 0 16px 0;
  line-height: 1.1;
  font-size: 2rem;
  font-weight: 800;
  color: #1c1c1e;
}

.main-content .article__header-writer {
  display: flex;
  gap: 14px;
  font-size: 1rem;
  color: #666;
}

.main-content .article__content {
  margin: 16px 0;
  line-height: 1.7;
  color: #222;
}

.main-content .article__tags {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 20px;
}

.main-content .article__content__footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 38px;
}

.main-content .article__content__emoji {
  color: #888;
  font-size: 18px;
  display: flex;
  gap: 38px;
  align-items: center;
}

.main-content .article__content__emoji .content__emoji-eye {
  font-size: 19px;
}

.news-chatbot {
  margin-top: 32px;
  background: #fff;
  border-radius: 26px;
  box-shadow: 0 4px 24px 0 rgba(0,0,0,0.07);
  padding: 32px 48px;
}

.sidebar {
  flex: 1;
  background: #fff;
  border-radius: 24px;
  box-shadow: 0 4px 24px 0 rgba(0,0,0,0.07);
  padding: 36px 28px;
  margin-top: 0;
  align-self: flex-start;

  &__title {
    font-weight: 800;
    font-size: 1.3rem;
    margin-bottom: 12px;
    color: #3182f6;
    padding-bottom: 10px;
  }

  &__article-wrapper {
    margin-bottom: 12px;
  }
}

.emoji-btn {
  display: flex;
  align-items: center;
  font-size: 17px;
  color: #888;
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s;
  &:hover { color: #3182f6; }
}

.floating-heart {
  position: absolute;
  font-size: 28px;
  color: red;
  animation: heartFloat 0.6s ease-out forwards;
}

@keyframes heartFloat {
  0% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  50% {
    opacity: 0.8;
    transform: translateY(-20px) scale(1.2);
  }
  100% {
    opacity: 0;
    transform: translateY(-40px) scale(0.8);
  }
}
</style>
