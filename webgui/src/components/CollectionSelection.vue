<script setup lang="ts">

import { toDatetimeInputString } from '@/utils';
import { computed, reactive, ref } from '@vue/reactivity';
import { onMounted, watch } from 'vue';
import { useStore, type Rule } from '@/stores/store'
import DateInterval from '@/components/DateInterval.vue'
import RuleSelectionTable from './RuleSelectionTable.vue';
import { propsToAttrMap } from '@vue/shared';


const store = useStore()

const emits = defineEmits(['update:selectedRules'])

const props = defineProps({
    selectedRules: {type:Array<Rule>, required: true}
})

const availableRules = computed(() => {
    return store.rulesOrderId.filter(r => !props.selectedRules.some(rule => rule.id == r.id))
})

function selectRule(rule: Rule) {
    props.selectedRules.push(rule)
    emits("update:selectedRules", props.selectedRules)
}

function removeRule(rule: Rule) {
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