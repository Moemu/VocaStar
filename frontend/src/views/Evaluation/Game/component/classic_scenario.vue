<script setup>
    import { ref, watch } from 'vue'
    import { useQuizStore } from '../../../../stores/quiz'

    const quizStore = useQuizStore();
    const id = ref(-1);
    console.log(id.value)
    const options = ref([]);
    const isCanNext = ref(false);
    //定义答案
    const answer = ref({
        type: "classic_scenario",
        question_id : quizStore.currentQuestion.question_id,
        option_id : id.value,
    });

    quizStore.answers = []

    const clickAnswer = (newId) => {
        id.value = newId;
        answer.value.option_id = newId;
        // console.log(id.value);
        console.log(answer.value);
    }

    watch(
        () => id.value,
        (newId) => {
            if(newId != -1){
                 isCanNext.value = true;
            }
    })


    // 直接通过 watch 监听 currentQuestion 的变化，自动更新 options
    watch(
    () => quizStore.currentQuestion,
    (newQuestion) => {
        if (newQuestion) { // 防止初始为空时报错
        options.value = newQuestion.options || [];
        }
        answer.value.question_id = newQuestion.question_id;
        id.value = -1;
        isCanNext.value = false;
    },
    { immediate: true } // 立即执行一次，确保初始化时也能加载数据
    );

    // 提交答案并且切换到下一题
    const submitAnswer = () => {
        // 切换下一题
        let finalAnswer = JSON.parse(JSON.stringify(answer.value));
         quizStore.nextQuestion();
        if(quizStore.answers.length < quizStore.totalQuestion && quizStore.currentIndex >= quizStore.answers.length){
            quizStore.answers.push(finalAnswer);
        }else{
            quizStore.answers.splice(quizStore.currentIndex - 1, 1, finalAnswer);
        }
        console.log("这是",quizStore.answers,quizStore.totalQuestion,quizStore.currentIndex)
    }




    // const options = [
    //             {
    //                 "id": 33,
    //                 "text": "动手搭建坚固的住所和生存工具",
    //                 "dimension": "R",
    //                 "image_url": null
    //             },
    //             {
    //                 "id": 34,
    //                 "text": "研究探索岛上的动植物生态系统",
    //                 "dimension": "I",
    //                 "image_url": null
    //             },
    //             {
    //                 "id": 35,
    //                 "text": "设计创作独特的求救信号和地图",
    //                 "dimension": "A",
    //                 "image_url": null
    //             },
    //             {
    //                 "id": 36,
    //                 "text": "照顾安抚大家的情绪，组织集体活动",
    //                 "dimension": "S",
    //                 "image_url": null
    //             }
    //         ]

</script>

<template>
    <div class="scenario-box">
        <div class="top">
            <h2>{{ quizStore.currentQuestion.title }}</h2>
            <p>{{ quizStore.currentQuestion.content }}</p>
        </div>
        <div class="middle">
            <div class="option" v-for="i in options" :key="i.id" @click="clickAnswer(i.id)" :class="{active: i.id == id }">
                {{ i.text }}
            </div>
        </div>
        <div class="button" @click="isCanNext ? submitAnswer() : null" :class="{ 'disabled' : !isCanNext}">
            下一题
            <i class="iconfont icon-arrow-right"></i>
        </div>
    </div>

</template>

<style lang="scss" scoped>
    .scenario-box{
        margin: 0 auto;
        width: 51%;
        height: 600px;
        // background-color: pink;
        .top{
            padding: 24px;
            height: 145px;
            border-radius: 12px;
            background-color: #1e293b80;
            h2{
                font-size: 20px;
            }
            p{
                font-size: 18px;
                color: #e2e8f0;
                margin-top: 16px;
            }
        }
        .middle{
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            margin-top: 30px;
            height: 342px;
            // background-color: #fff;
            .option{
                transition: all 0.3s ease;
                padding: 24px;
                height: 74px;
                background-color: #1e293b4d;
                color: #e2e8f0;
                font-size: 17px;
                border-radius: 12px;
                border: 1px solid #334155;
                &:hover{
                    cursor: pointer;
                    transform: scale(1.02);
                }
                &:active{
                    transform: scale(0.98);
                }
                &.active{
                    border-color: #a855f7;
                    background-color: #9333ea1a;
                }
            }
        }
        .button{
            transition: all 0.3s ease;
            padding: 12px 32px;
            margin: 35px auto 0;
            width: 17%;
            height: 48px;
            border-radius: 12px;
            font-weight: 700;
            background-image: linear-gradient(to right, #9333ea , #2563eb);
            &:hover{
                background-image: linear-gradient(to right, #7e22ce , #1d4ed8);
                transform: scale(1.04);
                cursor: pointer;
            }
            &:active{
                transform: scale(0.98);
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

</style>