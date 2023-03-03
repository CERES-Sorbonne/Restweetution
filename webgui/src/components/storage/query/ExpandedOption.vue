<script setup lang="ts">import { ref } from 'vue';

const emits = defineEmits(['update:modelValue'])

const props = defineProps({
    modelValue: Boolean
})

</script>

<template>
    <button class="btn btn-outline-secondary" :class="props.modelValue ? 'bg-secondary' : ''" @click="$emit('update:modelValue', !props.modelValue)">
        <i v-if="props.modelValue" class="bi bi-arrows-fullscreen text-white"></i>
        <i v-else class="bi bi-box-arrow-in-down-right"></i>
    </button>
</template>