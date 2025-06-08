<script setup>
const props = defineProps({
  modelValue: Number,
  totalPages: Number,
});

const emit = defineEmits(["update:modelValue"]);

function goToPage(page) {
  const isValidPage = page >= 1 && page <= props.totalPages;
  if (!isValidPage || page === props.modelValue) return;

  emit("update:modelValue", page);
  window.scrollTo({ top: 0, behavior: "smooth" });
}
</script>

<template>
  <div class="pagination" v-if="totalPages > 1">
    <button @click="goToPage(modelValue - 1)" :disabled="modelValue === 1">
      이전
    </button>
    <span>{{ modelValue }} / {{ totalPages }}</span>
    <button
      @click="goToPage(modelValue + 1)"
      :disabled="modelValue === totalPages"
    >
      다음
    </button>
  </div>
</template>

<style scoped>
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 28px;
}

.pagination button {
  font-size: 14px;
  padding: 7px 16px;
  border: none;
  background: #3182f6;
  color: white;
  border-radius: 100px;
  font-weight: 600;
  transition: background 0.2s;
  box-shadow: 0 2px 8px 0 rgba(49,130,246,0.08);
}

.pagination button:disabled {
  background: #cccccc;
  color: #fff;
  cursor: not-allowed;
}
</style>
