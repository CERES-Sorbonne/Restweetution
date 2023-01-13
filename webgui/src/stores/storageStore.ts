import { defineStore } from "pinia";
import { computed, reactive } from "vue";
import * as storage from '@/api/storage'
import type { ExportTweetRequest, TaskInfo } from "@/api/types";


export const useStorageStore = defineStore("storageStore", () => {
    const tasks: TaskInfo[] = reactive([])
    const tasksReversed = computed(() => {
        let result: TaskInfo[] = []
        tasks.forEach(t => result.unshift(t))
        return result
    })

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

    return {tasks, tasksReversed, loadTasks, exportTweets}
})