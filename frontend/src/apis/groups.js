import request from '../utils/http'

export const  getGroupsCategoryAPI = () =>{
    return request({
        url: '/api/community/groups/categories',
        method: 'GET',
    })
}

export const  getGroupsAPI = (params) =>{
    return request({
        url: '/api/community/groups',
        method: 'GET',
        params: {
            q: params.q || ''
        }
    })
}

export const  getGroupDetailAPI = (group_id) =>{
    return request({
        url: `/api/community/groups/${group_id}`,
        method: 'GET',
    })
}

export const getGroupMembersAPI = (group_id) =>{
    return request({
        url: `/api/community/groups/${group_id}/members`,
        method: 'GET',
    })
}

export const joinGroupAPI = (group_id) => {
    return request({
        url: `/api/community/groups/${group_id}/join`,
        method: 'POST',
    })
}

export const leaveGroupAPI = (group_id) => {
    return request({
        url: `/api/community/groups/${group_id}/membership`,
        method: 'DELETE',
    })
}

export const myGroupsAPI = () => {
    return request({
        url: '/api/community/groups/my',
        method: 'GET',
    })
}

export const myLikedGroupsAPI = (group_id) => {
    return request({
        url: `/api/community/groups/${group_id}/like`,
        method: 'POST',
    })
}

export const unlikeGroupAPI = (group_id) => {
    return request({
        url: `/api/community/groups/${group_id}/like`,
        method: 'DELETE',
    })
}

export const getCommunityActiveAPI = () => {
    return request({
        url: '/api/community/groups/feed',
        method: 'GET',
    })
}

export const createActiveAPI = (data) => {
    return request({
        url: '/api/community/groups/posts',
        method: 'POST',
        data: {
            group_id: data.group_id,
            title: data.title,
            content: data.content,
            attachments: data.attachments,
        }
    })
}

export const activeLikeAPI = (post_id) => {
    return request({
        url: `/api/community/groups/posts/${post_id}/like`,
        method: 'POST',
    })
}

export const createCommentAPI = (post_id, data) => {
    return request({
        url: `/api/community/groups/posts/${post_id}/comments`,
        method: 'POST',
        data: {
            content: data.content,
        }
    })
}

export const getDatabase = () => {
    return request({
        url: '/api/community/groups/repository',
        method: 'GET',
    })
}

export const uploadAttachmentAPI = (data) => {
    return request({
        url: '/api/community/groups/attachments',
        method: 'POST',
        data: {
            file: data.file,
            type: data.type,
        },
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}


