<script setup lang="ts">

import { computed } from '@vue/reactivity';
import { onMounted, watch } from 'vue';

const props = defineProps({
    possibleFields: {
        type: Array<string>,
        required: true
    },
    defaultFields: {
        type: Array<string>
    },
    selectedFields: {
        type: Array<string>,
        required: true
    }
})

const hasDefault = computed(() => props.defaultFields && props.defaultFields.length > 0)


function check(field: string) {
    if (props.selectedFields.includes(field)) {
        let index = props.selectedFields.indexOf(field)
        props.selectedFields.splice(index, 1)
    }
    else {
        props.selectedFields.push(field)
    }
}

function checkAll() {
    props.selectedFields.length = 0
    props.selectedFields.push(...props.possibleFields)
}

function checkNone() {
    props.selectedFields.length = 0
}

function checkDefault() {
    checkNone()
    if (props.defaultFields) {
        props.selectedFields.push(...props.defaultFields)
    }
}

onMounted(() => {
    if (hasDefault.value) {
        checkDefault()
    }
    else {
        checkAll()
    }
})

watch(() => props.possibleFields, () => {
    if (props.selectedFields.length == 0 || props.selectedFields.some(f => !props.possibleFields.includes(f))) {
        if (hasDefault.value) {
            checkDefault()
        }
        else {
            checkAll()
        }
    }
})

</script>

<template>
    <ul class="list-group small">
        <div class="input-group mb-2">
            <button @click="checkAll" class="btn btn-outline-dark form-control btn-sm">All</button>
            <button @click="checkDefault" v-if="hasDefault"
                class="btn btn-outline-dark form-control btn-sm">Default</button>
            <button @click="checkNone" class="btn btn-outline-dark form-control btn-sm">None</button>
        </div>
        <li v-for="field in possibleFields" class="list-group-item">
            <input class="form-check-input me-1" type="checkbox" :checked="props.selectedFields.includes(field)"
                @click="check(field)">
            {{ field }}
        </li>
    </ul>
</template>