<script setup lang="ts">
import Menu from "../components/Menu.vue"

import { useStore } from "@/stores/store";

const store = useStore()


</script>
<template>
    <Menu />
    <div v-if="store.isLoaded">
        <h1 class="text-center">Media Downloader</h1>
    </div>
</template>