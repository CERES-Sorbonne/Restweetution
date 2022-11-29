import { ref, reactive, computed } from "vue";
import { defineStore } from "pinia";
import * as collector from "../api/collector"




interface User {
  name: string
  bearer_token: string
  fields: any
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
