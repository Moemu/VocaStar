import { defineStore } from "pinia";
import { LoginAPI, RegisterAPI, LoginOutAPI } from '../apis/user'
import { ref } from 'vue'

export const useUserStore = defineStore('user',() =>{
    //1。 定义管理用户数据的state
    const userInfo = ref({});
    //定义获取接口数据的action函数
    const getLogin = async ({username,password}) => {
        const res = await LoginAPI({username,password});
        userInfo.value = res.data;
    }

    // 定义注册接口数据的action函数
    const getRegister = async ({username,nickname,email,password}) =>{
        await RegisterAPI({username,nickname,email,password})
    }

    //定义退出登录接口
    const getLoginOut = async () => {
        try{
            await LoginOutAPI();
            // 并且清除token
            userInfo.value = {};
        } catch(err){
            console.error('退出登录失败',err)
        }
    }

    return{ userInfo,
            getLogin,
            getRegister,
            getLoginOut
    }
},{
    persist: true, // 持久化存储
})