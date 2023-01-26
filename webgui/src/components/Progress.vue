<script setup lang="ts">
import { defineProps, computed } from 'vue';


const props = defineProps({
    total: {type:Number, required: true},
    current: {type:Number, required: true}
})

const totalCount = computed(() => props.total >= 0 ? props.total : '??')
const percentage = computed(() => props.total > 0 ? Math.round(props.current / props.total * 10000) / 100 : 0)


</script>

<template>
    <p class="text-center m-0 p-0">{{ percentage }}%  ({{ current }} / {{ totalCount }})</p>
    <div class="progress">
        <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" :aria-valuenow="Math.round(percentage)" aria-valuemin="0" aria-valuemax="100" :style="'width: ' + Math.round(percentage) +'%'"></div>
    </div>
</template>