<script setup lang="ts">
import {useStore} from '@/stores/store'

const store = useStore()

</script>

<template>
<nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
    <div class="container-fluid">
        <router-link to="/dashboard" class="navbar-brand">Dashboard</router-link>
        <button type="button" class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#navbarCollapse">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarCollapse">
            <div class="navbar-nav">
                <router-link class="nav-item nav-link" to="/users">Users</router-link>
                <router-link class="nav-item nav-link" to="/rules">Rules</router-link>
                <router-link class="nav-item nav-link" to="/errors">Errors</router-link>
                <router-link class="nav-item nav-link" to="/media">Media Downloader</router-link>
                <router-link class="nav-item nav-link" to="/storage">Storage</router-link>
            </div>
            <div class="navbar-nav ms-auto">
                <router-link to="/streamer" v-if="store.hasSelectedUser" class="nav-item nav-link pe-5">Streamer</router-link>
                <router-link to="/searcher" v-if="store.hasSelectedUser" class="nav-item nav-link pe-5">Searcher</router-link>
                <select class="form-select nav-item" aria-label="User Config" v-model="store.selectedUser">
                    <option :value="'undefined'">Select User Config</option>
                    <option v-for="user in store.users" :value="user.name">{{user.name}}</option>
                </select>
            </div>
        </div>
    </div>
</nav>
</template>