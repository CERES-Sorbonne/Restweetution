<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import RuleTable from './RuleTable.vue'
import {useStore} from '@/stores/store'
import { computed } from '@vue/reactivity';
import TimeWindow from './TimeWindow.vue';
import Notifications from './Notifications.vue';
import CollectTasks from './CollectTasks.vue';
import RuleSelectionTable from './RuleSelectionTable.vue';
import type { RuleInfo } from '@/api/collector';

const props = defineProps({
    selectedUser: {type: String, required: true}
})

const store = useStore()

const editRules = ref(false)
const loading = ref(false)

const localActiveRule: RuleInfo | any = reactive({})
const localActiveRuleArray = computed(() => {
    const res = []
    if(Object.keys(localActiveRule).length > 1) {
        res.push(localActiveRule)
    }
    return res
})

const searcher = computed(() => store.searchers[props.selectedUser])
const isLoaded = computed(() => searcher.value != undefined)

const availableRules = computed(() => {
    if(searcher.value && searcher.value.rule) {
        return store.orderedRules.filter((r:any) => r.id != localActiveRule.id)
    }
    return store.orderedRules
})

function triggerStartStop() {
    loading.value = true
    if(searcher.value.running) {
        store.searcherStop(props.selectedUser).then(() => loading.value = false)
    }
    else {
        store.searcherStart(props.selectedUser).then(() => loading.value = false)
    }
}

function delRule() {
    loading.value = true
    store.searcherDelRule(props.selectedUser).
    then(() => loading.value = false).
    catch((e) => {
        loading.value = false
        throw e
    })
}

function submit() {
    loading.value = true
    store.searcherSetRule(props.selectedUser, localActiveRule).
    then(() => loading.value = false)
}

function removeRule() {
    for (var member in localActiveRule) delete localActiveRule[member];
}
function setRule(rule: RuleInfo) {
    removeRule()
    Object.assign(localActiveRule, rule)
}

function setTimeWindow(window: any) {
    loading.value = true
    store.searcherSetTimeWindow(props.selectedUser, window).then(() => loading.value = false)
}

function getRuleFromStore() {
    Object.assign(localActiveRule, store.ruleFromId[searcher.value.rule.id])
}

watch(searcher, () => {
    if(searcher.value.rule.id != localActiveRule.id) {
        getRuleFromStore()
    }
})

watch(editRules, () => {
    if(!editRules.value) {
        submit()
    }
})

onMounted(() => {
    getRuleFromStore()
})

</script>

<template>
    <div v-if="isLoaded">

        <h2 class="text-center pb-4" >Searcher: 
            <span class="text-success" v-if="searcher.running">Collecting <span v-if="searcher.sleeping">(Sleeping)</span></span>
            <span class="text-warning" v-else>Stopped</span>
        </h2>

        <div class="row">
            <div class="col-3">
                <div class="card mb-2">
                    <div class="card-body">
                        <h5 class="text-center">Control</h5>
                        <div class="text-center mb-3 mt-4">
                            <button :disabled="(editRules || loading)" type="button" class="btn btn-primary btn-lg me-2" @click="triggerStartStop">{{searcher.running ? 'Stop' : 'Start'}}</button>
                            <button :disabled="(searcher.running || loading)" type="button" class="btn btn-lg btn-outline-primary" @click="editRules = !editRules"><span v-if="!editRules">Edit</span><span v-if="editRules">Stop Edit</span></button>
                        </div>
                    </div>
                </div>
                <div class="card mb-2">
                    <div class="card-body text-center">
                        <CollectTasks :collect-tasks="searcher.collect_tasks" @submit="(tasks) => store.searcherSetCollectTasks(props.selectedUser, tasks)"/>
                    </div>
                </div>
                <div class="card mb-2">
                    <div class="card-body text-center" style="max-height:300px; overflow: auto;">
                        <Notifications :notifications="store.searcherNotifs"/>
                    </div>
                </div>
            </div>
            <div class="col-9">
                <TimeWindow :time_window="searcher.time_window" :edit="editRules" @submit="setTimeWindow"/>
                <h5 class="text-left">Rule</h5>
                <RuleSelectionTable :show-action="editRules" v-if="localActiveRuleArray.length > 0" action-name="Remove" :loading="loading" :rules="localActiveRuleArray" :selectable="editRules" @select="removeRule" :fields="['id', 'tag', 'query']"/>
                <h5 v-else class="text-center text-warning">
                    No Rule Selected
                    <hr />
                </h5>
                <h5 class="text-center">Available Rules</h5>
                <RuleSelectionTable :show-action="editRules" action-name="Set" :loading="loading" :selectable="editRules" :unique-select="true" :rules="availableRules" @select="setRule" :fields="['id', 'tag', 'query', 'tweet_count']"/>
            </div>
        </div>
    </div>
</template>