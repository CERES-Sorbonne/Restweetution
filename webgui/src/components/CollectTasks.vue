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
    download_photo: props.collectTasks.download_photo,
    download_video: props.collectTasks.download_video,
    download_gif: props.collectTasks.download_gif,
    elastic_dashboard: props.collectTasks.elastic_dashboard,
    elastic_dashboard_name: props.collectTasks.elastic_dashboard_name
})

const edit = ref(false)


function submit() {
    emits('submit', editedTasks)
    edit.value = false
}

function reset() {
    editedTasks.download_photo = props.collectTasks.download_photo
    editedTasks.download_video = props.collectTasks.download_video
    editedTasks.download_gif = props.collectTasks.download_gif

    editedTasks.elastic_dashboard = props.collectTasks.elastic_dashboard
    editedTasks.elastic_dashboard_name = props.collectTasks.elastic_dashboard_name

    edit.value = false
}

</script>

<template >
    <h5>Options</h5>
    <ul class="text-start" style="list-style-type:none; padding-left: 0;">
        <li>
            Download Photo:
            <span class="text-success" v-if="props.collectTasks.download_photo">Yes</span>
            <span class="text-warning" v-else>No</span>
            <input class="ms-2" v-if="edit" type="checkbox" v-model="editedTasks.download_photo"/>
        </li>
        <li>
            Download Gif:
            <span class="text-success" v-if="props.collectTasks.download_gif">Yes</span>
            <span class="text-warning" v-else>No</span>
            <input class="ms-2" v-if="edit" type="checkbox" v-model="editedTasks.download_gif"/>
        </li>
        <li>
            Download Video:
            <span class="text-success" v-if="props.collectTasks.download_video">Yes</span>
            <span class="text-warning" v-else>No</span>
            <input class="ms-2" v-if="edit" type="checkbox" v-model="editedTasks.download_video"/>
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