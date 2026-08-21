<script setup>
import { ref, computed, watch } from 'vue'
import { useQuizStore } from '../../../stores/quiz';
const quizStore = useQuizStore();
const selectedIndex = ref([0,0,0,0,0,0]);
const maxHours = ref(10);
const answer = ref({
    type: 'time_allocation',
    question_id: quizStore.currentQuestion.question_id,
    allocations:{
        "R": 2.0,
        "I": 2.0,
        "A": 2.0,
        "S": 2.0,
        "E": 1.0,
        "C": 1.0,
    }
});
//计算总分配时间
const totalAllocated = computed(() => {
    return selectedIndex.value.reduce((acc, cur) => acc + cur, 0);
})
//计算总差时间
const totalVariation = computed(() => {
    return maxHours.value -totalAllocated.value;
})

//可以下一题
const canNext = computed(() => {
    return totalAllocated.value == maxHours.value;
});

//点击下一题
const handleNext = () => {
    if(canNext.value){
        quizStore.nextQuestion();
        quizStore.answers.push(answer.value);
    }
}

const canDoing = ref(true);

// 监听总时间，超过10个小时不能继续分配
watch(totalAllocated,(newVal) => {
    if(newVal >= maxHours.value){
        console.log("超过10个小时不能继续分配");
        canDoing.value = false;
    }else{
        canDoing.value = true;
    }
})

//点击进行渲染
const handleClick = (hourIndex,activityIndex) => {
    // 当第一次点击或者是当分配时间为0时
    if(selectedIndex.value[activityIndex] == 0 && canDoing.value){
        if(hourIndex <= totalVariation.value){
            selectedIndex.value[activityIndex] = hourIndex;
        }
    }else if(hourIndex == selectedIndex.value[activityIndex]){
        //当分配了时间后点击最后一个亮灯可以灭灯
        selectedIndex.value[activityIndex]--;
    }else if(selectedIndex.value[activityIndex] < 10 && hourIndex > selectedIndex.value[activityIndex]  && canDoing.value){
        if(hourIndex <= totalVariation.value){
            selectedIndex.value[activityIndex] = hourIndex;
        }
    }
}

const questions = {
            "question_id": 19,
            "type": "time_allocation",
            "title": "时间分配游戏",
            "content": "想象你有一个完全自由的周末，有 10 小时可以自由支配，请把时间分配给最想做的活动。",
            "options": [],
            "selected_option_id": null,
            "selected_option_ids": null,
            "rating_value": null,
            "metric_values": null,
            "allocations": null,
            "settings": {
                "max_hours": 10.0,
                "activities": [
                    {
                        "label": "动手制作",
                        "description": "制作手工艺品、修理物品、DIY 项目",
                        "dimension": "R"
                    },
                    {
                        "label": "学习研究",
                        "description": "阅读书籍、在线课程、探索新知识",
                        "dimension": "I"
                    },
                    {
                        "label": "创意设计",
                        "description": "绘画、写作、音乐创作、设计作品",
                        "dimension": "A"
                    },
                    {
                        "label": "朋友聚会",
                        "description": "与朋友交流、组织活动、团队协作",
                        "dimension": "S"
                    },
                    {
                        "label": "规划项目",
                        "description": "制定计划、策划方案、设定目标",
                        "dimension": "E"
                    },
                    {
                        "label": "整理优化",
                        "description": "整理空间、优化系统、完善细节",
                        "dimension": "C"
                    }
                ]
            }
        }

        const tubiao = ['🛠️','📚','👥','🎨','📋','🤝'];




</script>

<template>
    <div class="game-container">
        <div class="second-container">
            <img src="../../../assets/iconfont/backgroud1.png" alt=""></img>
            <div class="first-container"></div>
        </div>
        <div class="third-container">
            <h1>⏰ 时间分配游戏 </h1>
            <p>想象你有一个完全自由的周末，有10小时可以自由支配</p>
            <div class="time">
                总时间剩余 :
                <ul>
                    <li v-for="v in 10">🕙</li>
                </ul>
                <div class="number">
                    {{ questions.settings.max_hours }}小时
                </div>
            </div>
            <div class="middle">
                <li v-for="(value,index) in questions.settings.activities">
                    <div class="title">
                        {{ tubiao[index] }}<div class="text"><h3>{{ value.label }}</h3><p>{{ value.description }}</p></div>
                    </div>
                    <div class="atribution">
                        分配时间:
                        <span>{{selectedIndex[index]}}小时</span>
                    </div>
                    <div class="button-group">
                        <div class="button" v-for="(i,id) in 10" @click="handleClick(id + 1,index)" :class="{active : id + 1 <= selectedIndex[index]}">
                            <span v-show="id + 1 <= selectedIndex[index]">{{ i }}</span>
                        </div>
                    </div>
                </li>
            </div>
            <div class="bottom">
                <p>*点击方格分配时间，每个方格代表1小时*</p>
                <div class="bottom-button" @click="handleNext()" :class="{disabled:!canNext}">
                    分配完成 <i class="iconfont icon-youjiantou"></i>
                </div>
            </div>
        </div>
    </div>
