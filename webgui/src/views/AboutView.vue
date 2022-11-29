<script setup lang="ts">
import {ref, onMounted} from 'vue'
import Streamer from "../components/Streamer.vue"

const editStreamerRules = ref(false)
const console = window.console

</script>
<template>
  <div class="row">
    <!-- <div class="col-sm-6"> -->
      <Streamer />
  </div>
</template>