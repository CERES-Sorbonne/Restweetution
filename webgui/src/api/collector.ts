import type { CollectTasks } from '@/stores/store';
import axios from 'axios';

export interface RuleInfo {
    id: number
    tag: string
    query: string
    created_at: string
    count_estimate: number
}

export interface CountRequest {
    query: string
    start?: Date
    end?: Date
    recent?: boolean
}

export interface CountPoint {
    date: string
    count: number
}

export interface CountResult {
    total: number
    points: CountPoint[]
    query: string,
}



export interface DownloadQueueStatus {
    qsize: number
    current_url: number
    bytes_downloaded: number
    bytes_total: number
    progress_percentage: number
    downloaded_count: number
}

export interface MediaDownloaderStatus {
    photo: DownloadQueueStatus
    video: DownloadQueueStatus
    gif: DownloadQueueStatus
}

export const BASE_URL = '/collector_api'
let user_id = ''

// console.log(BASE_URL)

export function getUsers() {
    return axios.get(BASE_URL + '/users/info')
}

export function selectUser(user: string) {
    user_id = user
}

export async function addUser(userName: string, bearer_token: string) {
    const res = await axios.post(BASE_URL + '/users/add', { name: userName, bearer_token: bearer_token });
    return res.data;
}

export async function delUsers(names: string[]) {
    const res = await axios.post(BASE_URL + '/users/del', names);
    return res.data;
}

export async function getRules() {
    const res = await axios.get(BASE_URL + '/rules/info');
    const ruleInfos = res.data as RuleInfo[]
    ruleInfos.forEach(r => r.count_estimate = Number(r.count_estimate))
    ruleInfos.forEach(r => r.id = Number(r.id))
    return ruleInfos
}

export async function getStreamerInfo(user:string) {
    const res = await axios.get(BASE_URL + '/streamer/info/' + user)
    return res.data
}

export async function streamerStart(user:string) {
    const res = await axios.post(BASE_URL + '/streamer/start/' + user)
    return res.data
}

export async function streamerStop(user:string) {
    const res = await axios.post(BASE_URL + '/streamer/stop/' + user)
    return res.data
}

export async function streamerSetRules(user:string, rules:any) {
    const res = await axios.post(BASE_URL + '/streamer/set/rules/' + user, rules)
    return res.data
}

export async function streamerAddRules(user:string, rules:any[]) {
    const res = await axios.post(BASE_URL + '/streamer/add/rules/' + user, rules)
    return res.data
}

export async function streamerDelRules(user:string, ruleIds:number[]) {
    const res = await axios.post(BASE_URL + '/streamer/del/rules/' + user, ruleIds)
    return res.data
}

export async function streamerSetCollectTasks(user:string, tasks: CollectTasks) {
    const res = await axios.post(BASE_URL + '/streamer/set/collect_options/' + user, tasks)
    return res.data
}

export async function streamerVerify(user:string) {
    const res = await axios.post(BASE_URL + '/streamer/verify/' + user)
    console.log(res.data)
    return res.data
}

export async function streamerSync(user:string) {
    const res = await axios.post(BASE_URL + '/streamer/sync/' + user)
    return res.data
}


export async function verifyQuery(user: string, query:any) {
    const res = await axios.post(BASE_URL + '/rules/test/' + user, query)
    return res.data
}

export async function addRules(rules: any[]) {
    const res = await axios.post(BASE_URL + '/rules/add', rules)
    return res.data
}

export async function searcherInfo(user_id: string) {
    const res = await axios.get(BASE_URL + '/searcher/info/' + user_id)
    return res.data
}

export async function searcherStart(user_id: string) {
    const res = await axios.post(BASE_URL + '/searcher/start/' + user_id)
    return res.data
}

export async function searcherStop(user_id: string) {
    const res = await axios.post(BASE_URL + '/searcher/stop/' + user_id)
    return res.data
}

export async function searcherSetRule(user_id: string, rule:any) {
    const res = await axios.post(BASE_URL + '/searcher/set/rule/' + user_id, rule)
    return res.data
}

export async function searcherDelRule(user_id: string) {
    const res = await axios.post(BASE_URL + '/searcher/del/rule/' + user_id)
    return res.data
}

export async function searcherSetTimeWindow(user_id: string, time_window:any) {
    const res = await axios.post(BASE_URL + '/searcher/set/time/' + user_id, time_window)
    return res.data
}

export async function searcherSetCollectTasks(user:string, tasks: CollectTasks) {
    const res = await axios.post(BASE_URL + '/searcher/set/collect_options/' + user, tasks)
    return res.data
}

export async function searcherCount(user: string, countRequest: CountRequest) {
    const res = await axios.post(BASE_URL + '/searcher/count/' + user, countRequest)
    return res.data as CountResult
}

export async function downloaderInfo() {
    const res = await axios.get(BASE_URL + '/downloader/info')
    return res.data as MediaDownloaderStatus
}

export async function downloadMedias(media_keys: Array<string>) {
    const res = await axios.post(BASE_URL + '/download/medias', media_keys)
    return res.data
}