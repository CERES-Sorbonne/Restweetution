<script setup lang="ts">

import { toDatetimeInputString } from '@/utils';
import { computed, reactive, ref } from '@vue/reactivity';
import { onMounted, watch } from 'vue';
import { useStore, type CollectTasks, type Rule } from '@/stores/store'
import DateInterval from '@/components/DateInterval.vue'
import CollectionSelection from './CollectionSelection.vue';
import * as storage_api from '@/api/storage'
import TweetTable from './TweetTable.vue';
import RowFieldSelection from './RowFieldSelection.vue';
import Exporter from '@/components/Exporter.vue'
import type { TweetQuery } from '@/api/types';


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
const modeExport = ref(false)

const hasTweets = computed(() => tweetResult.tweets.length > 0)

function optionalNavLinkClass(n: number) {
    let class_ = 'nav-link '
    if(tweetResult.count < 1 || (n == 1 && !hasTweets.value)) {
        class_ += 'disabled '
    }
    else if(mode.value == n) {
        class_ += 'active '
    }
    return class_
}

const maxDiscoverPages = computed(() => {
    if(tweetResult.count < 0) {
        return 0
    }
    return Math.floor(tweetResult.count / tweetPerPage.value)
})

const query = computed(() => {
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
    if(value == 2 && tweetResult.count < 1) {
        return
    }

    mode.value = value
}

async function discover() {
    let res = await storage_api.discoverTweets(query.value)
    tweetResult.count = res.count
    tweetResult.tweets = res.tweets
    discoverPage.value = 0
    setMode(1)
}

async function export_() {
    await getCount()
    setMode(2)
}

async function getPage(nb: number) {
    let q = Object.assign({}, query.value)
    q.offset = nb * tweetPerPage.value
    let res = await storage_api.getTweets(q)
    tweetResult.tweets = res
    discoverPage.value = nb
}

async function getCount() {
    let res = await storage_api.getTweetCount(query.value)
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
            <a :class="optionalNavLinkClass(1)" href="#" >Discover</a>
        </li>
        <li class="nav-item" @click="setMode(2)">
            <a :class="optionalNavLinkClass(2)" href="#" >Export</a>
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
                <button @click="getCount" type="button" class="btn btn-outline-primary me-2">Count</button>
                <button @click="discover" type="button" class="btn btn-outline-primary me-2">Discover</button>
                <button @click="export_" type="button" class="btn btn-outline-primary me-2">Export</button>
                <br />
                <br />
                <div v-if="(tweetResult.count != -1)">
                    <h5 class="text-center">Found:</h5>
                    {{tweetResult.count}} Tweets
                </div>
            </div>
        </div>
    </div>
    <div v-if="(mode == 1)" class="row">
        <div class="col-3">
            <RowFieldSelection :fields="selectedFields"/>
        </div>
        <div class="col-9">
            <div class="row">
                <div class="col-3">
                    <h5>Total: {{tweetResult.count}} Tweets</h5>
                </div>
                <div class="col">
                    <div class="text-end">
                        <h5>
                            <button @click="modeExport = !modeExport" type="button" class="btn btn-outline-primary me-2">Export</button>
                            Page {{discoverPage}} from {{maxDiscoverPages}} 
                            <button :disabled="(discoverPage == 0)" @click="getPage(discoverPage-1)" type="button" class="btn btn-outline-primary me-2">Prev</button>
                            <button :disabled="(discoverPage == maxDiscoverPages)" @click="getPage(discoverPage+1)" type="button" class="btn btn-outline-primary me-2">Next</button>
                        </h5>
                    </div>
                </div>
            </div>
            <div class="row" v-if="modeExport">
                <Exporter :query="query" :count="tweetResult.count" :fields="selectedFields"/>
            </div>
            <div class="row mt-3">
                <TweetTable :tweets="tweetResult.tweets" :fields="selectedFields"/>
            </div>
            
        </div>
    </div>
    <div v-if="(mode == 2)">
    </div>

</template>