<script setup>
import { ref } from "vue";
import { ElMessage } from "element-plus";
const password = ref("");
const elmessage = () => {
    ElMessage({ type: 'info', message: '此功能还在开发中'})
}
</script>

<template>
    <div class="register-container">
        <div class="login">
            <!-- 左侧图片区域 -->
            <div class="left">
                    <!-- 左侧背景定位 -->
                    <div class="bgc">
                    </div>
                    <!-- 左侧动画 -->
                     <div class="animation">

                     </div>
                    <img class="logo" src="../../assets/iconfont/地球.svg" alt="">
                    <div class="title">
                        职业探索平台
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
                    <h2>加入我们，开启探索</h2>
                    <p>选择你的角色，开始职业探索之旅</p>
                    <div class="form-box">
                        <div class="option">
                            <div class="title">
                                <div class="iconfont">
                                    👨‍🚀
                                </div>
                                <p>
                                    注册成为探索者
                                </p>
                            </div>
                            <div class="text">
                                体验职业星球，完成趣味测评，规划成长路径。
                            </div>
                            <RouterLink to="/register-explorer">
                                <div class="button">
                                    成为探索者
                                </div>
                            </RouterLink>
                        </div>
                        <div class="option">
                            <div class="title">
                                <div class="iconfont">
                                    🧑‍🏫
                                </div>
                                <p>
                                    注册成为导师
                                </p>
                            </div>
                            <div class="text">
                                分享行业经验，指导新人成长，扩大个人影响力。
                            </div>
                            <RouterLink to="">
                                <div class="button" @click="elmessage">
                                    成为导师
                                </div>
                            </RouterLink>
                        </div>
                        <div class="register">
                            已有账号？
                            <router-link to="/login">
                                <label class="register-label" for="password">
                                    直接登录
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
    .register-container{
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
            width: 68%;
            height: 98%;
            // background-color: pink;
            border-radius: 15px;

            .left{
                overflow: hidden;
                position: relative;
                width: 50%;
                height: 100%;
                padding-top: 115px;
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
                    width: 85px;
                    height: 85px;
                }

                .title{
                    margin-top: -5px;
                    font-size: 36px;
                    font-weight: 700;
                    background-image: linear-gradient(to right,#5e17eb,#00f5ff);
                    background-clip: text;
                    color: transparent;
                }

                p {
                    margin-top: 2px;
                    font-size: 18px;
                    color: rgb(203 213 225);
                }

                .photo-box{
                    position: relative;
                    width: 100%;
                    height: 280px;
                    .photo{
                        margin-top: 30px;
                        width: 88%;
                        height: 89%;
                        opacity: 0.5;
                        border-radius: 15px;
                    }

                    .img-bgc{
                        position: absolute;
                        bottom: 0px;
                        left: 6%;
                        width: 88%;
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
                    width: 80%;
                    height: 86%;
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
                        margin-top: 0px;
                        width: 100%;
                        height: 300px;
                        // background-color: pink;

                        .option{
                            width: 100%;
                            height: 203px;
                            margin-top: 28px;
                            padding: 24px;
                            background-color: #1e293b4d;
                            border-radius: 12px;
                            border: 2px solid #334155;
                            transition: all 0.4s ;
                            &:hover{
                                background-color: #1e293b80;
                                border-color: #475569;
                                transform: scale(1.02);
                            }
                            &:active{
                                transform: scale(0.98);
                            }
                            .title{
                                display: flex;
                                align-items: center;
                                .iconfont{
                                    display: flex;
                                    justify-content: center;
                                    align-items: center;
                                    width: 46px;
                                    height: 46px;
                                    font-size: 24px;
                                    border-radius: 23px;
                                    background-color: #5e17eb33;
                                }
                                p{
                                    margin-left: 15px;
                                    font-size: 20px;
                                    font-weight: 600;
                                    color: #fff;
                                }
                            }
                            .text{
                                margin-top: 13px;
                                color: #cbd5e1;
                                font-size: 16px;
                            }
                        }

                        label{
                            color: rgb(203 213 225);
                            font-size: 14px;
                            font-weight: 700;
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
                            height: 48px;
                            color: #fff;
                            font-size: 16px;
                            font-weight: 650;
                            background: linear-gradient(to right,#5e17eb , #00f5ff);
                            border-radius: 8px;
                            &:hover{
                                background: linear-gradient(to right,#7c3aed , #22d3ee);
                            }
                        }

                    }

                    .register{
                        margin-top: 30px;
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