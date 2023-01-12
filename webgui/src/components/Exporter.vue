<script setup lang="ts">
import { ref } from '@vue/reactivity';


const selectedExporter = ref('')

</script>

<template>
    <form class="row justify-content-md-center">
        <div class="col">
        <div class="input-group mb-3">
            <label class="input-group-text" for="inputGroupSelect01">Exporter</label>
            <select class="form-select" id="inputGroupSelect01" v-model="selectedExporter">
                <option selected value="''">Select Exporter ...</option>
                <option value="csv">CSV</option>
                <option value="elastic">Elastic</option>
            </select>
        </div>
        <div class="row g-1" v-if="selectedExporter == 'elastic'">
            <div class="input-group">
                <div class="input-group-text">Data Index</div>
                <input type="text" class="form-control" placeholder="Index" aria-label="Elastic Index">
            </div>

            <button type="button" class="btn btn-outline-primary mt-2">Export</button>
            <div class="progress mt-3">
                <div class="progress-bar progress-bar-striped progress-bar-animatedd" role="progressbar" :aria-valuenow="70" aria-valuemin="0" aria-valuemax="100" :style="'width: ' + 70 +'%'"></div>
            </div> 
        </div>
        </div>
    </form>
</template>