import request from '../utils/http'

export const getTeacherCategoryAPI = () => {
    return request({
        url: '/api/community/mentors/domains',
        method: 'GET',
    })
}

export const getTeacherListAPI = () => {
    return request({
        url:'/api/community/mentors/search',
        method: 'get'
    })
}

export const createTeacherAPI = (mentor_id) => {
    return request({
        url: `/api/community/mentors/${mentor_id}/request`,
        method: 'post'
    })
}

export const myTeacherListAPI = () => {
    return request({
        url: '/api/community/mentors/my',
        method: 'get'
    })
}