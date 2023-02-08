<script setup lang="ts">
import FieldSelection from './FieldSelection.vue';
import type { ViewResult } from '@/api/types'
import { reactive } from 'vue';
import DataTable from './DataTable.vue';

const props = defineProps({
    dataView: { type: Object as () => ViewResult, required: true}
})

const selectedFields: Array<string> = reactive([])

</script>

<template>
   <div class="row" v-if="dataView.view">
        <div class="col-3">
            <FieldSelection :selected-fields="selectedFields" :possible-fields="dataView.fields" :default-fields="dataView.default_fields"/>
        </div>
        <div class="col-9">
            <DataTable :data="props.dataView.view" :fields="selectedFields"/>
        </div>
   </div>
</template>