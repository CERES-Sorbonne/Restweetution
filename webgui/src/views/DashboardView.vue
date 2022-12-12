<script setup lang="ts">
import {ref, onMounted} from 'vue'
import Menu from '@/components/Menu.vue';
import Notifications from '@/components/Notifications.vue';
import { useStore } from '@/stores/store';

const store = useStore()

</script>
<template>
    <Menu />
    <div class="row">
        <div class="col" v-if="store.isLoaded">
            <div class="row mt-4" v-for="user in store.users">
                <h5 class="">{{user.name}}</h5>
                <div class="col">
                    Streamer: 
                    <span class="text-success" v-if="store.streamers[user.name].running">Collecting</span>
                    <span class="text-warning" v-else>Paused</span>
                </div>
                <div class="col">
                    Searcher: 
                    <span class="text-success" v-if="store.searchers[user.name].running">Collecting</span>
                    <span class="text-warning" v-else>Paused</span>
                </div>
            </div>
        </div>
        <div class="col overflow-scroll" style="max-height:600px;">
            <Notifications :notifications="store.notifs"/>
        </div>
    </div>
</template>