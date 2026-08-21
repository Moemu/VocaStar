<script setup>
    import { ref, onMounted, watch} from 'vue'
    import { useQuizStore } from '../../../../stores/quiz'
    const quizStore = useQuizStore();

    const answer = ref({
        type: 'image_preference',
        question_id : quizStore.currentQuestion.question_id,
        option_ids : [],
    });

    const baseUrl = ref(import.meta.env.VITE_API_BASE_URL || '');

    const canNext = ref(false);
    const question = ref({});
    question.value = quizStore.currentQuestion;
    console.log("这个是第一个图片题目",question.value);

    // 直接通过 watch 监听 currentQuestion 的变化，自动更新 options
    watch(
    () => quizStore.currentQuestion,
    (newQuestion) => {
        //如果进入下一题就重置答案选项
        answer.value.option_ids = [];
        if (newQuestion) { // 防止初始为空时报错
            question.value = newQuestion || {};
            answer.value.question_id = newQuestion.question_id;
        }
        console.log('这个是',question.value)
    },
    { immediate: true } // 立即执行一次，确保初始化时也能加载数据
    );

    // const question = {
    //         "question_id": 16,
    //         "type": "image_preference",
    //         "title": "图片偏好题（场景一）",
    //         "content": "从以下图片中选择最吸引你的 2 张。每张图片代表一个兴趣维度。",
    //         "options": [
    //             {
    //                 "id": 69,
    //                 "text": "图片 A（对应 C）",
    //                 "dimension": "C",
    //                 "image_url": "/static/quiz-options/P8A.webp"
    //             },
    //             {
    //                 "id": 70,
    //                 "text": "图片 B（对应 E）",
    //                 "dimension": "E",
    //                 "image_url": "/static/quiz-options/P8B.webp"
    //             },
    //             {
    //                 "id": 71,
    //                 "text": "图片 C（对应 S）",
    //                 "dimension": "S",
    //                 "image_url": "/static/quiz-options/P8C.webp"
    //             },
    //             {
    //                 "id": 72,
    //                 "text": "图片 D（对应 A）",
    //                 "dimension": "A",
    //                 "image_url": "/static/quiz-options/P8D.webp"
    //             },
    //             {
    //                 "id": 73,
    //                 "text": "图片 E（对应 I）",
    //                 "dimension": "I",
    //                 "image_url": "/static/quiz-options/P8E.webp"
    //             },
    //             {
    //                 "id": 74,
    //                 "text": "图片 F（对应 R）",
    //                 "dimension": "R",
    //                 "image_url": "/static/quiz-options/P8F.webp"
    //             }
    //         ],
    //         "selected_option_id": null,
    //         "selected_option_ids": null,
    //         "rating_value": null,
    //         "metric_values": null,
    //         "allocations": null,
    //         "settings": {
    //             "max_select": 2
    //         }
    //     }

const toggleOption = (id) => {
    if(!Array.isArray(answer.value.option_ids)){
        answer.value.option_ids = []
    }
    //1查找当前ID在选中数组的位置
    const index = answer.value.option_ids.indexOf(id);
    //2如果存在，则从选中数组中删除
    if(index > -1){
        answer.value.option_ids.splice(index,1)
    //3如果不存在，且选中数组未满，则添加到选中数组
    }else if(answer.value.option_ids.length < question.value.settings.max_select){
        answer.value.option_ids.push(id)
    }
    console.log(answer.value.option_ids)
     if(answer.value.option_ids.length <= 2 && answer.value.option_ids.length > 0){
        canNext.value = true;
    }else{
        canNext.value = false;
    }
}

const nextQuestion = () => {
        if(canNext.value){
           let finalAnswer = JSON.parse(JSON.stringify(answer.value));
            quizStore.nextQuestion();
            if(quizStore.answers.length < quizStore.totalQuestion && quizStore.currentIndex >= quizStore.answers.length){
                quizStore.answers.push(finalAnswer);
            }else{
                quizStore.answers.splice(quizStore.currentIndex - 1, 1, finalAnswer);
            }
            console.log("这是",quizStore.answers,quizStore.totalQuestion,quizStore.currentIndex)
        }
    }

</script>

<template>
    <div class="scenario-box">
        <div class="top">
            <h2>{{ question.title }}</h2>
            <p>{{ question.content }}</p>
        </div>
        <div class="image-middle">
            <div class="image-option" v-for="(i,index) in question.options" :key="i.id" @click= "toggleOption(i.id)" :class="{bctive: answer.option_ids.includes(i.id)}">
                <img :src="baseUrl + i.image_url" alt="">
            </div>
        </div>
        <div class="button" @click="nextQuestion()" :class="{disabled: !canNext}">
            下一题
            <i class="iconfont icon-arrow-right"></i>
        </div>
    </div>

</template>

<style lang="scss" scoped>
    .scenario-box{
        margin: 0 auto;
        width: 51%;
        height: 700px;
        // background-color: pink;
        .top{
            position: relative;
            padding: 24px;
            height: 121px;
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
        .image-middle{
            display: flex;
            justify-content: center;
            align-items: start;
            flex-direction: row;
            flex-wrap: wrap;
            gap: 15px;
            margin-top: 30px;
            padding: 32px;
            height: 450px;
            background-color: #1e293b4d;
            border-radius: 12px;
            .image-option{
                transition: all 0.3s ease;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 0;
                width: 30%;
                height: 45%;
                font-size: 16px;
                font-weight: 500;
                border-radius: 16px;
                background-color: #1e293b80;
                // background-color: pink;
                img{
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    border-radius: 16px;
                }
                &.bctive{
                     border: 5px solid #9333ea;
                }
                &:hover{
                    cursor: pointer;
                    transform: scale(1.06);
                }
                &:active{
                    transform: scale(0.96);
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