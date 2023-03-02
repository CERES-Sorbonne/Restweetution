<script setup lang="ts">

const props = defineProps({
    tweets: Array<any>,
    fields: Array<string>
})

</script>

<template>
    <div class="table-responsive">
        <table class="table table-sm" @click="">
            <thead>
                <tr>
                <th scope="col" v-for="field in props.fields">{{field}}</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="tweet in props.tweets">
                    <td v-for="f in fields">{{tweet[f]}}</td>
                </tr>
            </tbody>
        </table>
    </div>
</template>