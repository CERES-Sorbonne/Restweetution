<script setup lang="ts">

// const props = defineProps({
    
// })

const errorMessage = 'Error message for test'

</script>

<template>
    <div class="input-group">
        <label class="input-group-text bg-danger text-white"><i class="bi bi-database-exclamation"></i></label>
        <div class="form-control bg-white text-danger">{{ errorMessage }}</div>
    </div>

</template>