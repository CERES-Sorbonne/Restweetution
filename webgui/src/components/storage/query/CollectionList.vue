<script setup lang="ts">
import type { CollectionDescription } from '@/api/types';
import { computed, ref } from '@vue/reactivity';
import { onMounted, reactive } from 'vue';

interface LocalCollection extends CollectionDescription {
    all?: Boolean
}


const props = defineProps({
    collections: {type: Array<CollectionDescription>, required: true},
    selectedCollection: {type: Object as () => LocalCollection, required: true}
})

const emits = defineEmits(['createCollection', 'deleteCollection', 'update:selectedCollection', 'edit', 'reset'])

const actionName = computed(() => props.selectedCollection.name ? props.selectedCollection.name : 'Select')


function selectCollection(collection: LocalCollection) {
    emits('update:selectedCollection', collection)
    resetEdit()
}

function resetEdit() {
    emits('reset')
}

function selectAll() {
    selectCollection({name: 'Complete DB', all: true, rule_ids: []})
    resetEdit()
}

function deleteCollection(name: String) {
    emits('deleteCollection', name)
    selectAll()
}

onMounted(() => {
    selectAll()
})

</script>

<template>
    <!-- <label class="input-group-text">Collection</label> -->
    <button class="btn btn-outline-primary dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false" style="width: 250px">
        <i v-if="selectedCollection.isGlobal" class="bi bi-globe2"></i>
        <i v-else-if="selectedCollection.all" class="bi bi-database"></i>
        <i v-else-if="!selectedCollection.isGlobal" class="bi bi-display"></i>
        {{ actionName }}
    </button>
    <ul class="dropdown-menu">
        <li>
            <a href="#" class="dropdown-item" aria-current="true" @click="emits('createCollection')">
                <i class="bi bi-folder-plus me-2"></i> New Collection
            </a>
        </li>
        <li>
            <a href="#" class="dropdown-item" aria-current="true" @click="selectAll">
                <i class="bi bi-database-add me-2"></i> Complete DB
            </a>
        </li>
        <li v-for="collection in props.collections">
            <a href="#" class="dropdown-item" aria-current="true" @click="selectCollection(collection)">
                <i class="bi bi-folder me-2"></i>{{ collection.name }}
            </a>
        </li>
    </ul>
    <button v-if="selectedCollection.name && !selectedCollection.isGlobal && !selectedCollection.all" @click="deleteCollection(selectedCollection.name)" class="btn btn-outline-secondary"><i class="bi bi-trash"></i></button>
    <button v-else class="btn btn-outline-secondary" @click="emits('createCollection')"><i class="bi bi-folder-plus"></i></button>

    <button v-if="!selectedCollection.all" @click="emits('edit')" class="btn btn-outline-secondary"><i class="bi bi-pencil-square"></i></button>
    <label v-else class="input-group-text"><i class="bi bi-pencil-square text-light"></i></label>
    
</template>