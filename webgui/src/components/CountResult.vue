<script setup lang="ts">import type { ViewCountResult } from '@/api/types';


const props = defineProps({
    count: {type: Number, required: true},
    view: {type: String, required: true}
})

</script>

<template>
    <div class="input-group">
        <label class="input-group-text bg-success text-white"><i class="bi bi-database-check"></i></label>
        <template v-if="props.count">
            <div class="form-control bg-white text-center">{{ props.count }}</div>
            <div class="input-group-text bg-success text-white">{{ view }}</div>
        </template>
        <!-- <div class="form-control bg-white text-center">{{ countResult.users }}</div>
        <div class="input-group-text bg-success text-white">Users</div>
        <div class="form-control bg-white text-center">{{ countResult.media }}</div>
        <div class="input-group-text bg-success text-white">Medias</div> -->
    </div>

</template>