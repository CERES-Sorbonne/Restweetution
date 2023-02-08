import axios from 'axios';
import type { CollectionQuery, ViewQuery } from './types';

export const BASE_URL = '/storage_api'


export async function discoverTweets(query = {}) {
    let res = await axios.post(BASE_URL + '/tweet_discover', query)
    return res.data
}

export async function getTweets(query = {}) {
    let res = await axios.post(BASE_URL + '/tweets', query)
    return res.data
}

export async function getTweetCount(query = {}) {
    let res = await axios.post(BASE_URL + '/tweet_count', query)
    return res.data
}

export async function getTasks() {
    let res = await axios.get(BASE_URL + '/tasks')
    return res.data
}

export async function exportTweets(exportQuery: any) {
    let res = await axios.post(BASE_URL + '/export/tweets', exportQuery)
    return res.data
}

export async function viewMedia(query: ViewQuery) {
    let res = await axios.post(BASE_URL + '/view/', query)
    return res.data
}