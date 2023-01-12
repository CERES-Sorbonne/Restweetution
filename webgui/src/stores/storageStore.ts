import { defineStore } from "pinia";
import { reactive } from "vue";
import * as storage from '@/api/storage'

interface TaskInfo {
    id: number;
    name: string;
    started_at: Date;
    is_running: boolean;
    progress: number;
    result: object;
}

export const useStorageStore = defineStore("storageStore", () => {
    const tasks: TaskInfo[] = reactive([])

    function updateTasks(taskList: TaskInfo[]) {
        tasks.length = 0
        tasks.push(...taskList)
    }

    function loadTasks() {
        storage.getTasks().then(updateTasks)
    }

    function exportTweets(query: any) {
        storage.exportTweets(query).then(updateTasks)
    }

    loadTasks()

    return {tasks, loadTasks, exportTweets}
})