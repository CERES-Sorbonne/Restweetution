<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import {useStore} from '@/stores/store'
import { computed } from '@vue/reactivity';
import TimeWindow2 from './TimeWindow2.vue';
import Notifications from './Notifications.vue';
import CollectTasks from './CollectTasks.vue';
import RuleSelectionTable from './RuleSelectionTable.vue';
import type { RuleInfo } from '@/api/collector';
import Progress from '@/components/Progress.vue'

const props = defineProps({
    selectedUser: {type: String, required: true}
})

const store = useStore()

const editRules = ref(false)
const loading = ref(false)
const showQuery = ref(false)

const localActiveRule: RuleInfo | any = reactive({id: undefined, query: undefined, tag:undefined})
const hasRule = computed(() => localActiveRule.id != undefined)

const searcher = computed(() => store.searchers[props.selectedUser])
const isLoaded = computed(() => searcher.value != undefined && store.isLoaded)

const timeWindow = reactive({start: undefined, end: undefined, recent: true})

const hasTotalCount = computed(() => searcher.value.time_window.total_count >= 0)
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

function triggerEdit() {
    if(editRules.value) {
        submit()
        editRules.value = false
    }
    else {
        editRules.value = true
    }
}

function submit() {
    loading.value = true
    if(!hasRule.value) {
        store.searcherDelRule(store.selectedUser).then(() => {
            loading.value = false
        }).catch(() => {
            loading.value = false
        })
        return
    }

    const setRuleRequest = {
        query: localActiveRule.query,
        tag: localActiveRule.tag,
        start: timeWindow.start,
        end: timeWindow.end,
        recent: timeWindow.recent
    }

    store.searcherSetRule(props.selectedUser, setRuleRequest).
    then(() => loading.value = false).catch(() => {
        loading.value = false
    })
}

function removeRule() {
    for (var member in localActiveRule) localActiveRule[member] = undefined;
}

function setRule(rule: RuleInfo) {
    removeRule()
    Object.assign(localActiveRule, rule)
}

function getRuleFromStore() {
    if(searcher.value.rule == undefined) {
        return
    }
    Object.assign(localActiveRule, store.ruleFromId[searcher.value.rule.id])
    Object.assign(timeWindow, searcher.value.time_window)
}

watch(searcher, () => {
    if(searcher.value.rule.id != localActiveRule.id) {
        getRuleFromStore()
    }
})

onMounted(() => {
    if(searcher.value != undefined) {
        getRuleFromStore()
    }
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
                            <button :disabled="(searcher.running || loading)" type="button" class="btn btn-lg btn-outline-primary" @click="triggerEdit"><span v-if="!editRules">Edit</span><span v-if="editRules">Stop Edit</span></button>
                        </div>
                    </div>
                </div>
                <div class="card mb-2">
                    <div class="card-body text-center">
                        <CollectTasks :collect-tasks="searcher.collect_options" @submit="(tasks) => store.searcherSetCollectTasks(props.selectedUser, tasks)"/>
                    </div>
                </div>
                <div class="card mb-2">
                    <div class="card-body text-center" style="max-height:300px; overflow: auto;">
                        <Notifications :notifications="store.searcherNotifs"/>
                    </div>
                </div>
            </div>
            <div class="col-9">
                <TimeWindow2 :time_window="timeWindow" :edit="editRules"/>
                <div v-if="hasRule" class="input-group" @click="showQuery = !showQuery">
                    <label class="input-group-text" style="cursor: pointer;">ID</label>
                    <label class="input-group-text" style="cursor: pointer;">{{  localActiveRule.id }}</label>
                    <!-- <label class="input-group-text">{{ localActiveRule.tag }}</label> -->
                    <label class="input-group-text" style="cursor: pointer;">Tag</label>
                    <input type="text" :value="localActiveRule.tag" :disabled="true" class="form-control" style="cursor: pointer;"/>
                    <button v-if="editRules" type="button" class="btn btn-primary" @click="removeRule">Remove</button>
                </div>
                <div v-if="hasRule && showQuery" class="card p-2 bg-light text-wrap">
                    {{ localActiveRule.tag }}
                </div>
                <div v-if="!hasRule" class="input-group">
                    <input type="text" class="form-control text-center" value="No Rule Set" :disabled="true"/>
                </div>
                <Progress v-if="hasTotalCount" :total="searcher.time_window.total_count" :current="searcher.time_window.collected_count"/>
                <!-- <TimeWindow :time_window="searcher.time_window" :edit="editRules" @submit="setTimeWindow"/> -->
                
                <hr />
                <h5 class="text-center mt-3">Available Rules</h5>
                <RuleSelectionTable :show-action="editRules" action-name="Set" :loading="loading" :selectable="editRules" :unique-select="true" :rules="availableRules" @select="setRule" :fields="['id', 'tag', 'query', 'tweet_count']"/>
            </div>
        </div>
    </div>
</template>