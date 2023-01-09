<script setup lang="ts">

import { toDatetimeInputString } from '@/utils';
import { computed, reactive, ref } from '@vue/reactivity';
import { onMounted, watch } from 'vue';

const props = defineProps({
    start: String,
    end: String,
    edit: { type: Boolean, default: true},
    disabledStartText: {type: String, default: 'Oldest'},
    disabledEndText: {type: String, default: 'Now'}
})

const setStart = ref(true)
const setEnd = ref(true)

function updateSet() {
    setStart.value = props.start != undefined
    setEnd.value = props.end != undefined
}

onMounted(() => {
    updateSet()
})

</script>

<template >
    <form>  
        <div class="input-group mt-1">
            <span class="input-group-text" style="width: 55px;">From</span>
            <input v-if="setStart" :disabled="!edit" type="datetime-local" aria-label="First name" class="form-control " :value="start" @input="$emit('update:start', ($event as any).target.value)">
            <input v-else :disabled="true" type="text" class="form-control" :value="disabledStartText"/>
            <span v-if="props.edit" class="form-switch ms-3">
                <input class="form-check-input mt-2" type="checkbox" role="switch" v-model="setStart">
            </span>
        </div>
        <div class="input-group">
            <span class="input-group-text" style="width: 55px;">To</span>
            <input v-if="setEnd" :disabled="!edit" type="datetime-local" class="form-control" :value="end" @input="$emit('update:end', ($event as any).target.value)">
            <input v-else :disabled="true" type="text" class="form-control" :value="disabledEndText"/>
            <span v-if="props.edit" class="form-switch ms-3">
                <input class="form-check-input mt-2" type="checkbox" role="switch" v-model="setEnd">
            </span>
        </div>
    </form>
</template>