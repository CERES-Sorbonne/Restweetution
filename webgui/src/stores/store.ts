import { ref, reactive, computed, watch } from "vue";
import { defineStore } from "pinia";
import * as collector from "../api/collector"
import { toDatetimeInputString } from "@/utils";

interface Task {
    updated_at: string
    fields: any
    is_running: boolean
}


interface User {
    name: string
    bearer_token: string
    fields: any
    streamer_config: Task
    searcher_config: Task
}

interface Streamer {
    running: boolean
    active_rules: any[]
    count: number
}

interface Searcher {
    running: boolean
    rule: { query: string, tag: string, id: string }
    time_window: any
}

export interface Notif {
    type: String
    source: String
    message: String
    user_id: String | undefined
}

type UserDict = { [name: string]: User }
type StreamerDict = { [name: string]: Streamer }
type SearcherDict = { [name: string]: Searcher }


export const useStore = defineStore("store", () => {
    const users: UserDict = reactive({})
    const selectedUser = ref('undefined')
    const hasSelectedUser = computed(() => users[selectedUser.value] != undefined)
    const streamers: StreamerDict = reactive({})
    const searchers: SearcherDict = reactive({})
    const rules: any[] = reactive([])
    const notifs: Notif[] = reactive([])

    const searcherNotifs = computed(() => {
        return notifs.filter(n => n.source == 'searcher').filter(n => n.user_id == selectedUser.value)
    })
    const streamerNotifs = computed(() => {
        return notifs.filter(n => n.source == 'streamer').filter(n => n.user_id == selectedUser.value)
    })
    const isLoaded = computed(() => {
        let user_ids = Object.keys(users)
        return !user_ids.some(user_id => streamers[user_id] == undefined)
    })

    function notifyError(message: string, source: string, user_id: any=undefined) {
        let err:Notif = {
            type: 'error',
            source: source,
            message: message,
            user_id: user_id
        }
        notifs.push(err)
    }

    function notifySuccess(message: string, source: string, user_id: any=undefined) {
        let err:Notif = {
            type: 'success',
            source: source,
            message: message,
            user_id: user_id
        }
        notifs.push(err)
    }

    async function loadRules() {
        let res = await collector.getRules()
        console.log(res)
        rules.length = 0
        rules.push(...res.rules)
    }


    async function addRules(rule: any[]) {
        let res = await collector.addRules(rule)
        rules.length = 0
        rules.push(...res.rules)
    }

    const orderedRules = computed(() => [...rules].sort((a, b) => b.tweet_count - a.tweet_count))


    function reset_users() {
        Object.keys(users).forEach(k => delete users[k])
    }

    function load() {
        reset_users()
        collector.getUsers().then((res) => {
            registerUsers(res.data)
        })
    }

    function registerUsers(users_res: UserDict) {
        Object.keys(users_res).forEach(k => {
            users[k] = users_res[k]
            searcherInfo(k)
            streamerInfo(k)
        })
    }

    async function addUser(username: string, bearer_token: string) {
        const users_res = await collector.addUser(username, bearer_token);
        registerUsers(users_res);
        return users_res;
    }

    async function deleteUsers(names: string[]) {
        const users_res = await collector.delUsers(names)
        console.log(users_res)
        reset_users()
        registerUsers(users_res)
        return users_res
    }


    function updateSelectedUserInfo() {
        if (selectedUser.value == undefined || selectedUser.value == 'undefined') {
            return
        }
        console.log(selectedUser.value)
        streamerInfo(selectedUser.value)
        searcherInfo(selectedUser.value)
    }

    watch(selectedUser, () => {
        updateSelectedUserInfo()
        localStorage.setItem('user_id', selectedUser.value)
    })

    async function streamerInfo(user_id: string) {
        try {
            const res = await collector.getStreamerInfo(user_id)
            streamers[user_id] = res
            notifySuccess('Streamer Info Update','streamer', user_id)
        } catch(err:any) {
            notifyError(err.response.data.detail, 'streamer', user_id)
        }
    }

    async function streamerStart(user_id: string) {
        try {
            const res = await collector.streamerStart(user_id)
            streamers[user_id] = res
            notifySuccess('Streamer Start','streamer', user_id)
        } catch(err:any) {
            notifyError(err.response.data.detail, 'streamer')
        }
    }
    
    async function streamerStop(user_id: string) {
        try {
            const res = await collector.streamerStop(user_id)
            streamers[user_id] = res
            notifySuccess('Streamer Stop','streamer', user_id)
        } catch(err:any) {
            notifyError(err.response.data.detail, 'streamer')
        }
    }
    
    async function streamerSetRules(user_id: string, rules: any) {
        try {
            const res = await collector.streamerSetRules(user_id, rules)
            streamers[user_id] = res
            notifySuccess('Streamer Set Rules','streamer', user_id)
        } catch(err:any) {
            notifyError(err.response.data.detail, 'streamer')
        }
    }
    
    async function streamerAddRules(user_id: string, rules: any[]) {
        try {
            const res = await collector.streamerAddRules(user_id, rules)
            streamers[user_id] = res
            notifySuccess('Streamer Add Rules','streamer', user_id)
        } catch(err:any) {
            notifyError(err.response.data.detail, 'streamer')
        }
    }
    
    async function streamerDelRules(user_id: string, ruleIds: number[]) {
        try {
            const res = await collector.streamerDelRules(user_id, ruleIds)
            streamers[user_id] = res
            notifySuccess('Streamer Delete Rules','streamer', user_id)
        } catch(err:any) {
            notifyError(err.response.data.detail, 'streamer')
        }
    }
    
    async function getStreamerDebug(user_id: string) {
        try {
            const res = await collector.getStreamerDebug(user_id)
            return res as { api_rules: any[] }
        } catch(err: any) {
            notifyError(err.response.data.detail, 'streamer')
            throw err
        }
    }
    
    async function verifyQuery(query: any) {
        try {
            if (!hasSelectedUser.value) {
                throw Error('Select a User first to perform verifyQuery')
            }
            const res = await collector.verifyQuery(selectedUser.value, query)
            console.log(res)
            return res as { valid: boolean, error: any }
        } catch(err: any) {
            notifyError(err.response.data.detail, 'verifyQuery')
            throw err
        }
    }

    function updateSearcherInfo(user_id: string, updateUserInfo: Searcher) {
        let time_window = updateUserInfo.time_window
        if(time_window.start) {
            updateUserInfo.time_window.start = toDatetimeInputString(new Date(time_window.start))
        }
        else {
            updateUserInfo.time_window.start = undefined
        }
        
        if(time_window.end) {
            updateUserInfo.time_window.end = toDatetimeInputString(new Date(time_window.end))
        }
        else {
            updateUserInfo.time_window.end = undefined
        }

        searchers[user_id] = updateUserInfo
    }

    async function searcherInfo(user_id: string) {
        try {
            const res = await collector.searcherInfo(user_id)
            updateSearcherInfo(user_id, res)
            notifySuccess('updated searcher info', 'searcher', user_id)
        } catch(err:any) {
            notifyError(err.response.data.detail, 'searcher', user_id)
        }
    }
    
    async function searcherStart(user_id: string) {
        try {
            const res = await collector.searcherStart(user_id)
            updateSearcherInfo(user_id, res)
            notifySuccess('Start searcher', 'searcher', user_id)
        } catch(err:any) {
            console.log(err)
            notifyError(err.response.data.detail, 'searcher', user_id)
        }
    }
    
    async function searcherStop(user_id: string) {
        try {
            const res = await collector.searcherStop(user_id)
            updateSearcherInfo(user_id, res)
            notifySuccess('Searcher Stop', 'searcher', user_id)
        } catch(err:any) {
            notifyError(err.response.data.detail, 'searcher', user_id)
        }
    }
    
    async function searcherSetRule(user_id: string, rule: any) {
        try {
            const res = await collector.searcherSetRule(user_id, rule)
            updateSearcherInfo(user_id, res)
            notifySuccess('Searcher Set Rules', 'searcher', user_id)
        } catch(err:any) {
            notifyError(err.response.data.detail, 'searcher', user_id)
        }
    }
    
    async function searcherDelRule(user_id: string) {
        try {
            const res = await collector.searcherDelRule(user_id)
            updateSearcherInfo(user_id, res)
            notifySuccess('Searcher Remove Rule', 'searcher', user_id)
        } catch(err:any) {
            notifyError(err.response.data.detail, 'searcher', user_id)
        }
    }
    
    async function searcherSetTimeWindow(user_id: string, time_window: any) {
        try {
            const res = await collector.searcherSetTimeWindow(user_id, time_window)
            updateSearcherInfo(user_id, res)
            notifySuccess('Searcher Set TimeWindow', 'searcher', user_id)
        } catch(err:any) {
            notifyError(err.response.data.detail, 'searcher', user_id)
        }
    }

    function updateFromSocket(event: any) {
        let message = event.data
        let update = JSON.parse(message)
        console.log(update)
        if(update.source == 'searcher') {
            console.log('searcher update')
            updateSearcherInfo(update.user_id, update.data)
            // notifySuccess('Searcher Websocket Update','searcher', update.user_id)
        }
        if(update.source == 'streamer') {
            streamers[update.user_id] = update.data
            // notifySuccess('Streamer Websocket Update','streamer', update.user_id)
        }
    }

    

    let usr = localStorage.getItem('user_id')
    if (usr) {
        selectedUser.value = usr
    }

    const connection = new WebSocket("ws://localhost:8000/ws")
    connection.onmessage = updateFromSocket


    return {
        users, load, isLoaded, addUser, deleteUsers, selectedUser, hasSelectedUser,
        verifyQuery,
        streamers, streamerInfo, streamerStart, streamerStop, streamerAddRules, streamerDelRules, streamerSetRules, getStreamerDebug,
        searchers, searcherInfo, searcherStart, searcherStop, searcherSetRule, searcherDelRule, searcherSetTimeWindow, connection,
        rules, loadRules, orderedRules, addRules,
        notifs, searcherNotifs, streamerNotifs
    }
});