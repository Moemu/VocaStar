<script setup>
import { useQuizStore } from '../../../../stores/quiz';
import { ref, watch } from 'vue';
const quizStore = useQuizStore();


watch(() => quizStore.secondAS,(newVal,oldVal) => {
    console.log('这是secondAS',newVal)
    if(newVal.length != 0){
        if(oldVal.length == 0){
            quizStore.secondNext = true;
            quizStore.qN++;
        }else{
            quizStore.secondNext = true;
        }
    }else{
        if(oldVal.length != 0){
            quizStore.qN--;
            quizStore.secondNext = false;
        }else{
            quizStore.secondNext = false;
        }
    }
})

const canNext = () => {
    if(quizStore.secondNext){
        quizStore.nextQN()
    }
}
</script>


<template>
    <div class="question2-container">
        <h3>
            <div class="left">
                <span class="number">2</span>你的专业<span class="fuhao">*</span>
            </div>
            <div class="right" @click="quizStore.prevQN()">
                <i class="iconfont icon-xiangzuojiantou"></i>
                返回
            </div>
        </h3>
        <!-- <p>选择最符合你当前状态的选项</p> -->
        <input type="text" name="major" placeholder="请输入你所学或感兴趣的专业方向" v-model="quizStore.secondAS" >
        <p>（例如：计算机科学、金融、心理学、机械工程等）</p>
        <div class="bottom-box">
            <div class="button" @click="canNext()" :class="{disabled:quizStore.secondNext}">
                下一步<i class="iconfont icon-arrow-right"></i>
            </div>
        </div>
    </div>

</template>


<style lang="scss">
    .question2-container {
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
                    color: #c084fc;
                    background-color: #a855f74d;
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
        input{
            transition: all 0.2s linear;
            appearance: none;
            outline: none;
            font: inherit;
            color: inherit;
            -webkit-appearance: none;
            margin-top: 25px;
            padding: 12px 16px;
            width: 100%;
            height: 50px;
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