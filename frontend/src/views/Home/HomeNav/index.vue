<script setup>
import { useUserStore } from '../../../stores/user';
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
const router = useRouter();
const userStore = useUserStore();
const token = userStore.userInfo.access_token;

const doLoginOut = async () => {
    await userStore.getLoginOut();
    router.replace({path: '/login'});
    ElMessage.success('退出登录成功');
}



</script>

<template>
    <div class="container">
        <div class="left">
            <img src="https://lf-code-agent.coze.cn/obj/x-ai-cn/256051588354/attachment/微信图片_20250929221417_862_2_20251001101007.png" alt="">
            <h1>职趣星航</h1>
        </div>
        <div class="middle">
            <ul>
                <li>
                    <RouterLink>
                        <i class="iconfont icon-shouye-shouye first"> 首页</i>

                    </RouterLink>
                </li>
                <li>
                    <RouterLink to="/career-explore">
                        <i class="iconfont icon-diqiu second"> 职业星球</i>
                    </RouterLink>
                </li>
                <li>
                    <RouterLink to="/document">
                        <i class="iconfont icon-pingjiaceping second"> 测评</i>
                    </RouterLink>
                </li>
                <li>
                    <RouterLink to="/community">
                        <i class="iconfont icon-sangeren second"> 社区</i>
                    </RouterLink>
                </li>
            </ul>
        </div>
        <div class="right" v-if="token">
            <i class="iconfont icon-tongzhi">
                <span class="number">
                    3
                </span>
            </i>
            <div class="user">
                <img src="https://space.coze.cn/api/coze_space/gen_image?image_size=square&prompt=User%20avatar%20professional&sign=715bc8643e19b13f1c1480c3feefde0f" alt="">
                <p>Moemu</p>
                <i class="iconfont icon-jiantou_liebiaozhankai"></i>
                <div class="second-menu">
                    <RouterLink to="/user">
                        <li>
                            <i class="iconfont icon-customer-fill"></i>
                            个人中心
                        </li>
                    </RouterLink>
                    <RouterLink>
                         <li>
                            <i class="iconfont icon-shezhi"></i>
                            设置
                        </li>
                    </RouterLink>
                    <div class="line">
                    </div>
                    <RouterLink >
                         <li class="third" @click="doLoginOut">
                            <i class="iconfont icon-shezhi"></i>
                            退出登录
                        </li>
                    </RouterLink>
                </div>
            </div>
        </div>
        <div class="right-second" v-else @click="$router.push('/login')">
            请先登录<i class="iconfont icon-customer-fill" ></i>
        </div>
    </div>
</template>

<style lang="scss">
    .container{
        position: fixed;
        top: 0;
        left: 0;
        z-index: 999;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 16px;
        width: 100%;
        height: 64px;
        background: #0f1a2bcc;
        backdrop-filter: blur(12px);
        border-bottom: 1px solid #1e293b;
        .left{
            display: flex;
            align-items: center;
            width: 12%;
            img{
                width: 40px;
                height: 40px;
            }
            h1{
                margin-left: 16px;
                font-size: 20px;
                font-weight: 700;
                color: transparent;
                background-image: linear-gradient(to right,#c084fc,#3b82f6);
                background-clip: text;
            }
        }

        .middle{
            width: 23%;
            // background-color: pink;
            ul{
                display: flex;
                justify-content: space-between;
                align-items: center;
                li{
                    .iconfont{
                        font-size: 17px;
                    }
                    .first:hover{
                        color: #c084fc;
                    }
                    .second{
                        color: #cbd5e1;
                        &:hover{
                            color: #fff;
                        }
                    }
                }
            }

        }

        .right{
            display: flex;
            align-items: center;
            width: 13.5%;
            // background-color: pink;
            .iconfont{
                color: #cbd5e1;
                position: relative;
                margin-left: 40px;
                font-size: 25px;
                &:hover{
                    color: #fff;
                    .number{
                        color: #fff;
                    }
                }
                .number{
                    position: absolute;
                    right: 0px;
                    top: -5px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    width: 16px;
                    height: 16px;
                    font-size: 12px;
                     color: #cbd5e1;
                    border-radius: 999px;
                    background-color: #ef4444;
                }
            }
            .user{
                position: relative;
                display: flex;
                align-items: center;
                margin-left: 12px;
                img{
                    width: 40px;
                    height: 40px;
                    border-radius: 999px;
                    border: 2px solid #a855f74d;
                }
                p{
                    margin-left: 8px;
                    font-size: 14px;
                }
                .iconfont{
                    margin-left: 2px;
                    margin-top: 3px;
                    &:hover{
                        color: #cbd5e1;
                    }
                }
                &:hover{
                    cursor: pointer;
                    .iconfont{
                        color: #fff;
                    }
                    .second-menu{
                        visibility: visible;
                    }
                }
                .second-menu{
                    transition: all .3s;
                    visibility: hidden;
                    position: absolute;
                    right: 4px;
                    bottom: -140px;
                    padding: 6px 0;
                    width: 192px;
                    height: 132px;
                    background-color: #1e293b;
                    border-radius: 8px;
                    box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
                    li{
                        display: flex;
                        align-items: center;
                        padding: 7px 0 7px 12px;
                        color: #cbd5e1;
                        .iconfont{
                            font-size: 17px;
                            margin-right: 6px;
                            &:hover{
                                color: #cbd5e1;
                            }
                        }
                        &:hover{
                            background-color: #334155;
                            color:#fff;
                            .iconfont{
                                color: #fff;
                            }
                        }
                    }
                    .line{
                        margin: 5px 0;
                        border-top: 1px solid #334155;
                    }
                    .third{
                        color: #f87171;
                        .iconfont{
                            color: #f87171;
                        }
                        &:hover{
                            color: #f87171;
                            .iconfont{
                                color: #f87171;
                            }
                        }
                    }
                }
            }
        }
        .right-second{
            font-size: 17px;
            color: #cbd5e1;
            .iconfont{
                margin-left: 8px;
                font-size: 18px;
                color: #cbd5e1;
            }
            &:hover{
                color: #fff;
                cursor: pointer;
                .iconfont{
                    color: #fff;
                }
            }
        }
    }
</style>