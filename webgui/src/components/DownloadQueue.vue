<script setup lang="ts">
import type { DownloadQueueStatus } from '@/api/collector';
import Progress from './Progress.vue';

const props = defineProps({
    queue: {
        required: true,
        type: Object as () => DownloadQueueStatus
    },
    name: {
        type: String,
        default: 'Queue'
    }
})
</script>

<template>
    <div class="card">
        <div class="card-body">
            <h5 class="text-center">{{ props.name }}</h5>
            <ul class="list-group">
                <li class="list-group-item">In Queue: {{props.queue.qsize}}</li>
                <li class="list-group-item">Current Task: {{props.queue.current_url}}</li>
                <li class="list-group-item" v-if="props.queue.bytes_total > 0"><Progress :current="props.queue.bytes_downloaded" :total="props.queue.bytes_total"/></li>
            </ul>
        </div>
    </div>
</template>