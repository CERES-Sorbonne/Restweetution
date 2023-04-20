<script setup lang="ts">
import { ref, reactive } from 'vue'
import { computed } from '@vue/reactivity';
import type { RuleInfo } from '@/api/collector';


function copyClipboard(value: string, id: number) {
    navigator.clipboard.writeText(value);
    copied.value = id
}

const props = defineProps({
    rules: Array<RuleInfo>,
    actionName: {type: String, default: undefined},
    showAction: {type: Boolean, default: true}
})

const filter = ref('')



function containsTag(filter:string, target:string) {
    let t1 = filter.toUpperCase().split(',').map(v => v.replace(' ', ''))
    console.log(t1)
    let t2 = target.toUpperCase().split(',').map(v => v.replace(' ', ''))
    // console.log(t2)
    return t1.some(tag => t2.some(tag2 => tag2.match(tag)))
}

const filteredRules = computed(() => {
    if(props.rules == undefined) {
        return undefined
    }
    if(filter.value == '') {
        return props.rules
    }
    let filtered = props.rules.filter(r => containsTag(filter.value, r.tag))
    return filtered
})


const expanded = ref(-1)
const copied = ref(-1)

function expand(id: number) {
    if(expanded.value == id) {
        expanded.value = -1
    }
    else {
        expanded.value = id
    }
}

</script>

<template>
    <div class="table-responsive">
        <table class="table table-sm table-hover">
            <thead>
                <tr>
                <th scope="col">
                    <div class="input-group">
                        <label class="input-group-text">ID</label>
                    </div>
                </th>
                <th scope="col">
                    <div class="input-group">
                        <label class="input-group-text">Tags</label>
                        <input type="text" v-model="filter" class="form-control" placeholder="Filter"/>
                    </div>
                </th>
                <th scope="col">
                    <div class="input-group">
                        <label class="input-group-text">Count</label>
                    </div>
                </th>
                <th v-if="props.actionName && showAction" scope="col" class="text-end">
                    <div class="input-group">
                        <label class="input-group-text">Action</label>
                    </div>
                </th>
                </tr>
            </thead>
            <tbody class="">
                <template v-for="rule in filteredRules">
                    <tr @click="expand(rule.id)" role='button'>
                        <th scope="row" class="align-middle">{{rule.id}}</th>
                        <td class="align-middle user-select-none" style="width: 100%;">{{rule.tag}}</td>
                        <td class="align-middle user-select-none text-end">{{ rule.tweet_count }}</td>
                        <td v-if="props.actionName && showAction" class="text-center"><button @click.stop="$emit('select', rule)" type="button" class="btn btn-light btn-sm">{{actionName}}</button></td>
                    </tr>
                    <tr v-if="(expanded == rule.id)">
                        <td><i @click="copyClipboard(rule.query, rule.id)" :class="'btn btn-sm bi bi-' + (copied == rule.id ? 'clipboard-check' : 'clipboard') + ' me-2'" style="cursor:pointer;"></i></td>
                        <td colspan="1">{{rule.query}}</td>
                    </tr>
                </template>
            </tbody>
        </table>
    </div>
</template>