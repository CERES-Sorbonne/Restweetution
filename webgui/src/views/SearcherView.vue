<script setup lang="ts">
import {ref, onMounted} from 'vue'
import Menu from '@/components/Menu.vue';
import Searcher from '@/components/Searcher.vue';

import {useStore} from '@/stores/store'

const store = useStore()


const editStreamerRules = ref(false)
const console = window.console



</script>
<template>
  <div class="row">
    <!-- <div class="col-sm-6"> -->
      <Menu />
      <div v-if="store.isLoaded">
        <Searcher :selectedUser="store.selectedUser"/>
      </div>
      <div v-else>
        <h1 class="text-center pt-4 text-info">Loading ...</h1>
      </div>
      <div v-if="store.isLoaded && store.selectedUser == 'undefined'">
        <h1 class="pt-4 text-danger text-center">No User Config Selected !</h1>
      </div>
  </div>
</template>