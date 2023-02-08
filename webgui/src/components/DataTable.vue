<script setup lang="ts">

const props = defineProps({
    data: Array<any>,
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
                <tr v-for="data in props.data">
                    <td v-for="f in fields">{{data[f]}}</td>
                </tr>
            </tbody>
        </table>
    </div>
</template>