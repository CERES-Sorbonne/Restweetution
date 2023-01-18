<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import RuleTable from './RuleTable.vue'
import {useStore} from '@/stores/store'
import { computed } from '@vue/reactivity';
import Notifications from './Notifications.vue';
import CollectTasks from './CollectTasks.vue';
import RuleSelectionTable from './RuleSelectionTable.vue';

const props = defineProps({
    selectedUser: {type: String, required: true}
})

const store = useStore()

const editRules = ref(false)
const showApiInfo = ref(false)
const loading = ref(false)
const loadingVerify = ref(false)

const streamer = computed(() => store.streamers[props.selectedUser])
const isLoaded = computed(() => streamer.value != undefined)
const availableRules = computed(() => {
    let active: any = {}
    if(streamer.value) {
        streamer.value.active_rules.forEach((r) => active[r.id] = true)
    }
    return store.orderedRules.filter((r:any) => !active[r.id])
})

const apiRules: any[] = reactive([])


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
        console.log(res)
        apiRules.length = 0
        res.api_rules.forEach(r => {
            apiRules.push({tag: r.tag, query: r.value, api_id: r.id})
        })
        loadingVerify.value = false
    })
}

function addRules(rules: any[]) {
    loading.value = true
    store.streamerAddRules(store.selectedUser, rules).
    then(() => loading.value = false)
    editRules.value = false
}

function delRules(rules: any) {
    loading.value = true
    store.streamerDelRules(store.selectedUser, rules.map((r:any) => r.id)).
    then(() => loading.value = false)
    editRules.value = false
}

function syncFromUI() {
    loading.value = true
    store.streamerSetRules(store.selectedUser, streamer.value.active_rules).
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

// onMounted(() => {
//     if(!store.hasSelectedUser) {
//         return
//     }
//     store.streamerInfo(props.selectedUser)
// })

watch(props, () => showApiInfo.value = false)

</script>

<template>
    <div v-if="isLoaded && props.selectedUser != 'undefined'">
        <h2 class="mb-5 text-center">Streamer:
            <span class="text-danger" v-if="streamer.conflict">Conflict</span>
            <span class="text-success" v-else-if="streamer.running">Collecting</span>
            <span class="text-warning" v-else>Stopped</span>
        </h2>
        <div class="row">
            <div class="col text-center">
                <div class="card mb-2">
                    <div class="card-body">
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
                        <CollectTasks :collect-tasks="streamer.collect_tasks" @submit="(tasks) => store.streamerSetCollectTasks(props.selectedUser, tasks)"/>
                    </div>
                </div>
                <div class="card">
                    <div class="card-body">
                        <h5>Collected</h5>
                        <p>Since Startup: {{streamer.count}}</p>
                    </div>
                </div>
            </div>
            <div class="col-9">
                <div v-show="showApiInfo">
                    <RuleTable title="[DEBUG] Streamer Rules on Twitter API" :rules="apiRules" :fields="['api_id', 'tag', 'query']"/>
                </div>
                <button type="button" class="btn btn-outline-primary me-1" :disabled="loading" @click="editRules = !editRules"><span v-if="!editRules">Edit Rules</span><span v-if="editRules">Stop Edit</span></button>
                <div class="row">
                    <div class="col">
                        <h5 class="text-center">Active Rules</h5>
                        <RuleSelectionTable action-name="Remove" :loading="loading" :rules="streamer.active_rules" :selectable="editRules" @selected="delRules" :fields="['id', 'tag', 'query', 'api_id']"/>
                
                    </div>
                    <div class="col">
                        <h5 class="text-center">Available Rules</h5>
                        <RuleSelectionTable action-name="Add" :loading="loading" :selectable="editRules" :rules="availableRules" @selected="addRules" :fields="['id', 'tag', 'query', 'tweet_count']"/>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>