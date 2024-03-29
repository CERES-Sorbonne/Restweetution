import { ref, reactive, computed, watch } from "vue";
import { defineStore } from "pinia";
import * as api from "../api/collector"
import { toDatetimeInputString } from "@/utils";
import type { RuleInfo } from "../api/collector";

interface Task {
    updated_at: string
    fields: any
    is_running: boolean
}

export interface CollectTasks {
    download_photo: boolean
    download_video: boolean
    download_gif: boolean
    elastic_dashboard: boolean
    elastic_dashboard_name: String
}

// export interface Rule {
//     id: number
//     tag: string
//     query: string
// }

interface User {
    name: string
    bearer_token: string
    fields: any
    streamer_state: Task
    searcher_state: Task
}

interface APIRule {
    id: string
    value: string
    tag: string
}

interface Streamer {
    running: boolean
    active_rules: any[]
    count: number
    collect_options: CollectTasks
    conflict: boolean
    api_rules: APIRule[]
}

interface Searcher {
    running: boolean
    sleeping: boolean
    rule: { query: string, tag: string, id: string }
    time_window: any
    collect_options: CollectTasks
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
    const rules: api.RuleInfo[] = reactive([])
    const notifs: Notif[] = reactive([])
    const downloader = <api.MediaDownloaderStatus >reactive({})
    
    const loadedRules = ref(false)

    const ruleFromId: {[id: number]: RuleInfo} = {}

