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


watch(setStart, () => {
    if(setStart.value) {
        let start = new Date()
        start.setDate(start.getDate() - 6)
        props.time_window.start = toDatetimeInputString(start)
    }
    else {
        props.time_window.start = undefined
    }
})

watch(setEnd, () => {
    if(setEnd.value) {
        let end = new Date()
        props.time_window.end = toDatetimeInputString(end)
    }
    else {
        props.time_window.end = undefined
    }
})


</script>

<template >
    <div>
        <div class="input-group mb-3">
            <button class="btn btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">From</button>
            <ul class="dropdown-menu">
                <li><a class="dropdown-item" href="#" @click="setStart = false">Oldest</a></li>
                <li><a class="dropdown-item" href="#" @click="setStart = true">Date</a></li>
            </ul>
            <input v-if="setStart" :disabled="(!edit || !setStart)" type="datetime-local" aria-label="First name" class="form-control " v-model="props.time_window.start">
            <input v-else :disabled="true" type="text" class="form-control" value="Oldest"/>
            <button class="btn btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">To</button>
            <ul class="dropdown-menu">
                <li><a class="dropdown-item" @click="setEnd = false" href="#">Now</a></li>
                <li><a class="dropdown-item" @click="setEnd = true" href="#">Date</a></li>
            </ul>
            <input v-if="setEnd" :disabled="(!edit || !setEnd)" type="datetime-local" class="form-control" v-model="props.time_window.end">
            <input v-else :disabled="true" type="text" class="form-control" value="Now"/>


            <button class="btn btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">{{ props.time_window.recent ? 'Recent': 'Full Search' }}</button>
            <ul class="dropdown-menu dropdown-menu-end">
                <li><a class="dropdown-item" href="#" @click="props.time_window.recent = true">Recent</a></li>
                <li><a class="dropdown-item" href="#" @click="props.time_window.recent = false">Full Search</a></li>
            </ul>

        </div>
    </div>

</template>