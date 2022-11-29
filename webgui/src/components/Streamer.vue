<script setup lang="ts">
import { ref, reactive } from 'vue'
import RuleTable from './RuleTable.vue'
import {useRulesStore} from '@/stores/rules'

const store = useRulesStore()

const running = ref(false)
const editRules = ref(false)
const showApiInfo = ref(false)

const newRule = reactive({tag: undefined, query: undefined})
const ruleIsVerified = ref(false)

function verifyRule() {
    ruleIsVerified.value = true
}

function addRule() {
    newRule.tag = undefined
    newRule.query = undefined
    ruleIsVerified.value = false
}

function setRule(rule: any) {
    newRule.tag = rule.tag
    newRule.query = rule.query
}

</script>

<template>
    <h2 class="text-center">Streamer</h2>
    <h6 class="text-center">Status: {{running ? 'Collecting' : 'Stopped'}}</h6>
    <div class="text-center">
        <button type="button" class="btn btn-primary" @click="running = !running">{{running ? 'Stop' : 'Start'}}</button>
        <button type="button" class="btn btn-primary ms-1" @click="editRules = !editRules"><span v-if="!editRules">Edit Rules</span><span v-if="editRules">Stop Edit</span></button>
        <button type="button" class="btn btn-primary ms-1" @click="showApiInfo = !showApiInfo"><span v-if="!showApiInfo">[Debug] Show API rules</span><span v-if="showApiInfo">[Debug] Hide Api Rules</span></button>
    </div>
    <br>
    <br>

    <div v-show="showApiInfo">
        <RuleTable title="[DEBUG] Streamer Rules on Twitter API" :rules="store.apiStreamerRules" :fields="['api_id', 'tag', 'query']"/>
    </div>

    <div v-show="editRules">
        <form action="/streamer/add_rule" method="POST">
            <h6>Add Rule</h6>
            <div class="row">
                <div class="col-sm-6">
                    <input type="text" v-model="newRule.tag" name="tag" class="form-control" placeholder="Tag">
                </div>
            </div>
            <textarea type="text" v-model="newRule.query" name="query" rows="3" cols="40" class="form-control mt-2" placeholder="querry"></textarea>
            <div class="row">
                <div class="col-sm-6">
                    <input type="submit" class="form-control mt-2" value="Verify" @click.prevent="verifyRule">
                </div>
                <div class="col-sm-6">
                    <input :disabled="!ruleIsVerified" type="submit" class="col-sm-3 form-control mt-2" value="Add" @click.prevent="addRule">
                </div>
            </div>
        </form>
    </div>

    <RuleTable title="Active Rules" :rules="store.orderedRules" :delButton="editRules" @remove-rule="" :fields="['id', 'tag', 'query', 'api_id']"/>
    <RuleTable :add-button="editRules" title="Rule History" :rules="store.orderedRules" @add-rule="setRule" :fields="['id', 'tag', 'query', 'tweet_count']"/>
</template>