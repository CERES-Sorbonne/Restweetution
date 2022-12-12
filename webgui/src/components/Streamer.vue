<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import RuleTable from './RuleTable.vue'
import {useStore} from '@/stores/store'
import { computed } from '@vue/reactivity';
import Notifications from './Notifications.vue';

const props = defineProps({
    selectedUser: {type: String, required: true}
})

const store = useStore()

const editRules = ref(false)
const showApiInfo = ref(false)
const loading = ref(false)

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

    showApiInfo.value = true
    apiRules.length = 0
    apiRules.push({tag: 'loadig', query: 'loading', api_id: 'loading'})
    store.getStreamerDebug(props.selectedUser).then((res) => {
        apiRules.length = 0
        res.api_rules.forEach(r => {
            apiRules.push({tag: r.tag, query: r.value, api_id: r.id})
        })
    })
}

function addRules(rules: any[]) {
    loading.value = true
    store.streamerAddRules(store.selectedUser, rules).
    then(() => loading.value = false)
}

function delRules(rules: any) {
    loading.value = true
    store.streamerDelRules(store.selectedUser, rules.map((r:any) => r.id)).
    then(() => loading.value = false)
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
        <h2 class="mb-5">Streamer</h2>
        <div class="row">
            <div class="col">
                <div class="">
                    <h5>Status:</h5>
                    <h3>{{streamer.running ? 'Collecting' : 'Stopped'}}</h3>
                </div>
                <div class="">
                    <button type="button" class="btn btn-primary btn-lg" @click="triggerStartStop">{{streamer.running ? 'Stop' : 'Start'}}</button>
                    <br />
                    <button type="button" class="btn btn-outline-primary mt-2 me-1" @click="editRules = !editRules"><span v-if="!editRules">Edit Rules</span><span v-if="editRules">Stop Edit</span></button>
                    <!-- <br /> -->
                    <button type="button" class="btn btn-outline-secondary mt-2" @click="triggerDebugData"><span v-if="!showApiInfo">[Debug]</span><span v-if="showApiInfo">[Debug] Hide Api Rules</span></button>
                </div>
            </div>

            <div class="col">
                <h5>Counters</h5>
                <p>Since Startup: {{streamer.count}}</p>
            </div>

            <div class="col-7 overflow-scroll" style="max-height: 200px;">
                <Notifications :notifications="store.streamerNotifs"/>
            </div>
        </div>

        <br>
        <br>

        <div v-show="showApiInfo">
            <RuleTable title="[DEBUG] Streamer Rules on Twitter API" :rules="apiRules" :fields="['api_id', 'tag', 'query']"/>
        </div>
        <h5 class="text-center">Active Rules</h5>
        <RuleTable action-name="Remove" :loading="loading" :rules="streamer.active_rules" :selectable="editRules" @selected="delRules" :fields="['id', 'tag', 'query', 'api_id']"/>
        
        <h5 class="text-center">Available Rules</h5>
        <RuleTable action-name="Add" :loading="loading" :selectable="editRules" :rules="availableRules" @selected="addRules" :fields="['id', 'tag', 'query', 'tweet_count']"/>
    </div>
</template>