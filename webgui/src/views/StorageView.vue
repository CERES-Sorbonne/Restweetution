<script setup lang="ts">
import Menu from "../components/Menu.vue"
import RuleTable from "../components/RuleTable.vue"

import { computed, reactive, ref } from "@vue/reactivity";
import { watch } from "vue";
import { useStore } from "@/stores/store";
import DiscoverTweets from "@/components/DiscoverTweets.vue";

const store = useStore()


</script>
<template>
    <Menu />
    <div v-if="store.isLoaded">
        <h1 class="text-center">Storage</h1>
        <DiscoverTweets />
    </div>
</template>