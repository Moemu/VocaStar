<script setup>
import { ref } from "vue";
import careerProfile from "./component/careerProfile.vue";
import requiry from "./component/requiry.vue";
import salery from "./component/salery.vue";
import technique from "./component/technique.vue";

const components = [careerProfile, requiry, salery, technique];


const tableData = ['职业概述','能力要求','薪资与分布','技能图谱'];
const id = ref(0);
const changeTable = (index) => {
    id.value = index;
}

</script>

<template>
    <div class="career-container">
        <div class="box">
            <div class="left" @click="$router.push('/career-explore')">
                <i class="iconfont icon-xiangzuojiantou"></i>返回星系
            </div>
            <h1>软件工程师</h1>
        </div>
        <div class="top">
            <div class="insight">
                <div class="background"></div>
                <img src="../../assets/career/8922e580eddb357a32b8099838bea33e.png" alt="">
                <div class="text">
                    <div class="left"><h1>软件工程师</h1><p>技术星云 · 探索职业可能性</p></div>
                    <div class="right"><div class="button collect"><i class="iconfont icon-shoucang1"></i>收藏</div><div class="button share"><i class="iconfont icon-JC_054"></i>分享</div></div>
                </div>
            </div>
            <div class="middle">
                <div class="left" @click="$router.push('/cosplay')"><div class="tubiao"><i class="iconfont icon-fanchuan"></i></div> 开始职业体验</div>
                <div class="right"><div class="button"><div class="tubiao"><i class="iconfont icon-sangeren second"></i></div>加入学习小组</div><div class="button"><div class="tubiao"><i class="iconfont icon-xiangmujingli"></i></div>寻找职业导师</div></div>
            </div>
            <div class="table">
                <li v-for="(i,index) in tableData" :key="index" :class="{active: id == index}" @click="changeTable(index)">{{ i }}</li>
            </div>
            <Transition name="slide-up" mode="out-in">
                <component :is="components[id]"></component>
            </Transition>
            <div class="footer">
               <h2>准备好开始你的软件工程师之旅了吗?</h2>
               <p>通过我们的职业体验，模拟真实工作场景，了解软件工程师的日常工作，提升核心能力。</p>
               <div class="anniu"><div class="button">开始职业体验<i class="iconfont icon-youjiantou"></i></div></div>
            </div>
        </div>
    </div>
</template>

