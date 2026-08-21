<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useQuizStore } from '../../stores/quiz';
const router = useRouter()
const quizStore = useQuizStore()

const slug = ref('');

const startQuiz1 = async () => {
    slug.value = 'classic_scenario_mode';
    await quizStore.startQuiz({slug: slug.value});
    console.log(slug.value);
    router.push({path : '/question'})
}

const startQuiz2 = async () => {
    slug.value ='intelligent_fusion_mode';
    await quizStore.startQuiz({slug: slug.value});
    console.log(slug.value);
    router.push({path : '/question'})
}




</script>

<template>
    <div class="evaluation-container">
        <div class="second-container">
            <img src="../../assets/iconfont/backgroud1.png" alt=""></img>
            <div class="first-container"></div>
        </div>
        <div class="third-container">
            <div class="top">
                <h1>发现你的职业天赋星!</h1>
                <p>穿越星际迷雾，找到最适合你的职业轨道！选择你的探索方式：</p>
            </div>
            <div class="middle">
                <div class="box first">
                    <div class="tubiao">
                        🚀
                    </div>
                    <h2>完整星际探索 (11题)</h2>
                    <p>适合想要深度了解自己的太空旅人</p>
                    <ul>
                        <li><span>•</span>6个创意非工作场景模拟</li>
                        <li><span>•</span>5个趣味互动游戏挑战</li>
                        <li><span>•</span>全面分析报告 + 个性化职业星球推荐</li>
                    </ul>
                    <div class="button" @click="startQuiz2">
                        开始探度探索<i class="iconfont icon-youjiantou"></i>
                    </div>
                </div>
                <div class="box second">
                    <div class="tubiao">
                        ⚡
                    </div>
                    <h2>快速轨道扫描 (8题)</h2>
                    <p>适合时间有限的星际速航者</p>
                    <ul>
                        <li><span>•</span>8个精选创意情景体验</li>
                        <li><span>•</span>快速定位职业倾向</li>
                        <li><span>•</span>核心能力分析报告+个性化职业星球推荐</li>
                    </ul>
                    <div class="button" @click="startQuiz1">
                        开始快速扫描<i class="iconfont icon-youjiantou"></i>
                    </div>
                </div>
           </div>
           <div class="bottom">
                <li><div class="first">✨</div><h3>真实场景模拟</h3><p>在创意情景中发现真实偏好</p></li>
                <li><div class="first">🎮</div><h3>互动游戏体验</h3><p>享受太空冒险般的答题乐趣</p></li>
                <li><div class="first">📊</div><h3>科学分析解读</h3><p>基于霍兰德理论的职业星图</p></li>
                <li><div class="first">🪐</div><h3>个性化推荐</h3><p>匹配最适合你的职业星球</p></li>
           </div>
           <div class="footer">
               <p>*两种模式均免费，3-8分钟完成</p>
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
        .third-container{
            width: 100%;
            height: 100px;
            position: absolute;
            top: 0;
            left: 0;
            z-index: 100;
            .top{
                margin-top: 48px;
                h1{
                    animation: 2s pulse infinite linear;
                    text-align: center;
                    font-size: 60px;
                    background-image: linear-gradient(to right, #60a5fa , #6366f1 , #9333ea);
                    background-clip: text;
                    color: transparent;
                }
                @keyframes pulse {
                    50%{
                        transform: scale(1.35);
                    }
                }
                p{
                    font-size: 24px;
                    text-align: center;
                }
            }
            .middle{
                display: flex;
                justify-content: center;
                gap: 32px;
                margin: 93px 0;
                height: 406px;
                width: 100%;
                // background-color: pink;
                .box{
                    transition: all 2s;
                    padding: 32px;
                    width: 384px;
                    height: 100%;
                    background-color: #fff;
                    border: 1px solid #3b82f64d;
                    border-radius: 16px;
                    background-image: linear-gradient(to bottom right,rgb(30 58 138 / 0.3) , rgb(49 46 129 / 0.3));
                    background-color: #1e3a8a4d;
                    &:hover{
                        box-shadow: 0px 10px 25px -5px #3b82f61b;
                        transform: translateY(-20px);
                    }
                    .tubiao{
                        font-size: 48px;
                    }
                    h2{
                        margin-top: 13px;
                        font-size: 24px;
                        font-weight: 700;
                    }
                    p{
                        margin-top: 11px;
                        color: #d1d5db;
                        font-size: 16px;
                    }
                    ul{
                        display: flex;
                        flex-direction: column;
                        justify-content: space-between;
                        margin-top: 25px;
                        height: 96px;
                        font-size: 16px;
                        li{
                            color: #d1d5db;;
                            span{
                                margin-right: 5px;
                                color: #60a5fa;
                            }
                        }
                    }
                    .button{
                        margin-top: 25px;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        padding: 12px 24px;
                        font-size: 16px;
                        background-image:linear-gradient(to right,#3b82f6 , #4f46e5);
                        border-radius: 12px;
                        &:hover{
                            background-image: linear-gradient(to right,#2563eb , #4338ca);
                            cursor: pointer;
                        }
                    }
                }
                .second{
                    background-image: linear-gradient(to bottom right,rgb(88 28 135 / 0.3) , rgb(131 24 67 / 0.3));
                    border: 1px solid #a855f74d;
                    .button{
                        background-image: linear-gradient(to right,#a855f7 , #db2777);
                        &:hover{
                            background-image: linear-gradient(to right,#9333ea , #be185d);
                        }
                    }
                }
            }
            .bottom{
                display: flex;
                justify-content: space-between;
                padding: 48px 16px 0;
                margin-top: 50px;
                height: 180px;
                // background-color: pink;
                li{
                    text-align: center;
                    width: 23.4%;
                    // background-color: #fff;
                    .first{
                        font-size: 30px;
                        color: transparent;
                        line-height: 36px;
                        background-image: linear-gradient(to bottom,#60a5fa , #a855f7);
                        background-clip: text;
                    }
                     h3{
                        margin-top: 9px;
                    }
                    p{
                        margin-top: 5px;
                        font-size: 14px;
                        color: #d1d5db;
                    }
                }
            }
            .footer{
                display: flex;
                justify-content: center;
                align-items: center;
                height: 110px;
                text-align: center;
                // background-color: pink;
                font-size: 14px;
                color: #9ca3af;
            }
        }
    }

</style>