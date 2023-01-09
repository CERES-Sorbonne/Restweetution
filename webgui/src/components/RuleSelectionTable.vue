<script setup lang="ts">
import { ref, reactive } from 'vue'
import { computed } from '@vue/reactivity';
import type { Rule } from '@/stores/store';


function copyToken(token: string) {
    navigator.clipboard.writeText(token);
}

const props = defineProps({
    rules: Array<Rule>,
    actionName: {type: String, default: 'select'}
})

const expanded = ref(-1)

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
        <table class="table table-sm" @click="">
            <thead>
                <tr>
                <th scope="col">ID</th>
                <th scope="col">Tags</th>
                <th scope="col" class="text-end">Action</th>
                </tr>
            </thead>
            <tbody>
                <template v-for="rule in rules">
                    <tr @click="expand(rule.id)">
                        <th scope="row" class="align-middle">{{rule.id}}</th>
                        <td class="align-middle">{{rule.tag}}</td>
                        <td class="text-end"><button @click.stop="$emit('select', rule)" type="button" class="btn btn-light btn-sm">{{actionName}}</button></td>
                    </tr>
                    <tr v-if="(expanded == rule.id)">
                        <td colspan="3">{{rule.query}}</td>
                    </tr>
                </template>
            </tbody>
        </table>
    </div>
</template>