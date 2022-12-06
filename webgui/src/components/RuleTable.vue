<script setup lang="ts">
import { reactive, computed, watch } from 'vue'
import { stringifyQuery } from 'vue-router';

const emits = defineEmits(["selected"]);

const filter = reactive({id: '', type: '', name: '', tag: '', query: ''})

const selected: any = reactive({})

function resetSelected() {
    Object.keys(selected).forEach(k => delete selected[k])
}

const props = defineProps({
    selectable: Boolean,
    loading: Boolean,
    actionName: String,
    rules: {
        type: Array<any>,
        required: true
    },
    fields: {
        type: Array<string>,
        validator(value: Array<string>) {
            return !value.some(v => !['id', 'tag', 'query', 'api_id', 'tweet_count'].includes(v))
        },
        default: ['id','tag', 'query', 'tweet_count']
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
const showName = computed(() => props.fields.includes('name'))
const showTag = computed(() => props.fields.includes('tag'))
const showQuery = computed(() => props.fields.includes('query'))
const showTweetCount = computed(() => props.fields.includes('tweet_count'))
const showApiId = computed(() => props.fields.includes('api_id'))
const anySelected = computed(() => Object.keys(selected).length > 0)

function selectedEvent() {
    emits('selected', props.rules.filter(r => selected[r.id]))
    resetSelected()
}

watch(props, () => {
    if(!props.selectable) {
        resetSelected()
    }
})

</script>

<template>
    <div class="table-responsive">
        <h5 class="text-center">{{props.title}}</h5>
        <button v-if="selectable" type="button" class="btn btn-primary mb-1" :disabled="!anySelected" @click="selectedEvent">{{actionName}}</button>
        <button v-if="loading" type="button" class="btn btn-secondary mb-1" :disabled="true" @click="selectedEvent">Loading...</button>
        <table class="table table-striped table-sm text-nowrap table-hover">
            <thead class="table-dark">
                <tr>
                    <th v-if="props.selectable" class="text-center">...</th>
                    <th v-if="showId">ID</th>
                    <th v-if="showName">Name</th>
                    <th v-if="showTag">Tag</th>
                    <th v-if="showQuery">Query</th>
                    <th v-if="showTweetCount">Tweet Count</th>
                    <th v-if="showApiId">API ID</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <th v-if="props.selectable"></th>
                    <th v-if="showId"><input style="max-width: 100px;" type="number" placeholder="ID" class="form-control" v-model="filter.id"></th>
                    <th v-if="showName"><input type="text" placeholder="Name" class="form-control" v-model="filter.name"></th>
                    <th v-if="showTag"><input type="text" placeholder="Tag" class="form-control" v-model="filter.tag"></th>
                    <th v-if="showQuery"><input type="text" placeholder="Query" class="form-control" v-model="filter.query"></th>
                </tr>
                <tr v-for="rule in filteredRules">
                    <td v-if="props.selectable" class="text-center"><input :disabled="loading" type="checkbox" v-model="selected[rule.id]" :value="rule.id"></td>
                    <td v-if="showId">{{rule.id}}</td>
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
/* input {
    min-width: 70px;
} */
/* .table-hover tbody tr:hover td{
  background-color: green;
} */
</style>