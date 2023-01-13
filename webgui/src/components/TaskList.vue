<script setup lang="ts">
import { useStorageStore } from '@/stores/storageStore';


const store = useStorageStore()

</script>

<template>
    <div class="text-center">
        <button type="button" @click="store.loadTasks" class="btn btn-outline-primary">Reload</button>
    </div>
    <div v-for="task in store.tasksReversed" class="m-3">
            <ul class="list-group">
                <li class="list-group-item text-center">{{task.name}}</li>
                <li class="list-group-item">Running: {{task.is_running}}</li>
                <li class="list-group-item">Key: {{task.key}}</li>
                <li class="list-group-item">
                    Progress: {{task.progress}}
                    <div class="progress">
                        <div class="progress-bar progress-bar-striped" :class="task.is_running ? ' progress-bar-animated' : ''" role="progressbar" :aria-valuenow="task.progress" aria-valuemin="0" aria-valuemax="100" :style="'width: ' + task.progress +'%'"></div>
                    </div>
                </li>
                <li v-if="task.result.path" class="list-group-item text-break"><a :href="task.result.path">{{task.result.path}}</a></li>
            </ul>
        <div>
        </div>
    </div>
</template>