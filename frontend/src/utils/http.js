import axios from 'axios';
import { ElMessage } from 'element-plus'
import 'element-plus/theme-chalk/el-message.css'
import router from '@/router'
import { useUserStore } from '../stores/user'

// axios的基础配置
const httpInstance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || '',
    timeout: 100000
})

// 添加请求拦截器
httpInstance.interceptors.request.use(function (config) {
    // 在发送请求之前做些什么

    //1. 从pinia获取token数据
    const userStore = useUserStore();
    const token = userStore.userInfo.access_token;
    // console.log('这个是token:',userStore.userInfo);

    //2. 按照后端的要求拼接token数据
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      // console.log('这个是token:',config.headers.Authorization);
      // console.log(token);
    }

    return config;
  }, function (error) {
    // 对请求错误做些什么
    return Promise.reject(error);
  });

// 添加响应拦截器
httpInstance.interceptors.response.use(function (response) {
    // 2xx 范围内的状态码都会触发该函数。
    // 对响应数据做点什么
    return response;
  }, function (error) {
    // 超出 2xx 范围的状态码都会触发该函数。
    // 对响应错误做点什么
    //统一错误提示语
    ElMessage({
      type: 'warning',
      message: error
    })

    //401token失效处理
    //1. 清楚本地数据
    //2. 跳转到登录页

    return Promise.reject(error);
  });

export default httpInstance