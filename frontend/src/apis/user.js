//封装所有和用户相关的接口函数
import request from '../utils/http'
import qs from 'qs'

// 登录接口
export const LoginAPI = ({username,password}) =>{
    return request({
        url: '/api/auth/login',
        method:'post',
        data:qs.stringify({username,password}),
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    })
}


//注册接口
export const RegisterAPI = ({username,nickname,email,password}) => {
    return request({
        url: '/api/auth/register',
        method: 'post',
        data: qs.stringify({
            username,
            nickname,
            email,
            password
        }),
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    })
}

//退出登录接口
export const LoginOutAPI = () => {
    return request({
        url: '/api/auth/logout',
        method: 'post',
         headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    })
}
