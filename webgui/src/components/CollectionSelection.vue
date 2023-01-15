<script setup lang="ts">

import { computed } from '@vue/reactivity';
import { useStore } from '@/stores/store'
import RuleSelectionTable from './RuleSelectionTable.vue';
import type { RuleInfo } from '@/api/collector';


const store = useStore()

const emits = defineEmits(['update:selectedRules'])

const props = defineProps({
    selectedRules: {type:Array<RuleInfo>, required: true}
})

const availableRules = computed(() => {
    return store.rulesOrderId.filter(r => !props.selectedRules.some(rule => rule.id == r.id))
})

function selectRule(rule: RuleInfo) {
    props.selectedRules.push(rule)
    emits("update:selectedRules", props.selectedRules)
}

function removeRule(rule: RuleInfo) {
    let index = props.selectedRules.findIndex(r => r.id == rule.id)
    if(index != -1) {
        props.selectedRules.splice(index, 1)
        emits("update:selectedRules", props.selectedRules)
    }
}

</script>

<template>
    <div class="row">
        <div class="col">
            <h5 class="text-center">Available</h5>
            <RuleSelectionTable :rules="availableRules" action-name="add" @select="selectRule"/>
        </div>
        <div class="col">
            <h5 class="text-center">Selected</h5>
            <RuleSelectionTable :rules="props.selectedRules" action-name="del" @select="removeRule"/>
            <h4 v-if="(props.selectedRules.length == 0)" class="text-center">All Rules</h4>

        </div>
    </div>
</template>