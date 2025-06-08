<script setup>
import { Bar, Doughnut } from "vue-chartjs";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from "chart.js";
import ContentBox from "@/common/ContentBox.vue";
import { ref, onMounted, watch } from "vue";
import ArticlePreview from "@/components/ArticlePreview.vue";
import { useAuthStore } from "@/store/auth";
import api from "@/utils/axios";

ChartJS.register(
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
);

const authStore = useAuthStore();

const categoryColors = ["#FFA07A", "#20B2AA", "#9370DB", "#FFB6C1", "#87CEFA", "#FFD700"];

const sampleCategoryStats = [
  { category: "정치", count: 4 },
  { category: "경제", count: 3 },
  { category: "문화", count: 2 },
];

const sampleKeywords = [
  { keyword: "AI", count: 10 },
  { keyword: "정책", count: 8 },
  { keyword: "청년창업", count: 6 },
  { keyword: "MZ세대", count: 5 },
  { keyword: "우주", count: 3 },
];

const sampleViews = [
  { day: "월", count: 3 },
  { day: "화", count: 5 },
  { day: "수", count: 2 },
  { day: "목", count: 4 },
  { day: "금", count: 1 },
  { day: "토", count: 0 },
  { day: "일", count: 2 },
];

const sampleArticles = [
  {
    id: 1001,
    title: "AI가 바꾸는 미래 사회",
    summary: "인공지능 기술의 발전으로 사회 구조가 어떻게 바뀌고 있는지 분석합니다.",
    category: "기술",
    write_date: "2025-05-20T10:00:00Z",
  },
  {
    id: 1002,
    title: "정책 변화가 청년 창업에 미치는 영향",
    summary: "정부 정책 변화에 따라 청년 창업 생태계에 미치는 영향력을 분석합니다.",
    category: "정책",
    write_date: "2025-05-22T08:30:00Z",
  },
  {
    id: 1003,
    title: "MZ세대, 정치 참여의 새로운 흐름",
    summary: "최근 2030 세대의 정치 참여가 눈에 띄게 증가하고 있습니다.",
    category: "정치",
    write_date: "2025-05-23T14:15:00Z",
  },
];

const fillSampleData = () => {
  categoryData.value.labels = sampleCategoryStats.map((item) => item.category);
  categoryData.value.datasets[0].data = sampleCategoryStats.map((item) => item.count);
  categoryData.value.datasets[0].backgroundColor = sampleCategoryStats.map(
    (_, idx) => categoryColors[idx % categoryColors.length]
  );
  categories.value = sampleCategoryStats.map((item) => [item.category, item.count]);

  keywordData.value.labels = sampleKeywords.map((item) => item.keyword);
  keywordData.value.datasets[0].data = sampleKeywords.map((item) => item.count);

  readData.value.labels = sampleViews.map((item) => item.day);
  readData.value.datasets[0].data = sampleViews.map((item) => item.count);

  favoriteArticles.value = sampleArticles;
};

const categoryData = ref({
  labels: [],
  datasets: [
    {
      data: [],
      backgroundColor: [],
    },
  ],
});

const categories = ref([]);

const keywordData = ref({
  labels: [],
  datasets: [
    {
      label: "키워드 빈도수",
      data: [],
      backgroundColor: "#C7E4B8",
    },
  ],
});

const readData = ref({
  labels: [],
  datasets: [
    {
      label: "주간 조회수",
      data: [],
      backgroundColor: "#DBB8E4",
    },
  ],
});

const favoriteArticles = ref([]);

const options = {
  plugins: {
    legend: {
      display: true,
      position: "right",
      labels: {
        padding: 15,
        boxWidth: 20,
        font: {
          size: 14,
        },
      },
    },
    tooltip: {
      callbacks: {
        label: (context) => {
          const label = context.label || "";
          const value = context.raw;
          return `${label}: ${value}개`;
        },
      },
    },
  },
};

const barOptions = {
  indexAxis: "y",
  scales: { x: { beginAtZero: true } },
  plugins: { legend: { display: false } },
};

const readBarOptions = {
  indexAxis: "x",
  scales: { x: { beginAtZero: true } },
  plugins: { legend: { display: false } },
};

const fetchDashboardData = async () => {
  if (!authStore.accessToken) {
    fillSampleData();  // ← 예시 데이터 넣기
    return;
  }

  try {
    const config = {
      headers: {
        Authorization: `Bearer ${authStore.accessToken}`,
      },
    };

    const { data } = await api.get("/api/v1/dashboard/", config);

    categoryData.value.labels = data.category_stats.map((item) => item.category);
    categoryData.value.datasets[0].data = data.category_stats.map((item) => item.count);
    categoryData.value.datasets[0].backgroundColor = data.category_stats.map(
      (_, idx) => categoryColors[idx % categoryColors.length]
    );
    categories.value = data.category_stats.map((item) => [item.category, item.count]);

    keywordData.value.labels = data.top_keywords.map((item) => item.keyword);
    keywordData.value.datasets[0].data = data.top_keywords.map((item) => item.count);

    readData.value.labels = data.daily_views.map((item) => item.day);
    readData.value.datasets[0].data = data.daily_views.map((item) => item.count);

    favoriteArticles.value = data.liked_articles;
  } catch (err) {
    console.error("대시보드 데이터 불러오기 실패:", err);
  }
};

onMounted(() => {
  fetchDashboardData();
});

watch(() => authStore.accessToken, (newToken, oldToken) => {
  if (newToken !== oldToken) {
    fetchDashboardData();
  }
});
</script>

