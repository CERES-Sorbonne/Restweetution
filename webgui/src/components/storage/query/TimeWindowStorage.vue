<script setup lang="ts">

import type { TimeWindow } from '@/api/types';
import { toDatetimeInputString } from '@/utils';
import { computed, reactive, ref } from '@vue/reactivity';

const props = defineProps({
    time_window: { type: Object as () => TimeWindow, required: true},
    edit: Boolean
})

const setStart = computed(() => props.time_window.start != undefined)
const setEnd = computed(() => props.time_window.end != undefined)


function initStart() {
    let start = new Date()
    start.setDate(start.getDate() - 6)
    props.time_window.start = toDatetimeInputString(start)
}

function initEnd() {
    let end = new Date()
    props.time_window.end = toDatetimeInputString(end)
}

</script>

<template >
    <button :disabled="!edit" class="btn btn-outline-primary dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">From</button>
    <ul class="dropdown-menu">
        <li><a class="dropdown-item" href="#" @click="props.time_window.start = undefined">Default</a></li>
        <li><a class="dropdown-item" href="#" @click="initStart">Date</a></li>
    </ul>
    <input v-if="setStart" :disabled="(!edit || !setStart)" type="datetime-local" aria-label="First name" class="form-control " v-model="props.time_window.start">
    <input v-else :disabled="true" type="text" class="form-control bg-white" value="Oldest"/>
    <button :disabled="!edit" class="btn btn-outline-primary dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">To</button>
    <ul class="dropdown-menu">
        <li><a class="dropdown-item" @click="props.time_window.end = undefined" href="#">Default</a></li>
        <li><a class="dropdown-item" @click="initEnd" href="#">Date</a></li>
    </ul>
    <input v-if="setEnd" :disabled="(!edit || !setEnd)" type="datetime-local" class="form-control" v-model="props.time_window.end">
    <input v-else :disabled="true" type="text" class="form-control bg-white" value="Now"/>
</template>