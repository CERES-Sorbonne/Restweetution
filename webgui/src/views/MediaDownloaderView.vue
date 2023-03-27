<script setup lang="ts">
import Menu from "../components/Menu.vue"
import DownloadQueue from "@/components/DownloadQueue.vue";
import { useStore } from "@/stores/store";
import { ref } from "vue";
import { downloadMedias } from "@/api/collector";

const mediaKeys = ref('')
const result = ref('')
const store = useStore()

function triggerDownload() {
    let keys = mediaKeys.value.split(',')
    downloadMedias(keys).then(res => result.value = res)
    mediaKeys.value = ''
}

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
        <div class="row">
            <div class="form-group">
                {{ result }} <br />
                <label for="exampleFormControlTextarea1">Trigger Media Key download</label>
                <textarea class="form-control" id="exampleFormControlTextarea1" rows="5" v-model="mediaKeys"></textarea>
                <button class="btn btn-primary" @click="triggerDownload">Submit</button>
            </div>
        </div>
    </div>
</template>