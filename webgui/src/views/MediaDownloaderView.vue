<script setup lang="ts">
import Menu from "../components/Menu.vue"
import DownloadQueue from "@/components/DownloadQueue.vue";
import { useStore } from "@/stores/store";

const store = useStore()


</script>
<template>
    <Menu />
    <div v-if="store.isLoaded && store.downloader.photo != undefined">
        <h1 class="text-center">Media Downloader</h1>
        <div class="row">
            <div class="col-4">
                <DownloadQueue :queue="store.downloader.photo" name="Photo Queue"/>
            </div>
            <div class="col-4">
                <DownloadQueue :queue="store.downloader.gif" name="GIF Queue"/>
            </div>
            <div class="col-4">
                <DownloadQueue :queue="store.downloader.video" name="Video Queue"/>
            </div>
        </div>
    </div>
</template>