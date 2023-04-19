<script setup lang="ts">
import { useStorageStore } from '@/stores/storageStore';
import Progress from './Progress.vue';

const store = useStorageStore()

function pathFolder(path: string) {
    let folder_arr = path.split('/')
    folder_arr.pop()
    let folder = folder_arr.join('/')
    return folder + '/'
}

</script>

<template>
    <div class="text-center">
        <button type="button" @click="store.loadTasks" class="btn btn-outline-primary">Reload</button>
    </div>
    <table class="table">
        <thead>
            <tr>
                <th>Name</th>
                <th>Status</th>
                <th>Key</th>
                <th>Processed</th>
                <th>Link</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="task in store.tasksReversed">
                <td>{{ task.name }}</td>
                <td>{{ task.is_running ? 'Running' : 'Stopped' }}</td>
                <td>{{ task.key }}</td>
                <td>
                    <div>
                        <Progress :total="task.max_progress" :current="task.progress" />
                    </div>
                </td>
                <td v-if="task.result.path" class="">
                    <a :href="task.result.path" class="btn btn-outline-primary"><i class="bi bi-download"></i> Download</a>
                    <a :href="pathFolder(task.result.path)" class="btn btn-outline-primary ms-2"><i
                            class="bi bi-folder2-open"></i>Folder</a>
                </td>
            </tr>
        </tbody>
    </table>
</template>
