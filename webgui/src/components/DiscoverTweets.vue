<script setup lang="ts">

import { toDatetimeInputString } from '@/utils';
import { computed, reactive, ref } from '@vue/reactivity';
import { onMounted, watch } from 'vue';
import { useStore, type CollectTasks, type Rule } from '@/stores/store'
import DateInterval from '@/components/DateInterval.vue'
import SelectableTableRows from './RuleSelectionTable.vue';
import CollectionSelection from './CollectionSelection.vue';
import * as storage_api from '@/api/storage'
import TweetTable from './TweetTable.vue';
import RowFieldSelection from './RowFieldSelection.vue';

interface TweetCountQuery{
    date_from?: String
    date_to?: String
    rule_ids?: Array<Number>
}


interface TweetQuery extends TweetCountQuery {
    ids?: string[]
    offset?: number
    limit?: number
    desc?: boolean
    fields?: string[]
}


const store = useStore()
const dateInterval = reactive({start: undefined, end: undefined})
const show = ref(false)
const showResult = ref(false)
const editRules = ref(false)
const selectedRules = reactive({values: new Array<Rule>()})
const tweetResult = reactive({count: -1, tweets: []})
const mode = ref(0) // 0: settings, 1: discover
const discoverPage = ref(0)
const tweetPerPage = ref(100)
const selectedFields = reactive(['id', 'author_username', 'created_at', 'text'])

const hasTweets = computed(() => tweetResult.tweets.length > 0)
const discoverTabClass = computed(() => {
    let cls = ''
    if(!hasTweets.value) {
        cls += ' disabled'
    }
    if(mode.value == 1) {
        cls += ' active'
    }
    return cls
})
const maxDiscoverPages = computed(() => {
    if(tweetResult.count < 0) {
        return 0
    }
    return Math.floor(tweetResult.count / tweetPerPage.value)
})

function resetTweetResult() {
    tweetResult.count = -1
    tweetResult.tweets.length = 0
    discoverPage.value = 0
}

function setMode(value: number) {
    if(value == 1 && !hasTweets.value) {
        return
    }
    mode.value = value
}

function getQuery() {
    let query: TweetQuery = {}
    if(dateInterval.start) {
        query.date_from = dateInterval.start
    }
    if(dateInterval.end) {
        query.date_to = dateInterval.end
    }
    if(selectedRules.values.length > 0) {
        query.rule_ids = selectedRules.values.map(r => r.id)
    }
    return query
}

async function discover() {

    let query = getQuery()
    let res = await storage_api.discoverTweets({...query})
    tweetResult.count = res.count
    tweetResult.tweets = res.tweets
    discoverPage.value = 0
    setMode(1)
}

async function getPage(nb: number) {
    let query = getQuery()
    query.offset = nb * tweetPerPage.value
    let res = await storage_api.getTweets(query)
    tweetResult.tweets = res
    discoverPage.value = nb
}

async function getCount() {
    let query = getQuery()
    let res = await storage_api.getTweetCount(query)
    tweetResult.count = res
}

watch(selectedRules, resetTweetResult)

</script>

<template >

    <ul class="nav nav-tabs mb-5">
        <li class="nav-item" @click="setMode(0)">
            <a class="nav-link" :class="(mode == 0 ? 'active' : '')" href="#">Collection Settings</a>
        </li>
        <li class="nav-item" @click="setMode(1)">
            <a :class="'nav-link' + discoverTabClass" href="#" >Discover</a>
        </li>
    </ul>


    <div class="row" v-if="(mode == 0)">
        <div class="col">
            <CollectionSelection :selectedRules="selectedRules.values"/>
        </div>
        <div class="col-3 m-5">
            <DateInterval v-model:start="dateInterval.start" v-model:end="dateInterval.end"/>
            <hr/>
            <div class="text-center">
                <button @click="getCount" type="button" class="btn btn-outline-primary btn-lg me-2">Count</button>
                <button @click="discover" type="button" class="btn btn-outline-primary btn-lg me-2">Discover</button>
                <br />
                <br />
                <div v-if="(tweetResult.count != -1)">
                    <h5 class="text-center">Found:</h5>
                    {{tweetResult.count}} Tweets
                </div>
            </div>
        </div>
    </div>
    <div v-else class="row">
        <div class="col-3">
            <RowFieldSelection :fields="selectedFields"/>
        </div>
        <div class="col-9">
            <div class="text-end">
                <h5 class="text-start">Total: {{tweetResult.count}} Tweets</h5>
                <h5>
                    Page {{discoverPage}} from {{maxDiscoverPages}} 
                    <button :disabled="(discoverPage == 0)" @click="getPage(discoverPage-1)" type="button" class="btn btn-outline-primary me-2">Prev</button>
                    <button :disabled="(discoverPage == maxDiscoverPages)" @click="getPage(discoverPage+1)" type="button" class="btn btn-outline-primary me-2">Next</button>
                </h5>
                
            </div>
            <TweetTable :tweets="tweetResult.tweets" :fields="selectedFields"/>
        </div>
    </div>

</template>