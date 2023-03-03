<script setup lang="ts">

import { toDatetimeInputString } from '@/utils';
import { computed, reactive, ref } from '@vue/reactivity';
import { onMounted, watch } from 'vue';

const emits = defineEmits(["submit"]);

const props = defineProps({
    time_window: { type: Object, required: true},
    edit: Boolean

})

const setStart = ref(false)
const setEnd = ref(false)

const timeWindow: any = reactive({})
const hasTotalCount = computed(() => timeWindow.total_count != -1)
const totalCount = computed(() => hasTotalCount.value ? timeWindow.total_count : '??')
const collectedCount = computed(() => timeWindow.collected_count)
const percentage = computed(() => hasTotalCount.value ? Math.round(collectedCount.value / totalCount.value * 10000) / 100 : 0)
const changed = computed(() => {
    return timeWindow.start != props.time_window.start || timeWindow.end != props.time_window.end || timeWindow.recent != props.time_window.recent
})


function resetEdit() {
    Object.assign(timeWindow, props.time_window)
    
    setStart.value = props.time_window.start != undefined
    setEnd.value = props.time_window.end != undefined
}

function submitEdit() {

    if(props.time_window.start == timeWindow.start && props.time_window.end == timeWindow.end && timeWindow.recent == props.time_window.recent) {
        return
    }

    let window = Object.assign({}, timeWindow)

    // set back to Date format to automatically take care of Timezone informations 
    // that we took out before for the datetime input
    if(window.start) {
        window.start = (new Date(window.start))
    }
    if(window.end) {
        window.end = (new Date(window.end))
    }

    emits('submit' ,window)
}

onMounted(() => {
    resetEdit()
})

watch(props.time_window, resetEdit)
watch(props, () => {
    resetEdit()
    if(!props.edit) {
        submitEdit()
    }
})

watch(setStart, () => {
    if(setStart.value) {
        if(props.time_window.start) {
            timeWindow.start = props.time_window.start
        }
        else {
            let start = new Date()
            start.setDate(start.getDate() - 6)
            timeWindow.start = toDatetimeInputString(start)
        }
    }
    else {
        timeWindow.start = undefined
    }
})

watch(setEnd, () => {
    if(setEnd.value) {
        if(props.time_window.end) {
            timeWindow.end = props.time_window.end
        }
        else {
            let end = new Date()
            timeWindow.end = toDatetimeInputString(end)
        }
    }
    else {
        timeWindow.end = undefined
    }
})


</script>

<template >
    <h5>Time Window ({{timeWindow.recent ? 'Recent' : 'Full Search'}})</h5>
    <div class="pt-2">
        <button v-if="props.edit" :disabled="!changed" @click="resetEdit" type="button" class="btn btn-outline-primary me-1" >Reset</button>
        <span v-if="props.edit" class="form-switch ms-3">
            <input class="form-check-input mt-2" type="checkbox" role="switch" id="flexSwitchCheckDefault" v-model="timeWindow.recent">
            <label class="form-check-label ms-2" for="flexSwitchCheckDefault">Recent</label>
        </span>
    </div>
    <form>        
        <div class="input-group mt-1">
            <span class="input-group-text" style="width: 55px;">From</span>
            <input v-if="setStart" :disabled="(!edit || !setStart)" type="datetime-local" aria-label="First name" class="form-control " v-model="timeWindow.start">
            <input v-else :disabled="true" type="text" class="form-control" value="Oldest"/>
            <span v-if="props.edit" class="form-switch ms-3">
                <input class="form-check-input mt-2" type="checkbox" role="switch" v-model="setStart">
            </span>
        </div>
        <div class="input-group">
            <span class="input-group-text" style="width: 55px;">To</span>
            <input v-if="setEnd" :disabled="(!edit || !setEnd)" type="datetime-local" class="form-control" v-model="timeWindow.end">
            <input v-else :disabled="true" type="text" class="form-control" value="Now"/>
            <span v-if="props.edit" class="form-switch ms-3">
                <input class="form-check-input mt-2" type="checkbox" role="switch" v-model="setEnd">
            </span>
        </div>
    </form>
    <div class="text-center">
        <p class="p-0 m-0">({{percentage}}%) {{collectedCount}} / {{totalCount}}</p>
    </div>
    <div v-if="hasTotalCount" class="progress">
        <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" :aria-valuenow="Math.round(percentage)" aria-valuemin="0" aria-valuemax="100" :style="'width: ' + Math.round(percentage) +'%'"></div>
    </div>

</template>