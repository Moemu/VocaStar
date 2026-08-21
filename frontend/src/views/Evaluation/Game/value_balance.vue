<script setup>
import { ref, watch} from 'vue'
import { useQuizStore } from '../../../stores/quiz'
const quizStore = useQuizStore()
const answer = ref({
    type: "value_balance",
    question_id: quizStore.currentQuestion.question_id,
    values: {
        "R": 20.0,
        "I": 20.0,
        "A": 20.0,
        "S": 20.0,
        "E": 10.0,
        "C": 10.0
    }
});

const canNext = () => {
    let finalAnswer = JSON.parse(JSON.stringify(answer.value));
    quizStore.nextQuestion();
    quizStore.answers.push(finalAnswer);
}



const isFirstActive = ref([false,false,false]);
const isSecondActive = ref([false,false,false]);
const number = ref([50,50,50]);
const firstNumber = ref([50,50,50]);
const secondNumber = ref([50,50,50]);

const text = ref(["平衡倾向","平衡倾向","平衡倾向"]);


watch(number, (newNumber) => {
  newNumber.forEach((num, index) => {
    firstNumber.value[index] = num;
    secondNumber.value[index] = 100 - num;

    if (num == 50) {
      isFirstActive.value[index] = false;
      isSecondActive.value[index] = false;
      text.value[index] = "平衡倾向";
    } else if (num < 50) {
      isSecondActive.value[index] = true;
      isFirstActive.value[index] = false;
      const diff = 50 - num;
      text.value[index] = diff + "%偏向" + question?.settings.dimensions[index].label2;
    } else {
      isFirstActive.value[index] = true;
      isSecondActive.value[index] = false;
      const diff = num - 50;
      text.value[index] = diff + "%偏向" + question?.settings.dimensions[index].label1;
    }
  });
}, { deep: true });


// watch(number, (newNumber) => {
//     firstNumber.value = newNumber;
//     secondNumber.value = 100 - newNumber;
//     if(newNumber == 50){
//         isFirstActive.value = false;
//         isSecondActive.value = false;
//         text.value = "平衡倾向";
//     }
//     else if(newNumber < 50){
//         isSecondActive.value = true;
//         isFirstActive.value = false;
//         const diff = (50 - newNumber)
//         text.value = diff + "% 偏向稳定可靠";
//     }
//     else {
//         isFirstActive.value = true;
//         isSecondActive.value = false;
//         const diff = (newNumber - 50)
//         text.value = diff + "% 偏向创新探索";
//     }
// })

const question = {
                    "question_id": 18,
                    "type": "value_balance",
                    "title": "价值观天平",
                    "content": "通过拖动滑块，标记你对下列价值观的认同度（0-100%）。",
                    "options": [],
                    "selected_option_id": null,
                    "selected_option_ids": null,
                    "rating_value": null,
                    "metric_values": null,
                    "allocations": null,
                    "settings": {
                        "scale": {
                            "min_value": 0.0,
                            "max_value": 100.0,
                            "step": 1.0
                        },
                        "dimensions": [
                            {
                                "label1": "实干与成果",
                                "dimension1": "R",
                                "label2": "理性与探索",
                                "dimension2": "I"
                            },
                            {
                                "label1": "创意与表达",
                                "dimension1": "A",
                                "label2": "关怀与合作",
                                "dimension2": "S",
                            },{
                                "label1": "领导与影响",
                                "dimension1": "E",
                                "label2": "秩序与效率",
                                "dimension2": "C"
                            }
                        ]
                    }
                }





</script>

<template>
    <div class="game-container">
        <div class="second-container">
            <img src="../../../assets/iconfont/backgroud1.png" alt=""></img>
            <div class="first-container"></div>
        </div>
        <div class="third-container">
            <h1>🎯  题目10：价值观天平 </h1>
            <p>请拖动滑块，表达你对每对价值观的偏好:</p>
            <div class="middle-box">
                <div class="question" v-for="(value,index) in question.settings.dimensions">
                    <div class="title">
                        <h4 class="first-title" :class="{active: isFirstActive[index]}">{{ value.label1 }}</h4>⚖️<h4 class="second-title" :class="{active: isSecondActive[index]}">{{ value.label2 }}</h4>
                    </div>
                    <input class="slider" type="range" min="0" max="100" value="50" v-model="number[index]">
                    <div class="text">
                        <p>你的倾向 :</p>
                        <h4>
                            {{ text[index] }}
                        </h4>
                    </div>
                    <div class="percentage">
                        <span>
                            {{firstNumber[index]}}%
                        </span>
                        <span>
                            {{secondNumber[index]}}%
                        </span>
                    </div>
                </div>
            </div>
            <div class="bottom">
                <p>*拖动滑块表达你的真实偏好，没有对错之分*</p>
                <div class="bottom-button" @click="canNext()">
                    继续探索 <i class="iconfont icon-youjiantou"></i>
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
                font-size: 20px;
                 color: #d1d5db;
            }
            .middle-box{
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                margin: 50px auto;
                padding: 32px;
                height: 800px;
                width: 49%;
                background-color: #ffffff0d;
                backdrop-filter: blur(4px);
                border: 1px solid #ffffff1a;
                border-radius: 16px;
                .question{
                    height: 204px;
                    // background-color: pink;
                    width: 100%;
                    .title{
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        font-size: 17px;
                        h4{
                            font-weight: 500;
                            font-size: 18px;
                            color: #d1d5db;
                            line-height: 28px;
                        }
                        .first-title{
                            &.active{
                                transition: all 0.3s ease;
                                color: #c084fc;
                                 box-shadow: -5px 5px 10px #c084fc;
                            }
                        }
                        .second-title{
                            &.active{
                                transition: all 0.3s ease;
                                color: #60a5fa;
                                 box-shadow: 5px 5px 10px #60a5fa;
                            }
                        }
                    }
                    .slider{
                        -webkit-appearance: none;
                        appearance: none;
                        margin-top: 25px;
                        width: 100%;
                        height: 23px;
                        border-radius: 999px;
                        border: 1px solid #ffffff1a;
                        background-color: #ffffff0d;

                        &::-webkit-slider-thumb{
                            -webkit-appearance: none;
                            appearance: none;
                            width: 28px;
                            height: 24px;
                            background: url(../../../assets/iconfont/星星.svg) no-repeat center!important;
                            background-size: contain;
                            cursor: pointer;
                        }
                    }
                    .text{
                        p{
                            font-size: 16px;
                            color: #d1d5db;
                        }
                        h4{
                            margin-top: 5px;
                            font-size: 20px;
                            color: #ffffff;
                            line-height: 28px;
                        }
                    }
                    .percentage{
                        display: flex;
                        justify-content: space-between;
                        color: #9ca3af;
                        font-size: 12px;
                    }
                }
            }
            .bottom{
                margin-top: 0px;
                height: 125px;
                text-align: center;
                p{
                    font-size: 14px;
                    color: #9ca3af;
                }
                .bottom-button{
                    transition: all 0.3s;
                    width: 10%;
                    margin: 30px auto 0;
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
                }
            }
        }
    }
</style>