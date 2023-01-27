<script setup lang="ts">
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'
import { reactive } from 'vue'
import { Colors } from 'chart.js';
import type { CountPoint } from '@/api/collector';
import { computed } from '@vue/reactivity';

ChartJS.register(Colors);
 
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const props = defineProps({
    points: {
        type: Array<CountPoint>,
        required: true
    }
})

const data = computed(() => {
    return {
        labels : props.points.map(p => p.date.split('T')[0]),
        datasets: [{
            data: props.points.map(p => p.count),
            label: 'tweets'
        }]
    }
})

const chartOptions = reactive({
    responsive: true,
})
</script>

<template>
  <Bar
    id="my-chart-id"
    :options="chartOptions"
    :data="data"
  />
</template>