import { defineStore } from "pinia";
import { computed, reactive } from "vue";
import * as storage from '@/api/storage'
import type { CollectionDescription, ExportTweetRequest, TaskInfo } from "@/api/types";


export const useStorageStore = defineStore("storageStore", () => {
    const collections: CollectionDescription[] = reactive([])
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

    function loadLocalCollections() {
        let colls = localStorage.getItem('local_collections')
        if(colls) {
            let res = JSON.parse(colls)
            collections.push(...res)
        }
    }

    function createLocalCollection() {
        let baseName = 'collection tmp'
        let counter = 1
        let name = baseName + counter
        while(collections.find(c => c.name == name)) {
            counter++
            name = baseName + counter
        }

        let coll: CollectionDescription = {isGlobal: false, name, rule_ids: [] }
        collections.push(coll)
        return coll
    }

    function updateLocalCollection() {
        let colls = collections.filter(c => !c.isGlobal)
        if(colls) {
            localStorage.setItem('local_collections', JSON.stringify(colls))
        }
    }

    function deleteLocalCollection(name: String) {
        let collIndex = collections.findIndex(c => c.name == name)
        if(collIndex < 0) return

        let coll = collections[collIndex]
        if(coll.isGlobal) return
        collections.splice(collIndex, 1)
    }

    loadTasks()
    loadLocalCollections()

    function updateFromSocket(event: any) {
        let message = event.data
        let update = JSON.parse(message) 
        // console.log(update)
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

    return {
        tasks, tasksReversed, loadTasks, exportTweets,
        collections, createLocalCollection, updateLocalCollection ,deleteLocalCollection,
    }
})