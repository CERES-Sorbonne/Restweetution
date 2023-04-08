<script setup lang="ts">
import FieldSelection from '../../FieldSelection.vue';
import type { ViewResult } from '@/api/types'
import { reactive } from 'vue';
import DataTable from '../../DataTable.vue';

const props = defineProps({
    dataView: { type: Object as () => ViewResult, required: true},
    selectedFields: {
        type: Array<string>,
        required: true
    }
})
</script>

<template>
   <div class="row" v-if="dataView.view">
        <div class="col-2">
            <FieldSelection :selected-fields="props.selectedFields" :possible-fields="dataView.fields" :default-fields="dataView.default_fields"/>
        </div>
        <div class="col-10">
            <DataTable :data="props.dataView.view" :fields="selectedFields"/>
        </div>
   </div>
</template>