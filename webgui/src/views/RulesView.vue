<script setup lang="ts">
import Menu from "../components/Menu.vue"
import RuleTable from "../components/RuleTable.vue"

import { computed, reactive, ref } from "@vue/reactivity";
import { watch } from "vue";
import { useStore } from "@/stores/store";

const store = useStore()

const edit = ref(false)
const newRule = reactive({tag: '', query: ''})

const anyQuery = computed(() => newRule.query != '')
const anyTags = computed(() => newRule.tag != '')
const ruleIsVerified = ref(false)
const errorMessage: any = reactive({})
const loading = ref(false)

function verifyRule() {
    loading.value = true
    store.verifyQuery(newRule).then(res => {
        loading.value = false
        ruleIsVerified.value = res.valid
        if(!res.valid) {
            setErrorMessage(res.error[0])
        }
        else {
            setErrorMessage({})
        }
    })
}

function setErrorMessage(error: any) {
    Object.keys(errorMessage).forEach(k => delete errorMessage[k])
    Object.assign(errorMessage, error)
}

function reset() {
    newRule.tag = ''
    newRule.query = ''
    ruleIsVerified.value = false
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


</script>
<template>
  <Menu />
  
  <div class="text-left pb-1 pt-3">
        <button type="button" class="btn btn-primary" @click="edit = !edit">{{edit ? 'Stop Edit' : 'Edit'}}</button>
        <button v-if="edit && !ruleIsVerified" :disabled="!store.hasSelectedUser || !anyQuery" type="button" class="btn btn-primary ms-1" @click="verifyRule">Verify Query</button>
        <button v-if="edit && ruleIsVerified" type="button" class="btn btn-primary ms-1"  @click="ruleIsVerified = false">Modify Query</button>
        <button v-if="ruleIsVerified" :disabled="!anyTags" type="button" class="btn btn-primary ms-1" @click="addRule">Submit</button>
        <button v-if="loading" disabled="true" type="button" class="btn btn-secondary ms-1">Loading...</button>
        
        <div class="pt-2" v-if="edit">
            <div v-if="errorMessage.title">
                <p class="text-danger">{{errorMessage.title}}</p>
                <div v-if="errorMessage.details">
                    <p class="text-danger" v-for="detail in errorMessage.details">{{detail}}</p>
                </div>
            </div>
            <div v-else>
                <p class="text-warning" v-if="!store.hasSelectedUser">Select a User Config to perform verification</p>
            </div>
            <div v-if="ruleIsVerified">
                <p class="text-success">Query is Valid ! Choose some Tags for identification</p>
            </div>
            <form action="/streamer/add_rule" method="POST">
                <div><textarea :disabled="ruleIsVerified" type="text" v-model="newRule.query" name="query" rows="3" cols="40" class="form-control" placeholder="Query"></textarea></div>
                <div v-if="ruleIsVerified" class="pt-1"><input type="text" v-model="newRule.tag" name="tag" class="form-control" placeholder="Tags" /></div>
            </form>
        </div>
    </div>

  <RuleTable :rules="store.rules" />
</template>