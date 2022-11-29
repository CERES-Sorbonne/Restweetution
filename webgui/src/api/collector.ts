import axios from 'axios';
// axios.defaults.headers.common['Access-Control-Allow-Origin'] = '*';


const BASE_URL = '/collector'
let user_id = ''

export function getUsers() {
    return axios.get(BASE_URL + '/users/info')
}

export function selectUser(user: string) {
    user_id = user
}