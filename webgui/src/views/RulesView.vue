<script setup lang="ts">
import Menu from "../components/Menu.vue"
import RuleSelectionTable from "@/components/RuleSelectionTable.vue";
import RuleCountChart2 from '@/components/RuleCountChart2.vue'

import { computed, reactive, ref } from "@vue/reactivity";
import { watch } from "vue";
import { useStore } from "@/stores/store";
import TimeWindow2 from "@/components/TimeWindow2.vue";
import type { CountRequest, CountResult } from "@/api/collector";
import * as collector from '@/api/collector'

const store = useStore()

const edit = ref(false)
const newRule = reactive({tag: '', query: ''})

const anyQuery = computed(() => newRule.query != '')
const anyTags = computed(() => newRule.tag != '')
// const ruleIsVerified = ref(false)
const errorMessage: any = reactive({})
const loading = ref(false)
const timeWindow = reactive({start: undefined, end: undefined, recent: true})

const countResults: CountResult[] = reactive([])
const actualResult: {res?: CountResult} = reactive({res: undefined})

const ruleIsVerified = computed(() => actualResult.res != undefined)

function setRule(rule: {tag: string, query: string}) {
    newRule.query = rule.query
    newRule.tag = rule.tag
}

// function verifyRule() {
//     loading.value = true
//     store.verifyQuery(newRule).then(res => {
//         loading.value = false
//         ruleIsVerified.value = res.valid
//         if(!res.valid) {
//             setErrorMessage(res.error[0])
//         }
//         else {
//             setErrorMessage({})
//         }
//     })
// }


function setErrorMessage(error: any) {
    Object.keys(errorMessage).forEach(k => delete errorMessage[k])
    Object.assign(errorMessage, error)
}

function count() {
    setErrorMessage({})
    const request: CountRequest = {
        query: newRule.query,
        start: timeWindow.start,
        end: timeWindow.end,
        recent: timeWindow.recent
    }
    loading.value = true
    collector.searcherCount(store.selectedUser, request).then(res => {
        countResults.unshift(res)
        actualResult.res = res
        loading.value = false
    }).catch(err => {
        loading.value = false
        setErrorMessage(err.response.data)
    })
}



function reset() {
    newRule.tag = ''
    newRule.query = ''
    actualResult.res = undefined
    setErrorMessage({})
}

function addRule() {
    store.addRules([newRule]).then(() => reset())
}

watch(edit, () => {
    if(!edit.value) {
        reset()
    }
})

const query = computed(() => newRule.query)
watch(query, ()=> {
    actualResult.res = undefined
})

const queryClass = computed(() => {
    if(ruleIsVerified.value) {
        return 'is-valid'
    }
    if(errorMessage.title) {
        return 'is-invalid'
    }
})


</script>
<template>
    <Menu />

    <div class="row">
        <div class="col">
            <h4 class="text-center">Rule Tester</h4>
            <TimeWindow2 :time_window="timeWindow" :edit="true"/>
            <div v-if="errorMessage">
                <p class="text-danger" v-for="err in errorMessage">{{err}}</p>
            </div>
            <div v-else>
                <p class="text-warning" v-if="!store.hasSelectedUser">Select a User Config to perform verification</p>
            </div>
            <form action="/streamer/add_rule" method="POST" class="input-group needs-validation">
                <textarea type="text" v-model="newRule.query" name="query" rows="3" cols="40" class="form-control" :class="queryClass" placeholder="Rule"></textarea>
                <button type="button" @click="count" class="btn btn-outline-secondary" :disabled="loading || !store.hasSelectedUser">{{ loading ? 'Loading..' : 'Count' }}</button>
                <div class="valid-feedback">
                    Count:  {{actualResult.res ? actualResult.res.total : ''}}
                </div>
                <div class="invalid-feedback">
                    <p class="text-danger" v-for="detail in errorMessage.details">{{detail}}</p>
                </div>
                <div v-if="ruleIsVerified" class="input-group needs-validation mt-2">
                    <input type="text" placeholder="Tags" v-model="newRule.tag" class="form-control" />
                    <button @click="addRule" class="btn btn-outline-secondary" type="button" :disabled="newRule.tag == undefined || newRule.tag == ''">Save Rule</button>
                    <div class="invalid-feedback">
                        Define at least one Tag
                    </div>
                </div>
            </form>

            <h5 v-if="countResults.length > 0" class="text-center">Count Results: </h5>
            <div v-for="count in countResults" class="card mb-2">
                <div class="card-body">
                    <p>{{ count.query }}</p>
                    <RuleCountChart2  :points="count.points"/>
                </div>
            </div>
        </div>

    
        <div class="col">
            <h5 class="text-center">Saved Rules</h5>
            <RuleSelectionTable :rules="store.orderedRules" actionName="Set" @select="setRule"/>
        </div>
    </div>
</template>