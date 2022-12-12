<script setup lang="ts">
import {ref, onMounted} from 'vue'
import Streamer from "../components/Streamer.vue"
import Menu from '@/components/Menu.vue';

import {useStore} from '@/stores/store'

const userStore = useStore()


const editStreamerRules = ref(false)
const console = window.console



</script>
<template>
  <div class="row">
    <!-- <div class="col-sm-6"> -->
      <Menu />
      <div v-if="userStore.hasSelectedUser">
        <Streamer :selectedUser="userStore.selectedUser"/>
      </div>
      <div v-else>
        <h1 class="pt-4 text-danger text-center">No User Config Selected !</h1>
      </div>
  </div>
</template>