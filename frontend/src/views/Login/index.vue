<script setup>
import { ref } from "vue";
import { ElMessage } from "element-plus";
import { useRouter } from "vue-router";
import 'element-plus/theme-chalk/el-message.css'
//引入pinia管理获取数据
import { useUserStore } from '../../stores/user'

//创建实例
const userStore = useUserStore();


const router = useRouter();

//1. 准备表单对象
const form = ref({
    username: 'Moemu',
    password: 'mPul3KmQQbU3ay2',
})

//2 准备规则对象
const rules = ref({
    username: [
        {required: true, message: '账号/邮箱不能为空', trigger:'blur'}
    ],
    password: [
        {required: true, message: '密码不能位空', trigger:'blur'},
        {min: 6, max: 20, message: '密码长度为6~20位', trigger:'blur'}
    ]
})

//3 获取form实例做表单验证
const formRef = ref(null)
const doLogin = () => {
    const {username, password } = form.value;
    // 验证逻辑
   formRef.value.validate(async (valid) =>{
        //如果校验通过
        if(valid){
            await userStore.getLogin({username,password})
            //1. 提示用户
            ElMessage({ type: 'success', message: '登录成功'})
            //2. 跳转首页
            router.replace({path: '/'})
        }
    })
}

const elmessage = () => {
    ElMessage({ type: 'info', message: '此功能还在开发中'})
}

</script>

<template>
    <div class="login-container">
        <div class="login">
            <!-- 左侧图片区域 -->
            <div class="left">
                    <!-- 左侧背景定位 -->
                    <div class="bgc">
                    </div>
                    <!-- 左侧动画 -->
                     <div class="animation">

                     </div>
                    <img class="logo" src="https://lf-code-agent.coze.cn/obj/x-ai-cn/256051588354/attachment/微信图片_20250929221417_862_2_20251001101007.png" alt="">
                    <div class="title">
                        职趣星航
                    </div>
                    <p>
                        发现你的职业星轨，开启未来之旅
                    </p>
                    <div class="photo-box">
                        <img class="photo" src="https://space.coze.cn/api/coze_space/gen_image?image_size=landscape_16_9&prompt=Abstract%20space%20galaxy%20with%20stars%20and%20planets%20with%20futuristic%20technology%20elements&sign=7effb704aaba028161cbf24a39c226b6" alt="">
                        <div class="img-bgc">
                    </div>
                    </div>
                    <!-- 右下角背景定位 -->
                    <div class="bgc2">
                    </div>
            </div>
            <!-- 右侧登录区域 -->
            <div class="right">
                <div class="box">
                    <h2>欢迎回来</h2>
                    <p>登录你的账号，继续探索职业星球</p>
                    <div class="form-box">
                        <!-- 登录表单 -->
                         <el-form ref="formRef" :model="form" :rules="rules">
                            <label for="email">
                                账号/邮箱
                            </label>
                            <el-form-item prop="username">
                                <el-input v-model="form.username" class="input" prefix-icon="UserFilled" icon-size="2px" placeholder="请输入账号/邮箱"></el-input>
                            </el-form-item>
                            <div class="second">
                                <label for="password">密码</label>
                            <label class="second-label" for="password" @click="elmessage">忘记密码？</label>
                            </div>
                            <el-form-item prop="password">
                                <el-input v-model="form.password"  class="input" type="password" show-password="true" prefix-icon="Lock" icon-size="2px" placeholder="请输入密码">
                                </el-input>
                            </el-form-item>
                            <div class="button" @click="doLogin">
                                登录
                            </div>
                         </el-form>
                         <div class="line-text">
                            或使用以下方式登录
                         </div>
                         <div class="iconfont">
                            <div class="wx" @click="elmessage">
                                <img src="../../assets/iconfont/weixin.svg" alt="">
                            </div>
                            <div class="qq" @click="elmessage">
                                <img src="../../assets/iconfont/QQ.svg" alt="">
                            </div>
                         </div>
                         <div class="register">
                            还没有账号？
                            <router-link to="/register-option">
                                <label class="register-label" for="password">
                                    立即注册
                                </label>
                            </router-link>
                         </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

</template>

