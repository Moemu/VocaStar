<script setup>
import { useQuizStore } from '../../../../stores/quiz';
import { ref } from 'vue';
const quizStore = useQuizStore();
const options = ['高中生 - 探索初始轨道','大学生 - 构建知识星系','职场新人 - 刚刚启航 (0-3年)','资深宇航员 - 经验丰富 (3-8年)','星际指挥官 - 资深专家 (8年以上)']
const id = ref(-1);
const optionAS = ['高中生','大学生','职场新人','资深宇航员','星际指挥官'];

const handleClick = (index) => {
    quizStore.firstId = index;
    if(quizStore.firstAS.length != 0 && !quizStore.firstNext){
        quizStore.qN++;
    }
    quizStore.firstNext = true;
    quizStore.firstAS = optionAS[index];
}

const canNext = () => {
    if(quizStore.firstNext){
        quizStore.nextQN()
    }
}

</script>



<template>
    <div class="question1-container">
        <h3>
            <span class="number">1</span>
            你当前的星际航程阶段
            <span class="fuhao">*</span>
        </h3>
        <p>选择最符合你当前状态的选项</p>
        <div class="main-text">
            <li v-for="(i,index) in options" :key="index" @click="handleClick(index)" :class="{active: quizStore.firstId == index}"><span></span>{{ i }}</li>
        </div>
        <div class="bottom-box">
            <div class="button" @click="canNext()" :class="{disabled:quizStore.firstNext}">
                下一步<i class="iconfont icon-arrow-right"></i>
            </div>
        </div>
    </div>

</template>


<style lang="scss">
    .question1-container {
        overflow: hidden;
        width: 100%;
        height: 100%;
        // background-color: pink;
        h3{
            display: flex;
            align-items: center;
            font-size: 20px;
            line-height: 28px;
            .number{
                margin-right: 10px;
                display: flex;
                justify-content: center;
                align-items: center;
                width: 24px;
                height: 24px;
                font-size: 14px;
                font-weight: 700;
                line-height: 20px;
                color: #60a5fa;
                background-color: #3b82f64d;
                border-radius: 999px;
            }
            .fuhao{
                color: #ef4444;
            }
        }
        p{
            margin-top: 8px;
            font-size: 14px;
            line-height: 20px;
            color: #9ca3af;
        }
        .main-text{
            display: flex;
            flex-wrap: wrap;
            margin-top: 17px;
            width: 100%;
            gap: 12px;
            li{
                display: flex;
                align-items: center;
                padding: 16px;
                width: 49%;
                font-size: 16px;
                background-color: #11182780;
                border: 1px solid #374151;
                border-radius: 12px;
                span{
                    display: flex;
                    margin-right: 12px;
                    width: 20px;
                    height: 20px;
                    border-radius: 999px;
                    border: 2px solid #6b7280;
                }
                &:hover{
                    border-color: #6b7280;
                    cursor: pointer;
                }
                &.active{
                    border-color: #3b82f6;
                    background-color: #3b82f61a;
                    span{
                        background-color: #3b82f6;
                    }
                }
            }
        }
        .bottom-box{
            display: flex;
            justify-content: end;
            height: 40px;
            width: 100%;
            .button{
                display: flex;
                justify-content: center;
                align-items: center;
                width: 102px;
                height: 100%;
                font-weight: 700;
                // background-color: pink;
                border-radius: 8px;
                background-image: linear-gradient(to right,#3b82f6 , #4f46e5);
                opacity: 0.5;
                cursor: not-allowed;
                &:hover{
                    background-image: linear-gradient(to right,#2563eb , #4338ca);
                }
                &.disabled{
                    opacity: 1;
                    cursor: pointer;
                }
            }

        }
    }
</style>