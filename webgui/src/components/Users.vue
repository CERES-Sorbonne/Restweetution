<script setup lang="ts">
import { ref, reactive } from 'vue'
import RuleTable from './RuleTable.vue'
import {useUserStore} from '@/stores/users'

const store = useUserStore()

</script>

<template>
    <h2 class="text-center">Users</h2>
    <div>
        <div v-for="user in store.users">
            <h3>{{user.name}}</h3>
            <h4>{{user.bearer_token}}</h4>
        </div>
    </div>
   </template>