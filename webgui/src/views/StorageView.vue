<script setup lang="ts">
import Menu from "../components/Menu.vue"

import { computed, reactive, ref } from "@vue/reactivity";
import { useStore } from "@/stores/store";
import Exporter from "@/components/Exporter.vue";
import CountView from "@/components/CountResult.vue";
import DataView from "@/components/storage/discover/DataView.vue";
import type { ViewQuery, ViewResult } from "@/api/types";
import QueryInput from "@/components/storage/query/QueryInput.vue";
import * as storage_api from '@/api/storage'

import Paginator from '@/components/storage/discover/Paginator.vue'

interface StorageResult { query?: ViewQuery, view?: ViewResult, count?: number}

const store = useStore()

const query = reactive({}) as ViewQuery
const storageResult = reactive({}) as StorageResult
const selectedFields: string[] = reactive([]) 

const hasCount = computed(() => storageResult.count && storageResult.count >= 0)
const hasResult = computed(() => storageResult.view)
const showExporter = computed(() => hasResult.value)
const hasCountAndResult = computed(() => hasCount.value && hasResult.value)



function discover(query: ViewQuery) {
    storage_api.getView(query).then(res => {
        storageResult.query = query
        storageResult.view = res
    })
    count(query)
}

function count(query: ViewQuery) {
    return storage_api.getViewCount(query).then((res: number) => {
        console.log(res)
        storageResult.query = query
        storageResult.count = res
    })
}

function setPage(res: ViewResult) {
    storageResult.view = res
}

function reset() {
    storageResult.count = undefined
    storageResult.query = undefined
    storageResult.view = undefined
}

</script>
<template>
    <Menu />
    <div v-if="store.isLoaded">
        <div class="row">
            <!-- <div class="col-2">
                <div class="card">
                    <h2 class="m-3 text-center">Storage</h2>
                </div>
            </div> -->
            <div class="col">
                <QueryInput @discover="discover" @count="count" @reset="reset" @change="q => Object.assign(query, q)"/>
            </div>
        </div>
        <div class="row mt-2">
            <div class="col">
                <CountView :view="storageResult.query.view_type" :count="storageResult.count" v-if="storageResult.count && storageResult.query"/>
                <!-- <StorageError /> -->
            </div>
            <div class="col">
                <Paginator :api-fn="storage_api.getView" :storage-result="storageResult" :page-size=20 v-if="hasCountAndResult && storageResult.count" @on-page="setPage"/>
            </div>
            <div class="col-7">
                <Exporter :query="query" :fields="selectedFields" v-if="showExporter"/>
            </div>
            
        </div>
        <hr />
        <div class="row mt-3">
            <div class="col">
                <DataView v-if="storageResult.view" :data-view="storageResult.view" :selected-fields="selectedFields"/>
            </div>
        </div>
    </div>
</template>