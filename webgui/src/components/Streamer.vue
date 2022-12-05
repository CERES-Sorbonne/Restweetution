<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import RuleTable from './RuleTable.vue'
import {useUserStore} from '@/stores/users'
import { useRulesStore } from '@/stores/rules';
import { computed } from '@vue/reactivity';

const props = defineProps({
    selectedUser: {type: String, required: true}
})

const userStore = useUserStore()
const ruleStore = useRulesStore()

const editRules = ref(false)
const showApiInfo = ref(false)


const streamer = computed(() => userStore.streamers[props.selectedUser])
const isLoaded = computed(() => streamer.value != undefined)
const apiRules: any[] = reactive([])


function triggerStartStop() {
    if(streamer.value.running) {
        userStore.streamerStop(props.selectedUser)
    }
    else {
        userStore.streamerStart(props.selectedUser)
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
    userStore.getStreamerDebug(props.selectedUser).then((res) => {
        apiRules.length = 0
        res.api_rules.forEach(r => {
            apiRules.push({tag: r.tag, query: r.value, api_id: r.id})
        })
    })
}

function addRule(rule: any) {
    userStore.streamerAddRules(userStore.selectedUser, [rule])
}

function delRule(rule: any) {
    userStore.streamerDelRules(userStore.selectedUser, [rule])
}

onMounted(() => {
    if(!userStore.hasSelectedUser) {
        return
    }
    userStore.updateStreamerInfo(props.selectedUser)
})

watch(props, () => showApiInfo.value = false)

</script>

<template>
    <h2 class="text-center">Streamer</h2>
    <div v-if="isLoaded && props.selectedUser != 'undefined'">
    <h6 class="text-center">Status: {{streamer.running ? 'Collecting' : 'Stopped'}}</h6>
    <div class="text-center">
        <button type="button" class="btn btn-primary" @click="triggerStartStop">{{streamer.running ? '- Stop -' : '- Start -'}}</button>
        <button type="button" class="btn btn-primary ms-1" @click="editRules = !editRules"><span v-if="!editRules">Edit Rules</span><span v-if="editRules">Stop Edit</span></button>
        <br />
        <button type="button" class="btn btn-secondary ms-1 mt-2" @click="triggerDebugData"><span v-if="!showApiInfo">[Debug]</span><span v-if="showApiInfo">[Debug] Hide Api Rules</span></button>
    </div>
    <br>
    <br>

    <div v-show="showApiInfo">
        <RuleTable title="[DEBUG] Streamer Rules on Twitter API" :rules="apiRules" :fields="['api_id', 'tag', 'query']"/>
    </div>

    <RuleTable title="Active Rules" :rules="streamer.active_rules" :delButton="editRules" @remove-rule="delRule" :fields="['id', 'tag', 'query', 'api_id']"/>
    <RuleTable :add-button="editRules" title="Rule History" :rules="ruleStore.orderedRules" @add-rule="addRule" :fields="['id', 'tag', 'query', 'tweet_count']"/>
    </div>
</template>