import { defineStore } from "pinia";
import { reactive } from "vue";
import * as storage from '@/api/storage'
import type { ExportTweetRequest, TaskInfo } from "@/api/types";


export const useStorageStore = defineStore("storageStore", () => {
    const tasks: TaskInfo[] = reactive([])

    function updateTasks(taskList: TaskInfo[]) {
        tasks.length = 0
        tasks.push(...taskList)
    }

    function loadTasks() {
        storage.getTasks().then(updateTasks)
    }

    function exportTweets(request: ExportTweetRequest) {
        storage.exportTweets(request).then(updateTasks)
    }

    loadTasks()

    return {tasks, loadTasks, exportTweets}
})