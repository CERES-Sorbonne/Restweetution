<script setup lang="ts">

import { toDatetimeInputString } from '@/utils';
import { computed, reactive, ref } from '@vue/reactivity';
import { onMounted, watch } from 'vue';
import type { CollectTasks } from '@/stores/store'

const emits = defineEmits(["submit"]);

const props = defineProps({
    collectTasks: { type: Object as () => CollectTasks, required: true},
})

const editedTasks: CollectTasks = reactive({
    download_media: props.collectTasks.download_media,
    elastic_dashboard: props.collectTasks.elastic_dashboard,
    elastic_dashboard_name: props.collectTasks.elastic_dashboard_name
})

const edit = ref(false)


function submit() {
    emits('submit', editedTasks)
    edit.value = false
}

function reset() {
    editedTasks.download_media = props.collectTasks.download_media,
    editedTasks.elastic_dashboard = props.collectTasks.elastic_dashboard
    editedTasks.elastic_dashboard_name = props.collectTasks.elastic_dashboard_name
    edit.value = false
}

</script>

<template >
    <h5>Collected Tasks</h5>
    <ul style="list-style-type:none; padding-left: 0;">
        <li>
            Media Download:
            <span class="text-success" v-if="props.collectTasks.download_media">Yes</span>
            <span class="text-warning" v-else>No</span>
            <input class="ms-2" v-if="edit" type="checkbox" v-model="editedTasks.download_media"/>
        </li>
        <li>
            Elastic Dashboard: 
            <span class="text-success" v-if="props.collectTasks.elastic_dashboard">Yes</span>
            <span class="text-warning" v-else>No</span>
            <input v-if="edit" class="ms-2" type="checkbox" v-model="editedTasks.elastic_dashboard"/>
            <input v-if="edit && editedTasks.elastic_dashboard" type="text" placeholder="Dashboard Name" class="form-control" v-model="editedTasks.elastic_dashboard_name"/>
        </li>
    </ul>
    <div>
        <button type="button" class="btn btn-primary" @click="(edit = true)" v-if="!edit">Edit</button>
        <button type="button" class="btn btn-primary me-1" @click="reset" v-if="edit">Cancel</button>
        <button type="button" class="btn btn-primary" @click="submit" v-if="edit">Submit</button>
    </div>
    
</template>