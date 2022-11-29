import axios from 'axios';
// axios.defaults.headers.common['Access-Control-Allow-Origin'] = '*';


const BASE_URL = '/collector'

export function getUsers() {
    return axios.get(BASE_URL + '/users/info')
}