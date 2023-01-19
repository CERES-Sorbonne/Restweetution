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
  <div class="row" v-if="store.isLoaded">
    <!-- <div class="col-sm-6"> -->
      <Menu />
      <div v-if="store.hasSelectedUser">
        <Searcher :selectedUser="store.selectedUser"/>
      </div>
      <div v-else>
        <h1 class="pt-4 text-danger text-center">No User Config Selected !</h1>
      </div>
  </div>
</template>