<script setup lang="ts">
import { useStorageStore } from '@/stores/storageStore';
import { ref } from '@vue/reactivity';
import type { TweetQuery, ExportTweetRequest } from '@/api/types'


const props = defineProps({
    query: {
        type: Object as () => TweetQuery,
        required: true
    },
    count: {
        type: Number,
        required: true
    }
})

const selectedExporter = ref('')
const exportSubId = ref('')
const exportId = ref('')
const store = useStorageStore()

function resetExport() {
    selectedExporter.value = ''
    exportSubId.value = ''
    exportId.value = ''
}

function requestExport() {
    if(exportId.value == '') {
        alert('Export ID cannot be null !  (Index, filename, etc.. depending on exporter )')
        return
    }
    let finalExportId = exportId.value
    if(exportSubId.value != '') {
        finalExportId = exportSubId.value + '/' + exportId.value
    }

    let req: ExportTweetRequest = {
        query: props.query,
        export_type: selectedExporter.value,
        id: finalExportId
    }
    store.exportTweets(req)
    resetExport()
}

</script>

<template>
    <div class="row">
        <div class="col">
            <form class="row justify-content-md-center">
                <div class="col">
                    <div class="card">
                        <div class="card-body pb-0">
                            <ul>
                                <li>
                                    Selected Rules: {{ props.query.rule_ids ?? 'All' }}
                                </li>
                                <li>
                                    Time Window: {{ props.query.date_from ?? 'Oldest' }} to {{ props.query.date_to ?? 'Now' }}
                                </li>
                                <li>
                                    Tweet Count: {{ props.count > -1 ? props.count : 'Unknown' }}
                                </li>
                            </ul>
                        </div>
                    </div>

                    <div class="input-group mt-2 mb-3">
                        <label class="input-group-text" for="inputGroupSelect01">Exporter</label>
                        <select class="form-select" id="inputGroupSelect01" v-model="selectedExporter">
                            <option selected value="''">Select Exporter ...</option>
                            <option value="csv">CSV</option>
                            <option value="elastic">Elastic</option>
                        </select>
                    </div>
                    <div v-if="selectedExporter != ''">
                        <div class="row g-1" v-if="selectedExporter == 'elastic'">
                            <div class="input-group">
                                <div class="input-group-text">Index Name</div>
                                <input type="text" class="form-control" placeholder="Index" v-model="exportId">
                            </div>
                        </div>

                        <div class="row">
                            <div class="input-group" v-if="selectedExporter == 'csv'">
                                <div class="input-group-text">Sub Folder</div>
                                <input type="text" class="form-control" placeholder="(Not required)" v-model="exportSubId">
                                <div class="input-group-text">File Name</div>
                                <input type="text" class="form-control" placeholder="my-file-name" v-model="exportId">
                            </div>
                        </div>
                        
                        <button type="button" class="btn btn-outline-primary mt-2" :disabled="props.count < 1" @click="requestExport">Export</button>
                        <div v-if="props.count < 1" class="text-warning">No tweets to export ...</div>
                    </div>
                </div>
            </form>
        </div>
        <div class="col-3">
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
        </div>
    </div>
    
</template>