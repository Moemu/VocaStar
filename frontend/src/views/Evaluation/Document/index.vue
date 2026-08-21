<script setup>
import { ref, Transition, watch} from 'vue'
import { useQuizStore } from '../../../stores/quiz'
import questionOne from './component/questionOne.vue'
import questionTwo from './component/questionTwo.vue'
import questionThree from './component/questionThree.vue'
import questionFour from './component/questionFour.vue'

const quizStore = useQuizStore();
console.log(quizStore.questionN);
quizStore.questionN = 'first';

// 配置组件列表
const componentMap = {
    first: questionOne,
    second: questionTwo,
    third: questionThree,
    fourth: questionFour,
}

const currentColor =['','#3b82f680','#8b5cf699','#ec4899b3','#f97316cc'];

// watch(() => quizStore.questionNumber,(newNumber) => {
//     currentComponent.value = newNumber;
//     console.log(currentComponent.value);
// })


</script>

<template>
    <div class="evaluation-container">
        <div class="second-container">
            <!-- <img src="../../../assets/iconfont/backgroud1.png" alt=""></img> -->
            <div class="first-container"></div>
        </div>
        <div class="document-container">
            <div class="top">
                <h1>🪐 完善你的星际档案</h1>
                <p>为了生成专属你的个性化职业星图，请补充以下信息：</p>
            </div>
            <div class="box-time">
                <div class="time" :style="{ backgroundColor: currentColor[quizStore.qN] }">
                    <div class="number">
                        {{quizStore.qN}}/4
                    </div>
                </div>
                <div class="loading">
                    <div class="loader">
                        <div class="bg" :style="{ width:`${quizStore.qN * 100 / 4}%`}"></div>
                    </div>
                    {{ quizStore.qN * 100 / 4 }}%
                </div>
            </div>
            <div class="middle">
                <Transition name="slide-left-right">
                    <Component :is="componentMap[quizStore.questionN]" :key="quizStore.questionN"></Component>
                </Transition>
           </div>
           <div class="bottom">
                <p>这些信息将帮助我们：</p>
                <ul>
                    <li>
                        <i class="iconfont icon-shoucang" :style="{ color: '#facc15' }"></i>
                        <p>结合测评结果，生成更精准的职业推荐</p>
                    </li>
                    <li>
                        <i class="iconfont icon-wenhao" :style="{ color: '#60a5fa' }"></i>
                        <p>理解你的独特困惑，提供针对性建议</p>
                    </li>
                    <li>
                        <i class="iconfont icon-chart" :style="{ color: '#c084fc' }"></i>
                        <p>提供符合你阶段和专业的实用路径</p>
                    </li>
               </ul>
           </div>
           <div class="footer-box">
               <p>数据安全加密 • 所有信息仅用于生成职业推荐</p>
           </div>
        </div>
    </div>
</template>

