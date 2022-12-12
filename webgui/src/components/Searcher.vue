<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import RuleTable from './RuleTable.vue'
import {useStore} from '@/stores/store'
import { computed } from '@vue/reactivity';
import TimeWindow from './TimeWindow.vue';
import Notifications from './Notifications.vue';

const props = defineProps({
    selectedUser: {type: String, required: true}
})

const store = useStore()

const editRules = ref(false)
const loading = ref(false)

const searcher = computed(() => store.searchers[props.selectedUser])
const isLoaded = computed(() => searcher.value != undefined)

const availableRules = computed(() => {
    if(searcher.value && searcher.value.rule) {
        return store.orderedRules.filter((r:any) => r.query != searcher.value.rule.query)
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

function setRule(rule: any) {
    loading.value = true
    store.searcherSetRule(props.selectedUser, rule).
    then(() => loading.value = false)
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

function setTimeWindow(window: any) {
    loading.value = true
    store.searcherSetTimeWindow(props.selectedUser, window).then(() => loading.value = false)
}

// onMounted(() => {
//     if(!store.hasSelectedUser) {
//         return
//     }
//     store.searcherInfo(props.selectedUser)
// })

// watch(props, () => {
    
// })


</script>

<template>
    <div v-if="isLoaded">

    <h2 class="text-center pb-4" >Searcher</h2>
    <div class="row">
        <div class="col">
            <div v-if="isLoaded && props.selectedUser != 'undefined'">
                <h6 class="text-center">Status:</h6>
                <h2 class="text-center pb-1">{{searcher.running ? 'Collecting' : 'Stopped'}}</h2>
                <div class="text-center mb-3">
                    <button :disabled="(editRules || loading)" type="button" class="btn btn-primary btn-lg" @click="triggerStartStop">{{searcher.running ? 'Stop' : 'Start'}}</button>
                </div>
                <div class="text-center">
                    <button :disabled="(searcher.running || loading)" type="button" class="btn btn-outline-primary" @click="editRules = !editRules"><span v-if="!editRules">Edit</span><span v-if="editRules">Stop Edit</span></button>
                </div>
            </div>
        </div>
        <div class="col-3">
            <TimeWindow :time_window="searcher.time_window" :edit="editRules" @submit="setTimeWindow"/>
        </div>
        <div class="col-7 overflow-scroll" style="max-height: 200px;">
            <Notifications :notifications="store.searcherNotifs"/>
        </div>
    </div>
    <br />
    <br />
    <h5 class="text-center">Active Rule</h5>
    <RuleTable :show-filter="false" action-name="Remove" :loading="loading" :rules="searcher.rule ? [searcher.rule] : undefined" :selectable="editRules" @selected="delRule" :fields="['id', 'tag', 'query']"/>
    
    <h5 class="text-center">Available Rules</h5>
    <RuleTable action-name="Set" :loading="loading" :selectable="editRules" :unique-select="true" :rules="availableRules" @selected="setRule" :fields="['id', 'tag', 'query', 'tweet_count']"/>
    </div>
</template>