import request from '../utils/http'

export function getPlantsAPI(){
    return request({
      url: '/api/career/exploration',
      method : 'get',
    })
}