<script setup lang="ts">

import { toDatetimeInputString } from '@/utils';
import { computed, reactive, ref } from '@vue/reactivity';
import { onMounted, watch } from 'vue';

const emits = defineEmits(["submit"]);

const props = defineProps({
    time_window: { type: Object, required: true},
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
    <div>
        <div class="input-group mb-3">
            <button :disabled="!edit" class="btn btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">From</button>
            <ul class="dropdown-menu">
                <li><a class="dropdown-item" href="#" @click="props.time_window.start = undefined">Default</a></li>
                <li><a class="dropdown-item" href="#" @click="initStart">Date</a></li>
            </ul>
            <input v-if="setStart" :disabled="(!edit || !setStart)" type="datetime-local" aria-label="First name" class="form-control " v-model="props.time_window.start">
            <input v-else :disabled="true" type="text" class="form-control" :value="props.time_window.recent ? '1 Week Ago' : '1 Month Ago'"/>
            <button :disabled="!edit" class="btn btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">To</button>
            <ul class="dropdown-menu">
                <li><a class="dropdown-item" @click="props.time_window.end = undefined" href="#">Default</a></li>
                <li><a class="dropdown-item" @click="initEnd" href="#">Date</a></li>
            </ul>
            <input v-if="setEnd" :disabled="(!edit || !setEnd)" type="datetime-local" class="form-control" v-model="props.time_window.end">
            <input v-else :disabled="true" type="text" class="form-control" value="Now"/>

            <button class="btn btn-outline-secondary dropdown-toggle" :disabled="!edit" type="button" data-bs-toggle="dropdown" aria-expanded="false">{{ props.time_window.recent ? 'Recent': 'Full Search' }}</button>
            <ul class="dropdown-menu dropdown-menu-end">
                <li><a class="dropdown-item" href="#" @click="props.time_window.recent = true">Recent</a></li>
                <li><a class="dropdown-item" href="#" @click="props.time_window.recent = false">Full Search</a></li>
            </ul>

        </div>
    </div>

</template>