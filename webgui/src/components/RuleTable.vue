<script setup lang="ts">
import { reactive, computed, watch } from 'vue'
import { stringifyQuery } from 'vue-router';

const filter = reactive({id: '', type: '', name: '', tag: '', query: ''})

const props = defineProps({
    delButton: Boolean,
    addButton: Boolean,
    rules: {
        type: Array<any>,
        required: true
    },
    fields: {
        type: Array<string>,
        validator(value: Array<string>) {
            return !value.some(v => !['id', 'type', 'name', 'tag', 'query', 'api_id', 'tweet_count'].includes(v))
        },
        default: ['id', 'type', 'name', 'tag', 'query', 'tweet_count']
    },
    title: {
        type: String,
        default: ''
    }
})

const filteredRules = computed(() => {
    let rules = props.rules
    if(filter.id !== '') {
        rules = rules.filter(r => r.id == filter.id)
    }
    if(filter.type !== '') {
        rules = rules.filter(r => r.type.includes(filter.type))
    }
    if(filter.name !== '') {
        rules = rules.filter(r => r.name.includes(filter.name))
    }
    if(filter.tag !== '') {
        rules = rules.filter(r => r.tag.includes(filter.tag))
    }
    if(filter.query !== '') {
        rules = rules.filter(r => r.query.includes(filter.query))
    }
    return rules
})
const showId = computed(() => props.fields.includes('id'))
const showType = computed(() => props.fields.includes('type'))
const showName = computed(() => props.fields.includes('name'))
const showTag = computed(() => props.fields.includes('tag'))
const showQuery = computed(() => props.fields.includes('query'))
const showTweetCount = computed(() => props.fields.includes('tweet_count'))
const showApiId = computed(() => props.fields.includes('api_id'))

</script>

<template>
    <div class="table-responsive">
        <h5 class="text-center">{{props.title}}</h5>
        <table class="table table-striped table-sm text-nowrap table-hover">
            <thead class="table-dark">
                <tr>
                    <th v-if="props.delButton" class="text-center">...</th>
                    <th v-if="props.addButton" class="text-center">...</th>
                    <th v-if="showId">ID</th>
                    <th v-if="showType">Type</th>
                    <th v-if="showName">Name</th>
                    <th v-if="showTag">Tag</th>
                    <th v-if="showQuery">Query</th>
                    <th v-if="showTweetCount">Tweet Count</th>
                    <th v-if="showApiId">API ID</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <th v-if="props.delButton"></th>
                    <th v-if="props.addButton"></th>
                    <th v-if="showId"><input style="max-width: 100px;" type="number" placeholder="ID" class="form-control" v-model="filter.id"></th>
                    <th v-if="showType">
                        <select style="min-width: 100px;" class="form-select" v-model="filter.type">
                            <option value="">All</option>
                            <option value="streamer">Streamer</option>
                            <option value="searcher">Searcher</option>
                        </select>
                    </th>
                    <th v-if="showName"><input type="text" placeholder="Name" class="form-control" v-model="filter.name"></th>
                    <th v-if="showTag"><input type="text" placeholder="Tag" class="form-control" v-model="filter.tag"></th>
                    <th v-if="showQuery"><input type="text" placeholder="Query" class="form-control" v-model="filter.query"></th>
                </tr>
                <tr v-for="rule in filteredRules">
                    <td v-if="props.delButton" @click="$emit('removeRule', rule.id)" class="text-center"><button class="btn text-danger p-0">X</button></td>
                    <td v-if="props.addButton" @click="$emit('addRule', rule)" class="text-center"><button class="btn text-success p-0">Set</button></td>
                    <td v-if="showId">{{rule.id}}</td>
                    <td v-if="showType">{{rule.type}}</td>
                    <td v-if="showName">{{rule.name}}</td>
                    <td v-if="showTag">{{rule.tag}}</td>
                    <td v-if="showQuery">{{rule.query}}</td>
                    <td v-if="showTweetCount">{{rule.tweet_count}}</td>
                    <td v-if="showApiId">{{rule.api_id}}</td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<style scoped>
input {
    min-width: 70px;
}
/* .table-hover tbody tr:hover td{
  background-color: green;
} */
</style>