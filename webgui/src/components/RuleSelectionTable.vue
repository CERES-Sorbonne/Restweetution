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
    actionName: {type: String, default: undefined}
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
                <th scope="col">ID</th>
                <th scope="col">Tags</th>
                <th scope="col">Count</th>
                <th v-if="props.actionName" scope="col" class="text-end">Action</th>
                </tr>
            </thead>
            <tbody class="">
                <template v-for="rule in rules">
                    <tr @click="expand(rule.id)" role='button'>
                        <th scope="row" class="align-middle">{{rule.id}}</th>
                        <td class="align-middle user-select-none">{{rule.tag}}</td>
                        <td class="align-middle user-select-none">{{ rule.tweet_count }}</td>
                        <td v-if="props.actionName" class="text-end"><button @click.stop="$emit('select', rule)" type="button" class="btn btn-light btn-sm">{{actionName}}</button></td>
                    </tr>
                    <tr v-if="(expanded == rule.id)">
                        <td colspan="3"><i @click="copyClipboard(rule.query, rule.id)" :class="'btn bi bi-' + (copied == rule.id ? 'clipboard-check' : 'clipboard') + ' me-2'" style="cursor:pointer;"></i>{{rule.query}}</td>
                    </tr>
                </template>
            </tbody>
        </table>
    </div>
</template>