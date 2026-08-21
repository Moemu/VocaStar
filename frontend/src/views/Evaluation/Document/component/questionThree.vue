<script setup>
import { useQuizStore } from '../../../../stores/quiz';
import { ref, watch } from 'vue';
const quizStore = useQuizStore();


watch(() => quizStore.thirdAS,(newVal,oldVal) => {
    if(newVal.length != 0){
        if(oldVal.length == 0){
            quizStore.thirdNext = true;
            quizStore.qN++;
        }else{
            quizStore.thirdNext = true;
        }
    }else{
        if(oldVal.length != 0){
            quizStore.qN--;
            quizStore.thirdNext = false;
        }else{
            quizStore.thirdNext = false;
        }
    }
})

const canNext = () => {
    if(quizStore.thirdNext){
        quizStore.nextQN()
    }
}


</script>


<template>
    <div class="question3-container">
        <h3>
            <div class="left">
                <span class="number">3</span>你当前的主要职业困惑<span class="fuhao">*</span>
            </div>
            <div class="right" @click="quizStore.prevQN()">
                <i class="iconfont icon-xiangzuojiantou"></i>
                返回
            </div>
        </h3>
        <!-- <p>选择最符合你当前状态的选项</p> -->
        <textarea type="text" name="major" v-model="quizStore.thirdAS" placeholder="请告诉我们你在职业探索中遇到的疑问或挑战"/>
        <p>（例如：不确定专业是否适合自己、不知道如何转行、缺乏发展方向等）</p>
        <div class="bottom-box">
            <div class="button" @click="canNext()" :class="{disabled: quizStore.thirdNext}">
                下一步<i class="iconfont icon-arrow-right"></i>
            </div>
        </div>
    </div>

</template>


<style lang="scss">
    .question3-container {
        overflow: hidden;
        width: 100%;
        height: 100%;
        // background-color: pink;
        h3{
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 20px;
            line-height: 28px;
            .left{
                display: flex;
                align-items: center;
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
                    color: #facc15;
                    background-color: #eab3084d;
                    border-radius: 999px;
                }
                .fuhao{
                    color: #ef4444;
                }
            }
            .right{
                display: flex;
                align-items: center;
                font-size: 14px;
                line-height: 20px;
                color: #9ca3af;
                .iconfont{
                    margin-right: 6px;
                    color: #9ca3af;
                    font-size: 18px;
                }
                &:hover{
                    cursor: pointer;
                    color: #fff;
                    .iconfont{
                        color: #fff;
                    }
                }
            }
        }
        p{
            margin-top: 8px;
            font-size: 14px;
            line-height: 20px;
            color: #9ca3af;
        }
        .bottom-box{
            display: flex;
            justify-content: end;
            margin-top: 20px;
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
        textarea{
            transition: all 0.2s linear;
            resize: none;
            appearance: none;
            outline: none;
            font: inherit;
            color: inherit;
            -webkit-appearance: none;
            margin-top: 25px;
            padding: 12px 16px;
            width: 100%;
            height: 146px;
            background-color: #11182799;
            border-radius: 12px;
            border: 1px solid #374151;
            color: #fff;
            font-size: 16px;
            outline: none;
            &:focus{
                border: 2px solid #fff;

            }
        }
    }
</style>