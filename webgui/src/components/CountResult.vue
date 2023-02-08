<script setup lang="ts">

// const props = defineProps({
    
// })

const countResult = {
    tweet: 453001,
    media: 13045,
    users: 245000
}

</script>

<template>
    <div class="input-group">
        <label class="input-group-text bg-success text-white"><i class="bi bi-database-check"></i></label>
        <div class="form-control bg-white text-center">{{ countResult.tweet }}</div>
        <div class="input-group-text bg-success text-white">Tweets</div>
        <div class="form-control bg-white text-center">{{ countResult.users }}</div>
        <div class="input-group-text bg-success text-white">Users</div>
        <div class="form-control bg-white text-center">{{ countResult.media }}</div>
        <div class="input-group-text bg-success text-white">Medias</div>
    </div>

</template>