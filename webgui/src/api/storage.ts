import axios from 'axios';

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
