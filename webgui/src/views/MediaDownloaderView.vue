<script setup lang="ts">
import Menu from "../components/Menu.vue"
import DownloadQueue from "@/components/DownloadQueue.vue";
import { useStore } from "@/stores/store";
import { ref, reactive } from "vue";
import { downloadMedias } from "@/api/collector";

const mediaKeys = ref('')
const result: any = reactive([])
const store = useStore()

async function triggerDownload() {
    let keys = mediaKeys.value.split(',')
    console.log('parsed keys')

    await iterateArrayInChunks(keys, 2, async (keyChunk: Array<string>) => {
        let res = await downloadMedias(keyChunk)
        result.push(res)
    })

    mediaKeys.value = ''
}

async function iterateArrayInChunks(array: any, chunkSize: any, callback: CallableFunction) {
  for (let i = 0; i < array.length; i += chunkSize) {
    const chunk = array.slice(i, i + chunkSize);
    await callback(chunk);
  }
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
                <p v-for="r in result">{{ r }}</p>
                <label for="exampleFormControlTextarea1">Trigger Media Key download</label>
                <textarea class="form-control" id="exampleFormControlTextarea1" rows="5" v-model="mediaKeys"></textarea>
                <button class="btn btn-primary" @click="triggerDownload">Submit</button>
            </div>
        </div>
    </div>
</template>