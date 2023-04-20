<script setup lang="ts">
import { ref, computed } from 'vue';
import type { ViewQuery } from '@/api/types';

const props = defineProps({
    storageResult: {type: Object, required: true},
    apiFn: {type: Function, required: true},
    pageSize: {type: Number, default: 50}
})

const emits = defineEmits(['onPage'])

const page = ref(0)

const maxPages = computed(() => Math.floor(props.storageResult.count / props.pageSize))

function prev() {
    if(page.value < 1) {
        return
    }
    let offset = (page.value -1) * props.pageSize
    let limit = props.pageSize

    let query = JSON.parse(JSON.stringify(props.storageResult.query)) as ViewQuery
    query.collection.offset = offset
    query.collection.limit = limit

    props.apiFn(query).then((res:any) => {
        page.value -= 1
        emits('onPage', res)
    })
}

function next() {
    if(page.value >= maxPages.value) {
        return
    }
    let offset = (page.value + 1) * props.pageSize
    let limit = props.pageSize

    let query = JSON.parse(JSON.stringify(props.storageResult.query)) as ViewQuery
    query.collection.offset = offset
    query.collection.limit = limit

    props.apiFn(query).then((res:any) => {
        page.value += 1
        emits('onPage', res)
    })
}

</script>

<template>
    <div class="input-group">
        <button class="btn btn-outline-primary" @click="prev">Prev</button>
        <label class="form-control bg-white text-center">{{ page + 1 }} / {{ maxPages + 1 }}</label>
        <button class="btn btn-outline-primary" @click="next">Next</button>
    </div>
</template>