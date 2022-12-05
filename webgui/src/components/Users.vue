<script setup lang="ts">
import { ref, reactive } from 'vue'
import RuleTable from './RuleTable.vue'
import {useUserStore} from '@/stores/users'
import { computed } from '@vue/reactivity';
import { stringifyQuery } from 'vue-router';

const store = useUserStore()

function copyToken(token: string) {
    navigator.clipboard.writeText(token);
}

const edit = ref(false)
const selected: {[name: string]: boolean} = reactive({})
const allSelected = ref(false)
const newUser = reactive({name: '', bearer_token: ''})

function triggerSelectAll() {
    if(allSelected.value) {
        Object.assign(selected, {})
        Object.keys(store.users).forEach(user => selected[user] = true)
    }
    else {
        Object.keys(store.users).forEach(u => delete selected[u])
    }
}

function triggerSelect(user_id: string) {
    if(!selected[user_id]) {
        delete selected[user_id]
    }
    if(!selected[user_id] && allSelected) {
        allSelected.value = false
    }
    else if(Object.keys(selected).length == Object.keys(store.users).length) {
        allSelected.value = true
    }
}

function cleanNewUser() {
    newUser.bearer_token = ''
    newUser.name = ''
}

function triggerEdit() {
    edit.value = !edit.value
    if(!edit.value) {
        allSelected.value = false
        triggerSelectAll()
        cleanNewUser()
    }
}

function addUser() {
    if(!newUserValid) {
        return
    }

    store.addUser(newUser.name, newUser.bearer_token).then(x => cleanNewUser())
}

function deleteSelectedUsers(){
    let selectedUsers = Object.keys(selected).filter(s => selected[s])
    store.deleteUsers(selectedUsers)
} 

function cleanSelected() {
    Object.keys(selected).forEach(k => {
        if(!store.users[k]) {
            delete selected[k]
        }
    })
}

const anySelected = computed(() => {
    return Object.keys(selected).length > 0
})

const newUserValid = computed(() => {
    return newUser.name != '' && newUser.bearer_token != ''
})

</script>

<template>
    <br />
    <h2 class="text-center">Users</h2>
    <br />
    <div class="text-left pb-1">
        <button type="button" class="btn btn-primary" @click="triggerEdit">{{edit ? 'Stop Edit' : 'Edit'}}</button>
        <span v-if="edit">
        <button type="button" class="btn btn-primary ms-1" :disabled="!anySelected" @click="deleteSelectedUsers">Delete</button>
        <button type="button" class="btn btn-primary ms-1" :disabled="!newUserValid" @click="addUser"> Add</button>
        <div class="input-group pt-2 pb-1">
        <span class="input-group-text">New User</span>
            <input type="text" v-model="newUser.name" class="form-control" placeholder="Unique Name">
            <input type="text" v-model="newUser.bearer_token" class="form-control w-50" placeholder="bearer_token">
        </div>
        <!-- <input type="text" v-model="newUser.name" name="name" class="" placeholder="Unique Name" /> -->
        <!-- <input type="text" v-model="newUser.bearer_token" name="bearer_token" class="" placeholder="bearer_token" /> -->
        </span>
    </div>
    <!-- <div class="row"> -->
        <!-- <div class="col-sm-1"><button type="button" class="btn btn-primary" @click="triggerEdit"><span v-if="!edit">Edit</span><span v-if="edit">Stop Edit</span></button></div> -->
        <!-- <div class="col-sm-1"><button :disabled="!anySelected" type="button" class="btn btn-primary" @click="deleteSelectedUsers">Delete</button></div> -->
        <!-- <div class="col-sm-1 gl-1"><button :disabled="!newUserValid" type="button" class="btn btn-primary" @click="addUser">Add</button></div> -->
        <!-- <div class="col-sm-3 g-0"> -->
            <!-- <input type="text" v-model="newUser.name" name="name" class="form-control" placeholder="Unique Name"> -->
        <!-- </div> -->
        <!-- <div class="col-sm-5 g-0"> -->
            <!-- <input type="text" v-model="newUser.bearer_token" name="name" class="form-control" placeholder="bearer_token"> -->
        <!-- </div> -->
    <!-- </div> -->
    <!-- <br /> -->
    <div class="table-responsive">
        <table class="table table-striped table-sm text-nowrap table-hover">
            <thead class="table-dark">
                <tr>
                    <th v-if="edit"><input type="checkbox" @change="triggerSelectAll" v-model="allSelected"></th>
                    <th>User</th>
                    <th>Streamer</th>
                    <th>Searcher</th>
                    <th class="text-center">...</th>
                    <th>bearer_token</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="user in store.users">
                    <th v-if="edit"><input type="checkbox" v-model="selected[user.name]" @change="triggerSelect(user.name)"></th>
                    <td>{{user.name}}</td>
                    <td class="text-center">{{user.searcher_task_config.is_running ? 'running' : 'paused'}}</td>
                    <td class="text-center">{{user.searcher_task_config.is_running ? 'running' : 'paused'}}</td>
                    <td class="text-success btn" @click="copyToken(user.bearer_token)">copy</td>
                    <td>{{user.bearer_token}}</td>
                </tr>
            </tbody>
        </table>
    </div>
   </template>