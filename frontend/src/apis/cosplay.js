import request from '../utils/http'

export function getCosplayProfile(){
    return request({
        url: '/api/cosplay/scripts',
        method: 'get'
    })
}

export function getCosPlayList(script_id){
    return request({
        url: `/api/cosplay/scripts/${script_id}`,
        method: 'get'
    })
}

export function getCreateCosplay(script_id){
    return request({
        url: `/api/cosplay/scripts/${script_id}/sessions`,
        method: 'post',
    })
}

export function getCurrentCosplay(session_id){
    return request({
        url: `/api/cosplay/sessions/${session_id}`,
        method: 'get',
    })
}

export function getCosplayChioce({session_id, option_id}){
    return request({
        url:`/api/cosplay/sessions/${session_id}/choice`,
        method: 'post',
        data: JSON.stringify({option_id: option_id}),
        headers: {
            'Content-Type': 'application/json'
        },
    })
}

export function getFinalReport(session_id){
    return request({
        url: `/api/cosplay/sessions/${session_id}/report`,
        method: 'get',
    })
}