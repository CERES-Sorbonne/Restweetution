<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import RuleTable from './RuleTable.vue'
import {useStore} from '@/stores/store'
import { computed } from '@vue/reactivity';
import Notifications from './Notifications.vue';
import CollectTasks from './CollectTasks.vue';
import RuleSelectionTable from './RuleSelectionTable.vue';
import type { RuleInfo } from '@/api/collector';
import {areArraysEqualSets} from '@/utils'

const props = defineProps({
    selectedUser: {type: String, required: true}
})

const store = useStore()

const editRules = ref(false)
const showApiInfo = ref(false)
const loading = ref(false)
const loadingVerify = ref(false)

const streamer = computed(() => {
    return store.streamers[props.selectedUser]
})
const isLoaded = computed(() => streamer.value != undefined)

const localActiveRules: RuleInfo[] = reactive([])
const availableRules = computed(() => {
    return store.orderedRules.filter((r:RuleInfo) => !localActiveRules.some(r2 => r2.id == r.id))
})

const apiRules: any[] = reactive([])


function takeRulesFromStore() {
    //console.log('take rules')
    localActiveRules.length = 0
    // console.log('active rules: ')
    // console.log(streamer.value.active_rules)
    // console.log(store.ruleFromId)
    let tmpRules = streamer.value.active_rules.map(r => store.ruleFromId[r.id]).filter(r => r != undefined)
    localActiveRules.push(...tmpRules)
}

const localRulesEqualToStore = computed(() => {
    //console.log(streamer.value.active_rules)
    // console.log(localActiveRules)
    let eq = areArraysEqualSets(streamer.value.active_rules.map(r => r.id),localActiveRules.map(r => r.id))
    //console.log(eq)
    return eq
})

watch(streamer, () => {
    console.log('trigger watch')
    console.log(streamer.value)
    if(!streamer) {
        return
    }
    if(!localRulesEqualToStore.value) {
        console.log('take rules')
        takeRulesFromStore()
    }
})

function triggerStartStop() {
    if(streamer.value.running) {
        store.streamerStop(props.selectedUser)
    }
    else {
        store.streamerStart(props.selectedUser)
    }
}

function triggerDebugData() {
    if(showApiInfo.value) {
        showApiInfo.value = false
        return
    }

    loadingVerify.value = true
    showApiInfo.value = true
    apiRules.length = 0
    apiRules.push({tag: 'loadig', query: 'loading', api_id: 'loading'})
    store.streamerVerify(props.selectedUser).then((res) => {
        //console.log(res)
        apiRules.length = 0
        res.api_rules.forEach(r => {
            apiRules.push({tag: r.tag, query: r.value, api_id: r.id})
        })
        loadingVerify.value = false
    })
}

function addRules(rule: RuleInfo) {
    localActiveRules.push(rule)
}

function delRules(rule: RuleInfo) {
    localActiveRules.splice(localActiveRules.findIndex(r => r.id == rule.id), 1)
}

function syncFromUI() {
    loading.value = true
    store.streamerSetRules(store.selectedUser, localActiveRules).
    then(() => loading.value = false)
    editRules.value = false
    showApiInfo.value = false
}

function syncFromAPI() {
    loading.value = true
    store.streamerSync(store.selectedUser).
    then(() => loading.value = false)
    editRules.value = false
    showApiInfo.value = false
}

onMounted(() => {
    if(!store.hasSelectedUser) {
        return
    }
    if(streamer.value) {
        takeRulesFromStore()
    }
})

watch(props, () => showApiInfo.value = false)

</script>

<template>
    <div v-if="store.isLoaded && isLoaded && props.selectedUser != 'undefined'">
        <h2 class="mb-5 text-center">Streamer:
            <span class="text-danger" v-if="streamer.conflict">Conflict</span>
            <span class="text-success" v-else-if="streamer.running">Collecting</span>
            <span class="text-warning" v-else>Stopped</span>
        </h2>
        <div class="row">
            <div class="col text-center">
                <div class="card mb-2">
                    <div class="card-body">
                        <h5 class="text-center">Controls</h5>
                        <div class="mb-2">
                            <button type="button" class="btn btn-primary btn-lg me-2" @click="triggerStartStop">{{streamer.running ? 'Stop' : 'Start'}}</button>
                            <button v-if="(!showApiInfo || loadingVerify) && !streamer.conflict" type="button" class="btn btn-lg btn-outline-secondary me-1" @click="triggerDebugData">Verify</button>
                            <button type="button" class="btn btn-lg btn-success" @click="(showApiInfo = false)" v-if="(!streamer.conflict && showApiInfo && !loadingVerify)">No Conflict</button>
                            <button type="button" class="btn btn-lg btn-danger" disabled="true" v-if="(streamer.conflict)">Conflict</button>
                        </div>
                        <div>
                            <button type="button" class="btn btn-warning me-1" @click="syncFromAPI" v-if="streamer.conflict">Sync From API</button>
                            <button type="button" class="btn btn-warning" @click="syncFromUI" v-if="streamer.conflict">Sync From UI</button>
                        </div>
                    </div>
                        
                </div>
                <div class="card mb-2">
                    <div class="card-body">
                        <CollectTasks :collect-tasks="streamer.collect_options" @submit="(tasks) => store.streamerSetCollectTasks(props.selectedUser, tasks)"/>
                    </div>
                </div>
                <div class="card mb-2">
                    <div class="card-body">
                        <h5>Collected</h5>
                        <p>Since Startup: {{streamer.count}}</p>
                    </div>
                </div>
                <div class="card mb-2">
                    <div class="card-body" style="max-height:200px; overflow: auto;">
                        <Notifications :notifications="store.streamerNotifs"/>    
                    </div>
                </div>
            </div>
            <div class="col-9">
                <div v-show="showApiInfo">
                    <RuleTable title="[DEBUG] Streamer Rules on Twitter API" :rules="apiRules" :fields="['api_id', 'tag', 'query']"/>
                </div>
                <div>
                    <button type="button" class="btn btn-outline-primary me-1" :disabled="loading || localRulesEqualToStore" @click="takeRulesFromStore">Cancel</button>
                    <button type="button" class="btn btn-outline-primary me-1" :disabled="loading || localRulesEqualToStore" @click="syncFromUI">Submit</button>
                    <button v-if="loading" type="button" class="btn btn-dark me-1" :disabled="true">Loading</button>
                </div>
                
                <div class="row">
                    <div class="col">
                        <h5 class="text-center">Active Rules</h5>
                        <RuleSelectionTable action-name="Remove" :loading="loading" :rules="localActiveRules" :selectable="editRules" @select="delRules" :fields="['id', 'tag', 'query', 'api_id']"/>
                
                    </div>
                    <div class="col">
                        <h5 class="text-center">Available Rules</h5>
                        <RuleSelectionTable action-name="Add" :loading="loading" :selectable="editRules" :rules="availableRules" @select="addRules" :fields="['id', 'tag', 'query', 'tweet_count']"/>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>