<script setup lang="ts">

import type {CollectionDescription, CollectionQuery, TimeWindow, ViewQuery} from '@/api/types'
import { computed, reactive, ref, watch } from 'vue';
import CollectionList from '../CollectionList.vue';
import Dropdown from '../Dropdown.vue';
import TimeWindowStorage from '../TimeWindowStorage.vue';
import {useStorageStore} from '@/stores/storageStore'
import CollectionSelection from '../CollectionSelection.vue';
import type { RuleInfo } from '@/api/collector';
import { useStore } from '@/stores/store';
import CollectionEditor from './CollectionEditor.vue';
import { storeToRefs } from 'pinia';
import * as storage_api from '@/api/storage'

const emits = defineEmits(['discover'])

const storageStore = useStorageStore()
const collectorStore = useStore()

const timeWindow = reactive(<TimeWindow>{})

const query = reactive({ 
    collection: <CollectionDescription>{}
})

const viewTypes = ['tweets', 'medias', 'users']
const selectedViewType = ref('')

const orderTypes = ['No Order', 'ascending', 'descending']
const selectedOrderType = ref('')

const editCollection = ref(false)
const actualQuery = computed(() => {
    let q: CollectionQuery = {}
    q.rule_ids = query.collection.rule_ids
    q.date_from = timeWindow.start_date
    q.date_to = timeWindow.end_date
    q.order = selectedOrderType.value == 'ascending' ? 1 : selectedOrderType.value == 'descending' ? -1 : 0

    let viewQuery: ViewQuery = {collection: q, view_type: selectedViewType.value}
    return viewQuery
})

function createAndSelectCollection() {
    let res = storageStore.createLocalCollection()
    query.collection = res
}

function startEdit() {
    console.log(query)
    editCollection.value = true
}

function saveLocal() {
    editCollection.value = false
    storageStore.updateLocalCollection()
}

function discover() {
    emits('discover', actualQuery.value)
}

const collectionName = computed(() => query.collection.name)
watch(collectionName, () => {
    editCollection.value = false
})

</script>

<template>
    <div class="input-group">
        <CollectionList 
            :collections="storageStore.collections" 
            v-model:selectedCollection="query.collection"
            @createCollection="createAndSelectCollection"
            @deleteCollection="storageStore.deleteLocalCollection"
            @edit="startEdit"/>
        <!-- <label class="input-group-text" style="width: 42px;"></label> -->
        <Dropdown :options="viewTypes" v-model="selectedViewType" width="100"/>
        <!-- <label class="input-group-text" style="width: 42px;"></label> -->
        <div class="ms-2"></div>
        <TimeWindowStorage :time_window="timeWindow" :edit="true"/>
        <Dropdown :options="orderTypes" v-model="selectedOrderType" width="120"/>
        <button class="btn btn-primary ms-2">Count</button>
        <button class="btn btn-primary ms-2" @click="discover">Discover</button>
    </div>
    <div class="card mt-3" v-if="editCollection">
        <div class="card-body">
            <CollectionEditor :collection="query.collection" @save="saveLocal"/>
        </div>
    </div>
    
</template>