<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";

import {useRulesStore} from './stores/rules'
import { useUserStore } from "./stores/users";
const store = useRulesStore()
const users_store = useUserStore()

store.loadRules()
users_store.load()

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