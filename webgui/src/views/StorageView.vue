<script setup lang="ts">
import Menu from "../components/Menu.vue"

import { computed, reactive, ref } from "@vue/reactivity";
import { useStore } from "@/stores/store";
import CollectionList from "@/components/CollectionList.vue";
import TimeWindowStorage from "@/components/TimeWindowStorage.vue";
import Dropdown from "@/components/Dropdown.vue";
import Exporter from "@/components/Exporter.vue";
import CountResult from "@/components/CountResult.vue";
import StorageError from "@/components/storage/StorageError.vue";
import DataView from "@/components/DataView.vue";
import type { CollectionQuery, ViewQuery, ViewResult } from "@/api/types";
import QueryInput from "@/components/storage/QueryInput.vue";
import * as storage_api from '@/api/storage'

const store = useStore()
const viewResult = <ViewResult>reactive({})


function discover(query: ViewQuery) {
    storage_api.viewMedia(query).then(res => {
        Object.assign(viewResult, res)
    })
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
                <QueryInput @discover="discover"/>
            </div>
        </div>
        <div class="row mt-2">
            <div class="col">
                <!-- <CountResult /> -->
                <!-- <StorageError /> -->
            </div>
            <div class="col-6">
                <!-- <Exporter /> -->
            </div>
            
        </div>
        <hr />
        <div class="row mt-3">
            <div class="col">
                <DataView v-if="viewResult.view" :data-view="viewResult"/>
            </div>
        </div>
    </div>
</template>