<style lang="scss" scoped>

    .login-container{
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        height: 100vh;
        background: #111b2c;


        .login{
            // overflow: hidden;
            position: relative;
            display: flex;
            width: 83%;
            height: 85%;
            // background-color: pink;
            border-radius: 15px;

            .left{
                overflow: hidden;
                position: relative;
                width: 50%;
                height: 100%;
                padding-top: 65px;
                background-color: #fff;
                border-radius: 15px 0 0 15px;
                text-align: center;
                background-image: linear-gradient(to bottom right,#0f1a2b , #1a2035);
                box-shadow: -10px 20px 20px rgba(0,0,0,1);

                .bgc{
                    position: absolute;
                    z-index: 999;
                    left: -80px;
                    top: -60px;
                    width: 60%;
                    height: 60%;
                    background-color: rgb(94 23 235 / 0.2);
                    // background-color: #fff;
                    filter: blur(64px);
                    border-radius: 500px;
                }

                .bgc2{
                    position: absolute;
                    z-index: 999;
                    right: -80px;
                    bottom: -60px;
                    width: 60%;
                    height: 60%;
                    border-radius: 500px;
                    background-color: rgb(0 245 255 / 0.1);
                    filter: blur(64px);
                }

                .animation{
                    position: absolute;
                    width: 22%;
                    height: 22%;
                    top: 152px;
                    left: 140px;
                    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
                    background-color: rgb(94 23 235 / 0.3);
                    border-radius: 90px;
                    filter: blur(24px);
                }

                @keyframes pulse{
                    0%, 100%{
                        opacity: 1;
                    }
                    50%{
                        opacity: 0.5;
                    }
                }

                .logo{
                    width: 108px;
                    height: 96px;
                }

                .title{
                    margin-top: 5px;
                    font-size: 36px;
                    font-weight: 700;
                    background-image: linear-gradient(to right,#5e17eb,#00f5ff);
                    background-clip: text;
                    color: transparent;
                }

                p {
                    margin-top: 5px;
                    font-size: 18px;
                    color: rgb(203 213 225);
                }

                .photo-box{
                    position: relative;
                    width: 100%;
                    height: 280px;
                    .photo{
                        margin-top: 30px;
                        width: 71%;
                        height: 89%;
                        opacity: 0.5;
                        border-radius: 15px;
                    }

                    .img-bgc{
                        position: absolute;
                        bottom: 0px;
                        left: 14.5%;
                        width: 71%;
                        height: 20%;
                        background: linear-gradient(to bottom,transparent, rgba(0,0,0,0.8));
                        border-radius: 0 0 15px 15px;
                    }
                }
            }

            .right{
                display: flex;
                justify-content: center;
                align-items: center;
                width: 50%;
                height: 100%;
                background-color: #10182b;
                border-radius: 0 15px 15px 0;
                box-shadow: 10px 20px 20px rgba(0,0,0,1);

                .box{
                    width: 85%;
                    height: 85%;
                    // background-color: pink;

                    h2{
                        font-size: 30px;
                        font-weight: 700;
                        color: #fff;
                    }

                    p{
                        margin-top: 5px;
                        color: rgb(148 163 184);
                        font-size: 16px;
                    }

                    .form-box{
                        margin-top: 32px;
                        width: 100%;
                        height: 300px;
                        // background-color: pink;

                        label{
                            color: rgb(203 213 225);
                            font-size: 14px;
                            font-weight: 700;
                        }

                        .el-input{
                            margin-top: 5px;
                            height: 49px;
                            font-size: 20px;
                            color: #282828;
                            background-color: #fff;
                            border-radius: 10px;

                        }

                        :deep(.el-input__wrapper){
                            background-color: #1e293b;
                            color: #fff;
                            border:1px solid #334155;
                            border-radius: 8px;
                        }

                        :deep(.el-input__inner){
                            color: #fff;
                            font-size: 16px;
                        }

                        :deep(.el-input__wrapper.is-focus){
                            border:3px solid #5e17eb;
                            box-shadow: none;
                        }

                        :deep(.el-input__inner:focus){
                            outline: none;
                            border-color: transparent;
                        }

                        .second{
                            display: flex;
                            justify-content: space-between;
                            width: 100%;
                            margin-top: 24px;

                            .second-label{
                                color: rgb(0, 245, 255);
                                &:hover{
                                    color: rgb(94 23 235);
                                    cursor: pointer;
                                }
                            }
                        }

                        .button{
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            margin-top: 25px;
                            width: 100%;
                            height: 48px;
                            color: #fff;
                            font-size: 16px;
                            font-weight: 650;
                            background: linear-gradient(to right,#5e17eb , #00f5ff);
                            border-radius: 8px;
                            &:hover{
                                cursor: pointer;
                                background: linear-gradient(to right,#7c3aed , #22d3ee);
                            }
                        }

                    }

                    .line-text{
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        width: 100%;
                        height: 30px;
                        margin-top: 20px;
                        color: #94a3b8;
                        font-size: 14px;

                        &::before{
                            margin-right: 18px;
                        }

                        &::after{
                            margin-left: 18px;
                        }

                        &::before,&::after{
                            content: "";
                            flex: 1;
                            height: 1px;
                            background-color: #334155;
                        }
                    }

                    .iconfont{
                        margin-top: 22px;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        width: 100%;
                        height: 50px;
                        // background-color: pink;
                        .wx{
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            margin-right: 12px;
                            width: 48px;
                            height: 48px;
                            background-color: #1e293b;
                            border-radius: 24px;
                            &:hover{
                                background-color: #334155;
                                cursor: pointer;
                            }
                        }

                        .qq{
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            margin-left: 12px;
                            width: 48px;
                            height: 48px;
                            background-color: #1e293b;
                            border-radius: 24px;
                            &:hover{
                                background-color: #334155;
                                cursor: pointer;
                            }
                        }

                        img{
                            width: 33px;
                            height: 26px;
                        }
                    }

                    .register{
                        margin-top: 20px;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        width: 100%;
                        height: 30px;
                        font-size: 14px;
                        font-weight: 700;
                        color: #94a3b8;
                        .register-label{
                            color: rgb(0, 245, 255);
                            &:hover{
                                    color: rgb(94 23 235);
                                    cursor: pointer;
                                }
                        }
                    }
                }
            }

        }
    }
















</style>