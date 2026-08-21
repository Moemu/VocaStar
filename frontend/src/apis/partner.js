import request from '../utils/http'

export const getSearchPartnerAPI = () => {
    return request({
        url: '/api/community/partners/search',
        method: 'get'
    })
}

export const getPartnerSkillAPI = () => {
    return request({
        url: '/api/community/partners/hot-skills',
        method: 'get'
    })
}

export const getRecommendPartnerAPI = () => {
    return request({
        url: '/api/community/partners/recommended',
        method: 'get'
    })
}

export const getchoosePartnerAPI = (partner_id) => {
    return request({
        url: `/api/community/partners/${partner_id}/bind`,
        method: 'post'
    })
}

export const getDeletePartnerAPI = (partner_id) => {
    return request({
        url: `/api/community/partners/${partner_id}/bind`,
        method: 'delete'
    })
}

export const getMyPartnerAPI = () => {
    return request({
        url: '/api/community/partners/my',
        method: 'get'
    })
}