import axios from 'axios';

const BASE_URL = '/collector'
let user_id = ''

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
    const res = await axios.get(BASE_URL + '/rules');
    return res.data;
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

export async function streamerAddRules(user:string, rules:any) {
    const res = await axios.post(BASE_URL + '/streamer/add/rules' + user, rules)
    return res.data
}

export async function streamerDelRules(user:string, ruleIds:number[]) {
    const res = await axios.post(BASE_URL + '/streamer/del/rules' + user, ruleIds)
    return res.data
}