import { ref, reactive, computed, watch } from "vue";
import { defineStore } from "pinia";
import * as collector from "../api/collector"


interface Task {
  updated_at: string
  fields: any
  is_running: boolean
}


interface User {
  name: string
  bearer_token: string
  fields: any
  streamer_task_config: Task
  searcher_task_config: Task
}

interface Streamer {
  running: boolean
  active_rules: any[]
}

type UserDict = {[name:string]: User}
type StreamerDict = {[name: string]: Streamer}

export const useUserStore = defineStore("users", () => {
  const users: UserDict = reactive({})
  const selectedUser = ref('undefined')
  const hasSelectedUser = computed(() => users[selectedUser.value] != undefined)
  const streamers: StreamerDict = reactive({})


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
      Object.keys(users_res).forEach(k => users[k] = users_res[k])
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
    if(selectedUser.value == undefined || selectedUser.value == 'undefined') {
      return
    }
    console.log(selectedUser.value)
    updateStreamerInfo(selectedUser.value)
  }

  watch(selectedUser, updateSelectedUserInfo)

async function updateStreamerInfo(user:string) {
    const res = await collector.getStreamerInfo(user)
    streamers[user] = res
}

async function streamerStart(user:string) {
    const res = await collector.streamerStart(user)
    streamers[user] = res
}

async function streamerStop(user:string) {
  const res = await collector.streamerStop(user)
  streamers[user] = res
}

async function streamerSetRules(user:string, rules:any) {
  const res = await collector.streamerSetRules(user, rules)
  streamers[user] = res
}

async function streamerAddRules(user:string, rules:any[]) {
  const res = await collector.streamerAddRules(user, rules)
  streamers[user] = res
}

async function streamerDelRules(user:string, ruleIds:number[]) {
  const res = await collector.streamerDelRules(user, ruleIds)
  streamers[user] = res
}

async function getStreamerDebug(user:string) {
  const res = await collector.getStreamerDebug(user)
  return res as {api_rules: any[]}
}

async function verifyQuery(query:any) {
  if(!hasSelectedUser.value) {
    throw Error('Select a User first to perform verifyQuery')
  }
  const res = await collector.verifyQuery(selectedUser.value, query)
  console.log(res)
  return res as {valid: boolean, error: any}
}

  return {users, load, addUser, deleteUsers, selectedUser, hasSelectedUser,
    verifyQuery,
    streamers, updateStreamerInfo, streamerStart, streamerStop, streamerAddRules, streamerDelRules, streamerSetRules, getStreamerDebug
  }
});
