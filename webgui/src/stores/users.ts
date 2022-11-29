import { ref, reactive, computed } from "vue";
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

export const useUserStore = defineStore("users", () => {
  const users: {[name:string]: User} = reactive({})

  function reset_users() {
    Object.keys(users).forEach(k => delete users[k])
  }

  function load() {
    reset_users()
    collector.getUsers().then((res) => {
      Object.keys(res.data).forEach(k => users[k] = res.data[k])
    })
  }

  return {users, load}
});