</template>

<style lang="scss">
    .game-container{
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
            padding: 0 16px;
            width: 100%;
            height: 100px;
            position: absolute;
            top: 0;
            left: 0;
            z-index: 100;
            text-align: center;
            h1{
                margin-top: 30px;
                font-size: 36px;
                line-height: 40px;
                color: transparent;
                background-clip: text;
                background-image: linear-gradient(to right,#60a5fa , #6366f1 , #9333ea);
            }
            p{
                margin-top: 16px;
                font-size: 17px;
                 color: #d1d5db;
            }
            .time{
                display: flex;
                justify-content: start;
                padding: 8px 24px;
                margin: 25px auto;
                margin-bottom: 44px;
                height: 42px;
                width: 34%;
                color: #d1d5db;
                font-size: 17px;
                background-color: #ffffff0d;
                border: 1px solid #ffffff1a;
                border-radius: 999px;
                ul{
                    display: flex;
                    margin-left: 20px;
                    margin-right: 5px;
                    li{
                        margin-right: 4px;
                    }
                }
                .number{
                    font-size: 15px;
                    font-weight: 600;
                }
            }
            .middle{
                display: flex;
                justify-content: space-between;
                flex-wrap: wrap;
                align-content: space-between;
                margin-top: 20px;
                height: 360px;
                width: 100%;
                // background-color: pink;
                li{
                    transition: .5s ;
                    padding: 20px;
                    height: 47%;
                    width: 32%;
                    background-color: #3b82f60e;
                    // background-color: #fff;
                    border: 1px solid #ffffff1a;
                    border-radius: 12px;
                    &:hover{
                        background-color: #3f81ef40;
                        transform: translateY(-2px);
                    }
                    .title{
                        display: flex;
                        align-items: center;
                        font-size: 24px;
                        h3{
                            text-align: start;
                            margin-left: 12px;
                            font-size: 18px;
                            line-height: 28px;
                        }
                        p{
                            margin-left: 12px;
                            margin-top: 2px;
                            font-size: 14px;
                            line-height: 20px;
                            color: #9ca3af;
                        }
                    }
                    .atribution{
                        margin-top: 16px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        font-size: 14px;
                        color: #d1d5db;
                        span{
                            font-size: 16px;
                            font-weight: 500;
                            color: #facc15;
                        }
                    }
                    .button-group{
                        margin-top: 4px;
                        display: flex;
                        justify-content: space-between;
                        div{
                            transition: all 0.3s;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            width: 7.2%;
                            height: 32px;
                            background-color: #1f293780;
                            border-radius: 6px;
                            border: 1px solid #374151;
                            &:hover{
                                background-color: #37415180;
                                cursor: pointer;
                            }
                            &:active{
                                transform: scale(0.91);
                            }
                            &.active{
                                background-color: #facc15;
                            }
                            span{
                                color: #1f2937;
                                font-weight: 700;
                            }
                        }
                    }
                }
            }
            .bottom{
                margin-top: 35px;
                height: 125px;
                text-align: center;
                p{
                    font-size: 14px;
                    color: #9ca3af;
                }
                .bottom-button{
                    transition: all 0.3s;
                    width: 10%;
                    margin-top: 20px;
                    margin: 20px auto 0;
                    padding: 12px 32px;
                    border-radius: 8px;
                    background-image: linear-gradient(to right,#3b82f6 , #4f46e5);
                    &:hover{
                        background-image: linear-gradient(to right,#2563eb , #4338ca);
                        transform: scale(1.04);
                        cursor: pointer;
                    }
                    &:active{
                        transform: scale(0.95);
                    }
                    &.disabled{
                        color: #94a3b8;
                        background-color: #334155;
                        background-image: none;
                        .iconfont{
                            color: #94a3b8;
                        }
                    }
                }
            }
        }
    }
</style>