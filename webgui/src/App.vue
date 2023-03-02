<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";

import { useStore } from "./stores/store";
const store = useStore()

store.loadRules()
store.load()

</script>

<template>

  <div class="container">
      <!-- <HelloWorld msg="You did it!" />
      <nav class="row">
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/about">About</RouterLink>
      </nav> -->

    <RouterView />
  </div>
</template>