<style lang="scss">
    .evaluation-container{
        position: relative;
        .second-container{
            z-index: 10;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100vh;
            background-image: linear-gradient(to bottom, #020617, #1e1b4b, #3b0764);
            .first-container{
                position: absolute;
                opacity: 0.4;
                top: 0;
                left: 0;
                z-index: 9;
                width: 100%;
                height: 100%;
                background-image: linear-gradient(to bottom, #020617, #1e1b4b, #3b0764);
            }
            img{
                animation: 1s identifier infinite alternate;
                width: 100%;
                height: 100%;
                object-fit: cover;
            }
            @keyframes identifier {
                50% {
                    opacity: 0.8;
                }
            }
        }
        .document-container{
            width: 100%;
            height: 100px;
            position: absolute;
            top: 0;
            left: 0;
            z-index: 100;
            .top{
                margin-top: 30px;
                h1{
                    text-align: center;
                    font-size: 36px;
                    line-height: 40px;
                    background-image: linear-gradient(to right, #60a5fa , #6366f1 , #9333ea);
                    background-clip: text;
                    color: transparent;
                }
                p{
                    margin-top: 8px;
                    color: #d1d5db;
                    font-size: 18px;
                    line-height: 28px;
                    text-align: center;
                }
            }
            .box-time{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin: 32px auto 0;
                width: 44.5%;
                height: 40px;
                // background-color: pink;
                .time{
                    position: relative;
                    width: 40px;
                    height: 40px;
                    border-radius: 999px;
                    background-color: #6674cc4d;
                    border: 2px solid #ffffff33;
                    .number{
                        position: absolute;
                        top: -5px;
                        right: -5px;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        width: 20px;
                        height: 20px;
                        font-size: 12px;
                        line-height: 16px;
                        background-color: #3b82f6;
                        border-radius: 999px;
                        border: 2px solid #0f172a;
                    }
                }
                .loading{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    width: 448px;
                    height: 20px;
                    font-size: 14px;
                    line-height: 20px;
                    color: #d1d5db;
                    // background-color: #fff;
                    .loader{
                        width: 380px;
                        height: 8px;
                        background-color: #374151;
                        border-radius: 999px;
                        .bg{
                            height: 100%;
                            background-image: linear-gradient(to right,#a855f7 , #3b82f6);
                            border-radius: 999px;
                        }
                    }
                }
            }

            .middle{
                overflow: hidden;
                position: relative;
                padding: 32px;
                margin: 35px auto 0;
                width: 44.5%;
                height: 514px;
                background-color: #ffffff0d;
                border: 1px solid #ffffff1a;
                border-radius: 16px;
                /* 5. 核心：左右过渡动画（与Transition的name对应） */
                /* 进入动画：从左侧（-100%）滑到原位（0） */
                .slide-left-right-enter-from {
                transform: translateX(-100%);
                opacity: 0;
                }

                .slide-left-right-enter-active {
                    position: absolute;
                    width: 90%;
                    height: 100%;
                    top: 32px;
                    left: 31px;
                    transition: transform 0.8s ease, opacity 0.2s ease-out;
                }

                .slide-left-right-enter-to {
                transform: translateX(0);
                opacity: 1;
                }

                /* 离开动画：从原位（0）滑到右侧（100%） */
                .slide-left-right-leave-from {
                transform: translateX(0);
                opacity: 1;
                }

                .slide-left-right-leave-active {
                transition: transform 0.8s ease, opacity 0.2s ease-out;
                /* 关键：让离开动画与进入动画同时执行，避免卡顿 */
                    position: absolute;
                    width: 90%;
                    height: 100%;
                    top: 32px;
                    left: 31px;
                // width: calc(600px - 60px); /* 与题目容器宽度一致（外框宽-内边距） */
                }

                .slide-left-right-leave-to {
                transform: translateX(100%);
                opacity: 0;
                }
            }
            .bottom{
                padding: 24px;
                width: 44.5%;
                height: 190px;
                margin: 35px auto 0;
                background-color: #ffffff0d;
                border: 1px solid #ffffff1a;
                border-radius: 16px;
                p{
                    text-align: center;
                    font-size: 16px;
                    color: #d1d5db;
                }
                ul{
                    margin: 30px 0 0;
                    display: flex;
                    justify-content: space-between;
                    align-items: cneter;
                    width: 100%;
                    height: 100px;
                    // background-color: pink;
                    li{
                        padding-top: 5px;
                        width: 31%;
                        height: 100%;
                        // background-color: pink;
                        text-align: center;
                        .iconfont{
                            font-size: 22px;
                        }
                        p{
                            margin-top: 5px;
                            font-size: 14px;
                            line-height: 20px;
                        }
                    }
                }
            }
            .footer-box{
                display: flex;
                justify-content: center;
                align-items: center;
                height: 110px;
                text-align: center;
                // background-color: pink;
                font-size: 14px;
                color: #6b7280;
            }
        }
    }

</style>