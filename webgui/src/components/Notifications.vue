<script setup lang="ts">

import { computed, reactive } from '@vue/reactivity';
import { onMounted, watch } from 'vue';
import type { Notif } from '../stores/store'

const props = defineProps({
    notifications: Array<Notif>
})

function typeToClass(type:String) {
    if(type == 'error') {
        return 'text-danger'
    }
    if(type == 'success') {
        return 'text-success'
    }
    return ''
}

</script>

<template >
    <h5>Nofifications</h5>
    <ol class="list-group">
    <li v-for="notif in props.notifications?.reverse()" class="list-group-item d-flex justify-content-between align-items-start">
        <div class="ms-2 me-auto">
            <div :class="('fw-bold ' + typeToClass(notif.type))">{{notif.type.toUpperCase()}} [{{notif.user_id}}]</div>
            <span class="fw-bold">{{notif.source}}</span> {{notif.message}}
        </div>
        <!-- <span class="badge bg-primary rounded-pill">14</span> -->
    </li>
</ol>
</template>