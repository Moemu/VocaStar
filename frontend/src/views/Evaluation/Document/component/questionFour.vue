<script setup>
import { useQuizStore } from '../../../../stores/quiz';
import { ref } from 'vue';
import { useRouter } from 'vue-router';
const router = useRouter();
const quizStore = useQuizStore();
const options = ['找到合适的专业方向','获得实习/工作机会','提升特定技能能力','探索职业发展可能性','转换职业轨道','其他']
const id = ref(-1)
const text =ref('');
const handleClick = (index) => {
    console.log(index)
    console.log()
    if(quizStore.fourthAS.includes(options[index])){
        id.value = quizStore.fourthAS.findIndex(item => item == options[index]);
        quizStore.fourthAS.splice(id.value,1);
    }else{
        quizStore.fourthAS.push(options[index]);
        console.log('我被调用了')
    }
    if(quizStore.fourthAS.length == 0){
        if(quizStore.fourthNext){
            quizStore.qN--;
        }
        quizStore.fourthNext = false;
    }else{
        if(!quizStore.fourthNext){
            quizStore.qN++;
        }
        quizStore.fourthNext = true;
    }
}

const canNext = () => {
    if(quizStore.fourthNext){
        quizStore.subProfile();
        router.push({path: '/evaluation'});
    }
}

</script>


<template>
    <div class="question4-container">
        <h3>
            <div class="left">
                <span class="number">4</span>
                    你希望短期内实现什么目标？
                <span class="fuhao">*</span>
            </div>
            <div class="right" @click="quizStore.prevQN()">
                <i class="iconfont icon-xiangzuojiantou"></i>
                返回
            </div>
        </h3>
        <!-- <p>选择最符合你当前状态的选项</p> -->
        <div class="main-text">
            <li v-for="(i,index) in options" @click="handleClick(index)" :class="{active: quizStore.fourthAS.includes(options[index])}"><span></span>{{ i }}</li>
            <input type="text" name="major" placeholder="请输入你的其他目标" v-model="text"  v-if="quizStore.fourthAS.includes('其他')">
        </div>
        <div class="bottom-box">
            <div class="button" @click="canNext()" :class="{disabled:quizStore.fourthNext}">
                完成并生成报告<i class="iconfont icon-arrow-right"></i>
            </div>
        </div>
    </div>

</template>


<style lang="scss">
    .question4-container {
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
                    color: #4ade80;
                    background-color: #22c55e4d;
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
        .main-text{
            display: flex;
            flex-wrap: wrap;
            margin-top: 25px;
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
                    border-radius: 4px;
                    border: 2px solid #6b7280;
                }
                &:hover{
                    border-color: #6b7280;
                    cursor: pointer;
                }
                &.active{
                    border-color: #22c55e;
                    background-color: #22c55e1a;
                    span{
                        background-color: #4ade80;
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
                margin-top: 6px;
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
                width: 183px;
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