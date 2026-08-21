<script setup>
import { ref, computed} from 'vue'
import { useUserStore } from '../../../stores/user';
import { useRouter } from "vue-router";
import  classic_scenario from './component/classic_scenario.vue'
import word_choice from './component/word_choice.vue'
import image_preference from './component/image_preference.vue'
import { useQuizStore } from '../../../stores/quiz'

const quizStore = useQuizStore();
const router = useRouter();

// 注册组件
const components = {
    classic_scenario,
    word_choice,
    image_preference
}

// 根据pinia中的题型类型，动态获取对应的组件
const type = computed(() => {
    if(quizStore.currentQuestion){
        const questionType = quizStore.currentQuestion.type;
        return components[questionType] || null;//无匹配时返回null
    }
    return null;//无匹配时返回null
})

</script>

<template>
    <div class="question-container">
        <div class="container">
            <div class="left" v-if="quizStore.currentIndex == 0" @click="quizStore.prevQuestion()">
                <i class="iconfont icon-arrow-left-bold"></i>
                返回
            </div>
            <div class="left" v-else ="quizStore.currentIndex != 0" @click="quizStore.prevQuestion()">
                <i class="iconfont icon-arrow-left-bold"></i>
                上一题
            </div>

            <div class="middle">
                <img src="../../../assets/iconfont/地球.svg" alt="">
                <h1>职趣星航</h1>
            </div>
            <div class="right">
                {{quizStore.totalQuestion}}/{{ quizStore.currentIndex + 1 }}
                <div class="loadding"><div class="bgc" :style="{width: `${(quizStore.currentIndex + 1) / quizStore.totalQuestion * 100}%`}"></div></div>
            </div>
        </div>
        <component :is="type" />
    </div>
</template>

<style lang="scss">
   .question-container{
        position: relative;
        display: flex;
        padding: 100px 16px 32px;
        height: 820px;
        width: 100%;
        background-image: linear-gradient(to bottom, #0f172a , #020617);
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
            align-items: center;
            margin-left: 20px;
            width: 12%;
            font-size: 18px;
            color:#cbd5e1;
            .iconfont{
                margin-right: 10px;
                margin-top: 3px;
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

        .middle{
            display: flex;
            align-items: center;
            width: 12%;
            img{
                width: 40px;
                height: 40px;
            }
            h1{
                 margin-left: 5px;
                font-size: 20px;
                font-weight: 700;
                color: transparent;
                background-image: linear-gradient(to right,#c084fc,#3b82f6);
                background-clip: text;
            }
        }

        .right{
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 11%;
            // background-color: pink;
            color:#cbd5e1;
            font-size: 18px;
            .iconfont{
                margin-top: 5px;
                margin-left: 15px;
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
            .loadding{
                width: 120px;
                height: 6px;
                background-color: #33415580;
                border-radius: 999px;
                .bgc{
                    height: 100%;
                    background-image: linear-gradient(to right,#a855f7 , #3b82f6);
                    border-radius: 999px;
                }
            }
        }
    }
}
</style>