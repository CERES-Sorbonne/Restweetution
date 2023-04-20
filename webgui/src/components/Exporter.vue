<script setup lang="ts">
import { useStorageStore } from '@/stores/storageStore';
import { computed, ref } from '@vue/reactivity';
import type { TweetQuery, ExportRequest, ViewQuery } from '@/api/types'
import { onMounted } from 'vue';
import TaskList from './TaskList.vue';


const props = defineProps({
    query: {
        type: Object as () => ViewQuery,
        required: true
    },
    fields: {
        type: Array<string>,
        required: true
    }
})

const selectedExporter = ref('')
const exportSubId = ref('')
const exportId = ref('')
const store = useStorageStore()
const activeSubId = ref(false)

function resetExport() {
    selectedExporter.value = 'csv'
    exportSubId.value = ''
    exportId.value = ''
    activeSubId.value = false
}

const canExport = computed(() => selectedExporter.value != '' && exportId.value.length > 0)

function requestExport() {
    if (exportId.value == '') {
        alert('Export ID cannot be null !  (Index, filename, etc.. depending on exporter )')
        return
    }
    let finalExportId = exportId.value
    if (exportSubId.value != '') {
        finalExportId = exportSubId.value + '/' + exportId.value
    }

    let req: ExportRequest = {
        query: { ...props.query },
        export_type: selectedExporter.value,
        id: finalExportId,
        fields: props.fields
    }

    store.exportTweets(req)
    resetExport()
}

onMounted(() => {
    selectedExporter.value = 'csv'
})

</script>

<template>
    <!-- <div class="row"> -->
    <!-- <div class="col"> -->
    <!-- <form class="row justify-content-md-center"> -->
    <div class="input-group">
        <!-- <label class="input-group-text" for="inputGroupSelect01">Exporter</label> -->
        <select class="form-select" id="inputGroupSelect01" v-model="selectedExporter" style="max-width: 150px;">
            <option value="csv">CSV</option>
            <option value="elastic">Elastic</option>
        </select>
        <template v-if="selectedExporter == 'csv'">
            <div class="input-group-text">File Name</div>
            <input type="text" class="form-control" placeholder="my-file-name" v-model="exportId">
            <button @click="activeSubId = !activeSubId" class="btn btn-outline-secondary" type="button">
                <i v-if="!activeSubId" class="bi bi-folder"></i>
                <i v-else class="bi bi-x"></i>
            </button>
            <input v-if="activeSubId" type="text" class="form-control" placeholder="(Not required)" v-model="exportSubId">
        </template>
        <template v-if="selectedExporter == 'elastic'">
            <div class="input-group-text">Index Name</div>
            <input type="text" class="form-control" placeholder="Index" v-model="exportId">
        </template>
        <button :disabled="!canExport" @click="requestExport" type="button" class="btn btn-primary">Export</button>
        <button class="btn btn-outline-secondary dropdown-toggle ms-2" type="button" data-bs-toggle="dropdown"
            data-bs-auto-close="outside" aria-expanded="false">
            Tasks
        </button>
        <div class="dropdown-menu" style="min-width: 500px;">
            <div class="m-4">
                <TaskList />
            </div>
        </div>
    </div>
    <!-- </form> -->
    <!-- </div> -->
    <!-- </div> --></template>