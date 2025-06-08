<script setup>
import { defineProps, useAttrs, computed } from 'vue';

const props = defineProps({
  isActive: Boolean,
  type: {
    type: String,
    default: 'button',
    validator: (value) => ['button', 'state', 'tag'].includes(value),
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md'].includes(value),
  },
});

const attrs = useAttrs();

const classes = computed(() => [
  'btn',
  `btn--${props.type}`,
  `btn--${props.size}`,
  { 'btn--active': props.isActive },
]);
</script>

<template>
  <button :class="classes" v-bind="attrs">
    <slot />
  </button>
</template>

<style scoped lang="scss">
.btn {
  white-space: nowrap;
  border-radius: 10px;
  font-weight: 600;
  transition: background 0.2s, color 0.2s, border 0.2s;
  cursor: pointer;
  border: 1.5px solid #e2e8f0;
  background: #f8fafc;
  color: #222;
  box-shadow: 0 1px 4px 0 rgba(49,130,246,0.03);

  &:hover, &:focus {
    background: #e6f0fa;
    border-color: #3182f6;
    color: #3182f6;
  }

  &--active {
    background: #3182f6;
    color: #fff;
    border-color: #3182f6;
    &:hover {
      background: #2563c6;
    }
  }

  &--sm {
    padding: 6px 14px;
    font-size: 13px;
  }

  &--md {
    padding: 12px 22px;
    font-size: 15px;
  }

  &--tag {
    background: #e6eaf0;
    color: #3182f6;
    border: none;
    cursor: default;
    font-size: 13px;
    padding: 5px 12px;
    &:hover { background: #e6eaf0; }
  }
}
</style>