<style lang="scss">
    .career-container {
        // height: 200px;
        width: 100%;
        background-image: linear-gradient(to bottom, #0f172a , #020617);
        .box{
            position: fixed;
            top: 0;
            left: 0;
            z-index: 999;
            display: flex;
            align-items: center;
            // justify-content: space-between;
            padding: 12px 16px;
            width: 100%;
            height: 52px;
            background: #0f1a2bcc;
            backdrop-filter: blur(12px);
            border-bottom: 1px solid #1e293b;
            .left{
                display: flex;
                align-items: center;
                width: 12%;
                font-size: 16px;
                color: #cbd5e1;
                .iconfont{
                    margin-right: 10px;
                    font-size: 20px;
                    font-weight: 700;
                    color: #cbd5e1;
                }
                &:hover{
                    cursor: pointer;
                    color: #fff;
                    .iconfont{
                        color: #fff;
                    }
                }
            }
             h1{
                    position: absolute;
                    left: 50%;
                    top: 50%;
                    transform: translate(-25%, -50%);
                    font-size: 20px;
                    font-weight: 700;
                    color: transparent;
                    background-image: linear-gradient(to right,#c084fc,#3b82f6);
                    background-clip: text;
            }
        }
        .top{
            position: relative;
            padding: 78px 16px 0;
            width: 100%;
            // height: 420px;
            .insight{
                position: relative;
                height: 256px;
                border-radius: 16px;
                .background{
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background-image: linear-gradient(to top,#0f172a , rgb(15 23 42 / 0.7) , transparent);
                }
                img{
                        width: 100%;
                        height: 100%;
                        border-radius: 16px;
                        object-fit: cover;
                }
                .text{
                    position: absolute;
                    bottom: 25px;
                    left: 25px;
                    height: 68px;
                    display: flex;
                    justify-content: space-between;
                    width: 96.5%;
                    // background-color: pink;
                    h1{
                        font-size: 30px;
                        line-height: 36px;
                    }
                    p{
                        margin-top: 8px;
                        color: #cbd5e1;
                        font-size: 16px;
                        line-height: 28px;
                    }
                    .right{
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        .button{
                            transition: all 0.3s ease;
                            margin-left: 15px;
                            padding: 8px 16px;
                            font-size: 14px;
                            font-weight: 700;
                            // background-color: #7e22ce;
                            background-color: #9333ea;
                            border-radius: 999px;
                            i{
                                margin-right: 4px;
                            }
                             &:hover{
                                transform: scale(1.05);
                                cursor: pointer;
                                background-color: #7e22ce;
                            }
                        }
                        .share{
                            background-color: #334155;
                            &:hover{
                                background-color: #475569;
                            }
                        }
                        // .collect{

                        // }
                    }
                }
            }
            .middle{
                display: flex;
                justify-content: space-between;
                margin-top: 30px;
                height: 96px;
                // background-color: pink;
                .left{
                    transition: all 0.5 linear;
                    text-align: center;
                    padding: 16px 24px;
                    width: 10%;
                    font-size: 16px;
                    font-weight: 500;
                    background-image: linear-gradient(to right,#9333ea , #2563eb);
                    border-radius: 12px;
                    .tubiao{
                        .iconfont{
                            font-size: 28px;
                            font-weight: 500;
                        }
                        margin-bottom: 10px;
                    }
                    &:hover{
                        cursor: pointer;
                        transform: scale(1.02);
                        background-image: linear-gradient(to right,#7e22ce , #1d4ed8);
                    }
                }
                .right{
                    display: flex;
                    justify-content: space-between;
                    width: 66.5%;
                    height: 100%;
                    // background-color: pink;
                    .button{
                        transition: all 0.3s ease;
                        padding: 16px 24px;
                        text-align: center;
                        width: 48%;
                        font-size: 16px;
                        font-weight: 500;
                        background-color: #1e293b;
                        border-radius: 12px;
                        .tubiao{
                            margin-bottom: 8px;
                            .iconfont{
                                font-size: 28px;
                            }
                        }
                        &:hover{
                            transform: scale(1.02);
                            cursor: pointer;
                            background-color: #334155;
                        }
                    }
                }
            }
            .table{
                margin-top: 50px;
                display: flex;
                width: 100%;
                height: 42px;
                border-bottom: 1px solid #1e293b;
                // background-color: pink;
                li{
                    transition: 0.1s ease;
                    margin-right: 35px;
                    height: 35px;
                    font-size: 14px;
                    font-weight: 500;
                    line-height: 20px;
                    color: #9dabbf;
                     cursor: pointer;
                    // border: 1px solid #581c874d;
                    &:hover{
                        color: #cbd5e1;
                    }
                    &.active{
                        border-bottom: 2px solid #a855f7;
                        color: #fff;
                    }
                }
            }
            .slide-up-enter-from{
                transform: translateY(20%);
                opacity: 0;
            }
            .slide-up-enter-active{
                transition: all 0.5s ease;
            }
            .slide-up-enter-to{
                transform: translateY(0);
                opacity: 1;
            }
            .footer{
                text-align: center;
                margin: 20px 0;
                width: 100%;
                height: 236px;
                padding: 32px;
                background-image: linear-gradient(to right, #1e293b , rgb(88 28 135 / 0.5) );
                border: 1px solid #581c874d;
                border-radius: 16px;
                h2{
                    margin-bottom: 14px;
                    font-size: 24px;
                }
                p{
                    color: #cbd5e1;
                    font-size: 16px;
                }
                .anniu{
                    margin-top: 40px;
                    display: flex;
                    justify-content: center;
                    gap: 14px;
                    .button{
                        transition: all 0.3s ease;
                        padding: 12px 24px;
                        color: #0f172a;
                        font-weight: 500;
                        font-size: 16px;
                        background-color: #ffffff;
                        border-radius: 12px;
                        .iconfont{
                            margin-left: 5px;
                            color: #0f172a;
                            font-size: 18px;
                            font-weight: 700;
                        }
                        &:hover{
                            cursor: pointer;
                            transform: scale(1.05);
                        }
                    }
                }
            }
        }
    }
</style>