    const searcherNotifs = computed(() => {
        return notifs.filter(n => n.source == 'searcher').filter(n => n.user_id == selectedUser.value)
    })
    const streamerNotifs = computed(() => {
        return notifs.filter(n => n.source == 'streamer').filter(n => n.user_id == selectedUser.value)
    })
    const isLoaded = computed(() => {
        let user_ids = Object.keys(users)
        return !user_ids.some(user_id => streamers[user_id] == undefined) && loadedRules.value
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
        let res = await api.getRules()
        // console.log(res)
        rules.length = 0
        rules.push(...res)

        const idToRule:{ [id: string] : api.RuleInfo; } = {}
        rules.forEach(r => idToRule[r.id] = r)
        
        Object.assign(ruleFromId, idToRule)
        loadedRules.value = true
    }


    async function addRules(rule: any[]) {
        let res = await api.addRules(rule)
        console.log(res)
        rules.length = 0
        rules.push(...res)
    }

    const orderedRules = computed(() => [...rules].sort((a, b) => b.count_estimate - a.count_estimate))
    const rulesOrderId = computed(() => [...rules].sort((a, b) => a.id - b.id))


    function reset_users() {
        Object.keys(users).forEach(k => delete users[k])
    }

    function load() {
        reset_users()
        downloaderInfo()
        api.getUsers().then((res) => {
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
        const users_res = await api.addUser(username, bearer_token);
        registerUsers(users_res);
        return users_res;
    }

    async function deleteUsers(names: string[]) {
        const users_res = await api.delUsers(names)
       // console.log(users_res)
        reset_users()
        registerUsers(users_res)
        return users_res
    }


    function updateSelectedUserInfo() {
        if (selectedUser.value == undefined || selectedUser.value == 'undefined') {
            return
        }
        //console.log(selectedUser.value)
        streamerInfo(selectedUser.value)
        searcherInfo(selectedUser.value)
    }

    watch(selectedUser, () => {
        updateSelectedUserInfo()
        localStorage.setItem('user_id', selectedUser.value)
    })

    async function streamerInfo(user_id: string) {
        try {
            const res = await api.getStreamerInfo(user_id)
            streamers[user_id] = res
            notifySuccess('Streamer Info Update','streamer', user_id)
        } catch(err:any) {
            notifyError(err.response.data.detail, 'streamer', user_id)
        }
    }

    async function streamerStart(user_id: string) {
        try {
            const res = await api.streamerStart(user_id)
            streamers[user_id] = res
            notifySuccess('Streamer Start','streamer', user_id)
        } catch(err:any) {
            notifyError(err.response.data.detail, 'streamer')
        }
    }
    
    async function streamerStop(user_id: string) {
        try {
            const res = await api.streamerStop(user_id)
            streamers[user_id] = res
            notifySuccess('Streamer Stop','streamer', user_id)
        } catch(err:any) {
            notifyError(err.response.data.detail, 'streamer')
        }
    }
    
    async function streamerSetRules(user_id: string, rules: any) {
        try {
            const res = await api.streamerSetRules(user_id, rules)
            streamers[user_id] = res
            notifySuccess('Streamer Set Rules','streamer', user_id)
        } catch(err:any) {
            notifyError(err.response.data.detail, 'streamer')
        }
    }
    
    async function streamerAddRules(user_id: string, rules: any[]) {
        try {
            const res = await api.streamerAddRules(user_id, rules)
            streamers[user_id] = res
            notifySuccess('Streamer Add Rules','streamer', user_id)
        } catch(err:any) {
            notifyError(err.response.data.detail, 'streamer')
        }
    }
    
    async function streamerDelRules(user_id: string, ruleIds: number[]) {
        try {
            const res = await api.streamerDelRules(user_id, ruleIds)
            streamers[user_id] = res
            notifySuccess('Streamer Delete Rules','streamer', user_id)
        } catch(err:any) {
            notifyError(err.response.data.detail, 'streamer')
        }
    }
    
    async function streamerVerify(user_id: string) {
        try {
            const res = await api.streamerVerify(user_id)
            streamers[user_id] = res
            return streamers[user_id]
        } catch(err: any) {
            notifyError(err.response.data.detail, 'streamer')
            throw err
        }
    }

    async function streamerSync(user_id: string) {
        try {
            const res = await api.streamerSync(user_id)
            streamers[user_id] = res
        } catch(err: any) {
            notifyError(err.response.data.detail, 'streamer')
            throw err
        }
    }

    async function streamerSetCollectTasks(user_id: string, tasks: CollectTasks) {
        try {
            const res = await api.streamerSetCollectTasks(user_id, tasks)
            streamers[user_id] = res
        } catch (err: any) {
            notifyError(err.response.data.detail, 'streamer')
            throw err
        }
    }
    
    async function verifyQuery(query: any) {
        try {
            if (!hasSelectedUser.value) {
                throw Error('Select a User first to perform verifyQuery')
            }
            const res = await api.verifyQuery(selectedUser.value, query)
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
            const res = await api.searcherInfo(user_id)
            updateSearcherInfo(user_id, res)
            notifySuccess('updated searcher info', 'searcher', user_id)
        } catch(err:any) {
            notifyError(err.response.data.detail, 'searcher', user_id)
        }
    }
    
    async function searcherStart(user_id: string) {
        try {
            const res = await api.searcherStart(user_id)
            updateSearcherInfo(user_id, res)
            notifySuccess('Start searcher', 'searcher', user_id)
        } catch(err:any) {
            console.log(err)
            notifyError(err.response.data.detail, 'searcher', user_id)
        }
    }
    
    async function searcherStop(user_id: string) {
        try {
            const res = await api.searcherStop(user_id)
            updateSearcherInfo(user_id, res)
            notifySuccess('Searcher Stop', 'searcher', user_id)
        } catch(err:any) {
            notifyError(err.response.data.detail, 'searcher', user_id)
        }
    }
    
    async function searcherSetRule(user_id: string, rule: any) {
        try {
            const res = await api.searcherSetRule(user_id, rule)
            updateSearcherInfo(user_id, res)
            notifySuccess('Searcher Set Rules', 'searcher', user_id)
        } catch(err:any) {
            notifyError(err.response.data.detail, 'searcher', user_id)
        }
    }
    
    async function searcherDelRule(user_id: string) {
        try {
            const res = await api.searcherDelRule(user_id)
            updateSearcherInfo(user_id, res)
            notifySuccess('Searcher Remove Rule', 'searcher', user_id)
        } catch(err:any) {
            notifyError(err.response.data.detail, 'searcher', user_id)
        }
    }
    
    async function searcherSetTimeWindow(user_id: string, time_window: any) {
        try {
            const res = await api.searcherSetTimeWindow(user_id, time_window)
            updateSearcherInfo(user_id, res)
            notifySuccess('Searcher Set TimeWindow', 'searcher', user_id)
        } catch(err:any) {
            notifyError(err.response.data.detail, 'searcher', user_id)
        }
    }

    async function searcherSetCollectTasks(user_id: string, tasks: CollectTasks) {
        try {
            const res = await api.searcherSetCollectTasks(user_id, tasks)
            updateSearcherInfo(user_id, res)
        } catch (err: any) {
            notifyError(err.response.data.detail, 'searcher')
            throw err
        }
    }

    async function downloaderInfo() {
        try {
            const res = await api.downloaderInfo()
            Object.assign(downloader, res)
        } catch (err: any) {
            notifyError(err.response.data.detail, 'downloader')
            throw err
        }
    }

    function updateFromSocket(event: any) {
        let message = event.data
        let update = JSON.parse(message)
        // console.log(update)
        if(update.source == 'searcher') {
            console.log('searcher update')
            updateSearcherInfo(update.user_id, update.data)
            // notifySuccess('Searcher Websocket Update','searcher', update.user_id)
        }
        if(update.source == 'streamer') {
            streamers[update.user_id] = update.data
            // notifySuccess('Streamer Websocket Update','streamer', update.user_id)
        }
        if(update.source == 'downloader') {
            Object.assign(downloader, update.data)
        }
    }

    

    let usr = localStorage.getItem('user_id')
    if (usr) {
        selectedUser.value = usr
    }

    let socketPrefix = 'ws'
    if(window.location.protocol == 'https:') {
        socketPrefix = 'wss'
    }

    const connection = new WebSocket(socketPrefix + "://" + location.host + api.BASE_URL + "/ws");
    connection.onmessage = updateFromSocket


    return {
        users, load, isLoaded, addUser, deleteUsers, selectedUser, hasSelectedUser,
        verifyQuery,
        streamers, streamerInfo, streamerStart, streamerStop, streamerAddRules, streamerDelRules, streamerSetRules, 
        streamerVerify, streamerSync, streamerSetCollectTasks,
        searchers, searcherInfo, searcherStart, searcherStop, searcherSetRule, searcherDelRule, searcherSetTimeWindow, 
        searcherSetCollectTasks,
        rules, loadRules, orderedRules, addRules, rulesOrderId, ruleFromId,
        notifs, searcherNotifs, streamerNotifs,
        downloader, downloaderInfo,
        connection,
    }
});
