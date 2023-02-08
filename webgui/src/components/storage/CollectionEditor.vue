<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue';
import type { CollectionDescription } from '@/api/types';
import type { RuleInfo } from '@/api/collector';
import { useStore } from '@/stores/store';
import CollectionSelection from '../CollectionSelection.vue';

const props = defineProps({
    collection: {type: Object as () => CollectionDescription, required: true}
})

const emits = defineEmits(['save'])
const store = useStore()

const newName = ref('')
const selectedRules: RuleInfo[] = reactive([])

function reset() {
    if(props.collection.name) {
        newName.value = props.collection.name
    }
    selectedRules.length = 0
    selectedRules.push(...props.collection.rule_ids.map(id => store.ruleFromId[id]))
}

function saveLocal() {
    if(!newName.value) return

    props.collection.name = newName.value
    props.collection.rule_ids.length = 0
    props.collection.rule_ids.push(...selectedRules.map(r => r.id))
    emits('save')
}

watch(props, () => {
    reset()  
})

onMounted(() => {
    reset()
})

</script>

<template>
        <div class="input-group">
            <label class="input-group-text">Collection Name</label>
            <input type="text" v-model="newName" class="form-control" />
            <input type="button" class="ms-2 btn btn-primary" @click="saveLocal" value="Save Local"/>
            <input :disabled="true" type="button" class="ms-2 btn btn-primary" value="Save Global"/>
        </div>
        <div class="mt-3">
            <CollectionSelection :selectedRules="selectedRules"/>
        </div>
</template>