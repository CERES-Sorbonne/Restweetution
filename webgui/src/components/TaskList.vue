<script setup lang="ts">
import { useStorageStore } from '@/stores/storageStore';

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
    <div class="row">
        <div v-for="task in store.tasksReversed" class="col-3 m-3">
                <ul class="list-group">
                    <li class="list-group-item text-center">{{task.name}}</li>
                    <li class="list-group-item">Running: {{task.is_running}}</li>
                    <li class="list-group-item">Key: {{task.key}}</li>
                    <li class="list-group-item">
                        Progress: {{task.progress}}
                        <div class="progress">
                            <div class="progress-bar progress-bar-striped" :class="task.is_running ? ' progress-bar-animated' : '' + (Number(task.progress == 100) ? 'bg_success' : '')" role="progressbar" :aria-valuenow="task.progress" aria-valuemin="0" aria-valuemax="100" :style="'width: ' + task.progress +'%'">
                            </div>
                        
                        </div>
                    </li>
                    <li v-if="task.result.path" class="list-group-item text-break">
                        <a :href="task.result.path" class="btn btn-outline-primary" ><i class="bi bi-download"></i> Download</a>
                        <a :href="pathFolder(task.result.path)" class="btn btn-outline-primary ms-2" ><i class="bi bi-folder2-open"></i>Folder</a>
                    </li>
                </ul>
            <div>
            </div>
        </div>
    </div>
</template>
