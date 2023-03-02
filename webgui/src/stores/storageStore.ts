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

    function updateFromSocket(event: any) {
        let message = event.data
        let update = JSON.parse(message) 
        console.log(update)
        if(update.source == 'export_tasks') {
            updateTasks(update.data)
        }
    }

    let socketPrefix = 'ws'
    if(window.location.protocol == 'https:') {
        socketPrefix = 'wss'
    }

    const connection = new WebSocket(socketPrefix + "://" + location.host + storage.BASE_URL + "/ws");
    connection.onmessage = updateFromSocket

    return {tasks, tasksReversed, loadTasks, exportTweets}
})