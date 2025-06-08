<script setup>
import StateButton from "@/common/StateButton.vue";
import { useDate } from "@/composables/useDate";
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import api from "@/utils/axios";
import { useAuthStore } from "@/store/auth";

const props = defineProps({
  data: {
    type: Object,
    required: true,
  },
});

const { formatDate } = useDate();
const date = computed(() => formatDate(props.data.write_date ?? ""));

const likeCount = computed(() => props.data.article_interaction?.likes ?? 0);
const readCount = computed(() => props.data.article_interaction?.read ?? 0);
const keywords = computed(() => props.data.keywords ?? []);
const content = computed(() => props.data.content ?? "내용이 없습니다");

const router = useRouter();
const authStore = useAuthStore();
const isPosting = ref(false);

const handleClick = async () => {
  if (isPosting.value) return;
  isPosting.value = true;

  try {
    const config = authStore.accessToken
      ? {
          headers: {
            Authorization: `Bearer ${authStore.accessToken}`,
          },
        }
      : {};
    await api.post(`/api/v1/interaction/view/${props.data.id}/`, null, config);
  } catch (error) {
    console.error("조회수 등록 실패:", error);
  } finally {
    router.push({ name: "newsDetail", params: { id: props.data.id } });
    isPosting.value = false;
  }
};
</script>

<template>
  <div class="card">
    <div class="card__header">
      <StateButton type="state" size="sm" disabled>
        {{ props.data.category }}
      </StateButton>
      <span class="card__header-item">{{ props.data.writer }}</span>
      <span class="card__header-item">· {{ date }}</span>
    </div>

    <div @click="handleClick" style="cursor: pointer">
      <h2 class="title">{{ props.data.title }}</h2>
      <p class="description">{{ content }}</p>
    </div>

    <div class="stats">
      <span>❤️ {{ likeCount }}</span>
      <span>👀 {{ readCount }}</span>
      <a :href="props.data.url" target="_blank">📄</a>
    </div>

    <div class="tags" v-if="keywords.length > 0">
      <StateButton
        v-for="(tag, index) in keywords"
        :key="index"
        type="tag"
        size="sm"
      >
        #{{ tag }}
      </StateButton>
    </div>
  </div>
</template>

<style scoped lang="scss">
.card {
  background-color: white;
  width: 100%;
  padding: 24px 0;
  border-bottom: 1px solid #e7e6e6;

  &__header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.9rem;
    color: #888;

    &-item {
      font-weight: normal;
    }
  }

  .title {
    margin: 12px 0;
    font-size: 22px;
    font-weight: bold;
    color: #1c1c1e;
  }

  .description {
    font-size: 1rem;
    color: var(--c-gray-600);
    margin: 15px 0;
    display: -webkit-box;
    -webkit-line-clamp: 4;
    line-clamp: 4;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
    line-height: 1.5;
  }

  .stats {
    display: flex;
    gap: 15px;
    font-size: 0.9rem;
    color: var(--c-gray-500);
    margin-bottom: 12px;
    align-items: center;
  }

  .tags {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 0;
  }
}
</style>
