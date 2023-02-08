<script setup lang="ts">import { computed, onMounted, ref } from 'vue';

const props = defineProps({
    options: {type: Array<string>, required: true},
    modelValue: {type: String, required: true},
    width: String,
    buttonType: String
})

const emits = defineEmits(['update:modelValue'])

const buttonStyle = computed(() => {
    if(!props.width) {
        return ''
    }
    return 'width: ' + props.width + 'px;'
})

const buttonClass = computed(() => {
    let t = props.buttonType ? props.buttonType : 'outline-primary'
    return 'btn btn-' + t + ' dropdown-toggle'
})

const capitalizedValue = computed(() => props.modelValue.charAt(0).toUpperCase() + props.modelValue.slice(1))


onMounted(() => {
    emits('update:modelValue', props.options[0])
})

</script>

<template>
    <button :class="buttonClass" type="button" data-bs-toggle="dropdown" aria-expanded="false" :style="buttonStyle">{{capitalizedValue}}</button>
        <ul class="dropdown-menu">
            <li v-for="option in props.options">
                <a href="#" class="dropdown-item" aria-current="true" @click="$emit('update:modelValue',option)">{{ option }}</a>
            </li>
        </ul>
</template>