<template>
  <div class="dashboard">
    <div>
      <h1 class="dashboard__title">📊 DASHBOARD</h1>
      <p class="dashboard__description">
        방문 기록 및 좋아요 데이터를 기반으로 나의 관심 분야를 확인하고,<br />
        관심 분야에 맞는 기사를 추천 받아보세요.<br />
        여러분의 취업 여정의 로드맵을 제공합니다.
      </p>
    </div>

    <div class="dashboard__content">
      <div v-if="!authStore.accessToken" class="overlay">
        <div class="overlay__text">
          로그인 후 대시보드를 이용하실 수 있습니다 😊
        </div>
      </div>

      <div class="dashboard__blur-target" :class="{ blurred: !authStore.accessToken }">
        <div class="dashboard__grid">
          <ContentBox class="category box-spacing">
            <h1>🐤 나의 관심 카테고리</h1>
            <p class="card_description">
              내가 주로 읽은 기사들을 분석하여 정치, 경제, 문화 등 가장 관심 있는
              뉴스 카테고리를 한눈에 보여드립니다.
            </p>
            <div class="category__chart" v-if="categoryData.labels.length">
              <Doughnut :data="categoryData" :options="options" />
              <div class="category__labels">
                <span
                  v-for="(category, index) in categories"
                  :key="index"
                  :style="{
                    borderColor: categoryColors[index],
                    color: categoryColors[index],
                  }"
                  class="category__label"
                >
                  {{ index + 1 }}순위: {{ category[0] }} ({{ category[1] }}개)
                </span>
              </div>
            </div>
            <div v-else class="chart-placeholder">
              <p>데이터를 불러오는 중이거나 표시할 데이터가 없습니다.</p>
            </div>
          </ContentBox>

          <ContentBox class="keyword box-spacing">
            <h1>⭐️ 주요 키워드</h1>
            <p class="card_description">
              내가 관심있게 본 뉴스 기사들에서 가장 많이 등장한 핵심 키워드를
              추출하여 현재 나의 주요 관심사를 보여드립니다.
            </p>
            <div class="chart-container" v-if="keywordData.labels.length">
              <Bar :data="keywordData" :options="barOptions" />
            </div>
            <div v-else class="chart-placeholder">
              <p>데이터를 불러오는 중이거나 표시할 데이터가 없습니다.</p>
            </div>
          </ContentBox>

          <ContentBox class="read box-spacing">
            <h1>📰 주간 읽은 기사</h1>
            <p class="card_description">
              최근 일주일 동안 하루에 몇 개의 기사를 읽었는지 그래프로 확인하며 나의
              뉴스 소비 패턴을 분석합니다.
            </p>
            <div class="chart-container" v-if="readData.labels.length">
              <Bar :data="readData" :options="readBarOptions" />
            </div>
            <div v-else class="chart-placeholder">
              <p>데이터를 불러오는 중이거나 표시할 데이터가 없습니다.</p>
            </div>
          </ContentBox>

          <ContentBox class="like-news box-spacing">
            <h1>❤️ 좋아요 누른 기사</h1>
            <p class="card_description">
              내가 좋아요를 누른 기사들의 목록을 한곳에서 모아보고 다시 찾아볼 수
              있습니다.
            </p>
            <div class="like-news__articles" v-if="favoriteArticles.length">
              <div v-for="(article, index) in favoriteArticles" :key="index">
                <ArticlePreview :to="`/news/${article.id}`" :news="article" />
              </div>
            </div>
            <div v-else class="article-placeholder">
              <p>데이터를 불러오는 중이거나 좋아요 누른 기사가 없습니다.</p>
            </div>
          </ContentBox>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.dashboard {
  display: flex;
  flex-direction: column;
  margin: 0 auto 0;
  max-width: 1200px;
  padding: 0 32px;
  background: #f8fafc;

  @media (max-width: 768px) {
    padding: 0 16px;
    gap: 30px;
  }

  &__title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #3182f6;
    margin-bottom: 10px;
    padding-bottom: 14px;
    border-bottom: 2px solid #e2e8f0;
    letter-spacing: -1px;
  }

  &__description {
    font-size: 1.15rem;
    color: #555;
    line-height: 1.7;
    margin-bottom: 28px;
  }

  &__content {
    position: relative;
    min-height: 600px;
  }

  &__blur-target {
    transition: filter 0.3s ease;

    &.blurred {
      filter: blur(4px);
      pointer-events: none;
      user-select: none;
    }
  }

  &__grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 32px;

    @media (max-width: 768px) {
      grid-template-columns: 1fr;
      gap: 24px;
    }
  }
}

.ContentBox {
  background: #fff;
  border-radius: 26px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.07);
  padding: 40px 32px;
  border: 1.5px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  height: 500px;
  max-height: 500px;
  overflow: hidden;
}

.card_description {
  margin-top: 8px;
  margin-bottom: 16px;
  color: #555;
  line-height: 1.7;
  font-size: 1.15rem;
}

.chart-container,
.category__chart,
.like-news__articles {
  flex-grow: 1;
  overflow-y: auto;
  max-height: 300px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.category__chart {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 24px;

  canvas {
    max-height: 250px;
    max-width: 250px;
  }
}

.category__labels {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 14px;
}

.category__label {
  border: 1.5px solid;
  padding: 4px 8px;
  border-radius: 10px;
  font-size: 1.05rem;
  font-weight: 600;
}

h1 {
  margin-bottom: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #222;
}

.chart-placeholder,
.article-placeholder {
  flex-grow: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #999;
  font-size: 1rem;
  text-align: center;
  padding: 20px;
}

.overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 20;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  pointer-events: none;

  &__text {
    background: #fff;
    padding: 32px 40px;
    border-radius: 26px;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.07);
    font-size: 1.15rem;
    color: #555;
    font-weight: 500;
    white-space: nowrap;
    border: 1.5px solid #e2e8f0;
  }
}
</style>

