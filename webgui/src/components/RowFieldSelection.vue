<script setup lang="ts">

import { toDatetimeInputString } from '@/utils';
import { computed, reactive, ref } from '@vue/reactivity';
import { onMounted, watch } from 'vue';
import type { CollectTasks } from '@/stores/store'

const emits = defineEmits(["submit"]);

const props = defineProps({
    fields: {
        type: Array<string>,
        default: ['id', 'author_username', 'text']
    }
})

const possibleFields = ['id', 'text', 'media_keys', 'media_sha1s', 'media_format', 'media_files', 'media_types', 'poll_ids', 'author_id', 'author_username', 'context_domains', 'context_entities', 'conversation_id', 'created_at', 'annotations', 'cashtags', 'hashtags', 'mentions', 'urls', 'urls_domain', 'coordinates', 'place_id', 'in_reply_to_user_id', 'in_reply_to_username', 'lang', 'possibly_sensitive', 'retweet_count', 'reply_count', 'like_count', 'quote_count', 'referenced_tweets_types', 'referenced_tweets_ids', 'referenced_tweets_authors', 'referenced_tweets_authors_usernames', 'reply_settings', 'source', 'withheld_copyright', 'withheld_country_codes', 'withheld_scope', 'rule_tags']

function check(field: string) {
    if(props.fields.includes(field)) {
        let index = props.fields.indexOf(field)
        props.fields.splice(index,1)
    }
    else {
        props.fields.push(field)
    }
}

function checkAll() {
    props.fields.length = 0
    props.fields.push(...possibleFields)
}

function checkNone() {
    props.fields.length = 0
}

</script>

<template>
    <ul class="list-group">
        <div class="input-group mb-2">
            <button @click="checkAll" class="btn btn-outline-dark form-control">All</button>
            <button @click="checkNone" class="btn btn-outline-dark form-control">None</button>
        </div>
        <li v-for="field in possibleFields" class="list-group-item">
            <input class="form-check-input me-1" type="checkbox" :checked="props.fields.includes(field)" @click="check(field)">
            {{field}}
        </li>
    </ul>
</template>