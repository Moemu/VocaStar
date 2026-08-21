<script setup>
    import { ref, onMounted} from 'vue'
    import { useQuizStore } from '../../../../stores/quiz';
    const quizStore = useQuizStore();
    const answer = ref({
        type: 'word_choice',
        question_id : quizStore.currentQuestion.question_id,
        option_ids : [],
    });

    const canNext = ref(false);


    const id = ref(-1);
    const time = ref(0);
    const question =   {
            "question_id": 15,
            "type": "word_choice",
            "title": "快速选择词汇",
            "content": "请在 10 秒内从词汇云中选择 3 个最吸引你的词语",
            "options": [
                {
                    "id": 57,
                    "text": "创新",
                    "dimension": "A",
                    "image_url": null
                },
                {
                    "id": 58,
                    "text": "稳定",
                    "dimension": "C",
                    "image_url": null
                },
                {
                    "id": 59,
                    "text": "分析",
                    "dimension": "I",
                    "image_url": null
                },
                {
                    "id": 60,
                    "text": "协作",
                    "dimension": "S",
                    "image_url": null
                },
                {
                    "id": 61,
                    "text": "冒险",
                    "dimension": "R",
                    "image_url": null
                },
                {
                    "id": 62,
                    "text": "细致",
                    "dimension": "C",
                    "image_url": null
                },
                {
                    "id": 63,
                    "text": "领导",
                    "dimension": "E",
                    "image_url": null
                },
                {
                    "id": 64,
                    "text": "技术",
                    "dimension": "R",
                    "image_url": null
                },
                {
                    "id": 65,
                    "text": "艺术",
                    "dimension": "A",
                    "image_url": null
                },
                {
                    "id": 66,
                    "text": "服务",
                    "dimension": "S",
                    "image_url": null
                },
                {
                    "id": 67,
                    "text": "规划",
                    "dimension": "E",
                    "image_url": null
                },
                {
                    "id": 68,
                    "text": "探索",
                    "dimension": "I",
                    "image_url": null
                }
            ],
            "selected_option_id": null,
            "selected_option_ids": null,
            "rating_value": null,
            "metric_values": null,
            "allocations": null,
            "settings": {
                "response_time_limit": 10,
                "max_select": 3
            }
        }

let timer = null;
time.value = question.settings.response_time_limit;
const startTimer = () => {
    let count = time.value;
    timer = setInterval(() =>{
        if(count <= 10 && count > 0){
            count--;
            time.value = count;
        }else if(count == 0){
            clearInterval(timer)
            nextQuestion();
        }
    },1000)
}

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
    }else if(answer.value.option_ids.length < question.settings.max_select){
        answer.value.option_ids.push(id)
    }
    if(answer.value.option_ids.length <= question.settings.max_select && answer.value.option_ids.length > 0){
        canNext.value = true;
    }else{
        canNext.value = false;
    }
    console.log(answer.value.option_ids)
}

const nextQuestion = () => {
        console.log("这是",time.value)
        if(time.value == 0 || canNext.value ){
            clearInterval(timer)
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

onMounted(() => startTimer())
</script>

<template>
    <div class="scenario-box">
        <div class="top">
            <h2>{{ question.title }}</h2>
            <p>{{ question.content }}</p>
            <div class="time-box">
                <i class="iconfont icon-shizhong"></i>{{ time }}s
            </div>
        </div>
        <div class="middle">
            <div class="option" v-for="(i,index) in question.options" :key="i.id" :style="{animationDelay: index * 0.1 + 's'}" @click= "toggleOption(i.id)" :class="{active: answer.option_ids.includes(i.id)}">
                {{ i.text }}
            </div>
        </div>
        <div class="button" @click="nextQuestion()" :class="{disabled:!canNext}">
            下一题
            <i class="iconfont icon-arrow-right"></i>
        </div>
    </div>

</template>

<style lang="scss" scoped>
    .scenario-box{
        margin: 0 auto;
        width: 51%;
        height: 558px;
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
            .time-box{
                position: absolute;
                top: 28px;
                right: 30px;
                padding: 8px 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #f87171;
                font-size: 20px;
                font-weight: 700;
                background-color: #dc262633;
                border-radius: 8px;
                .iconfont{
                    margin-right: 6px;
                    font-size: 20px;
                    color: #f87171;
                }
            }
        }
        .middle{
            display: flex;
            justify-content: center;
            align-items: start;
            flex-direction: row;
            flex-wrap: wrap;
            gap: 15px;
            margin-top: 30px;
            padding: 32px;
            height: 300px;
            background-color: #1e293b4d;
            border-radius: 12px;
            .option{
                animation: 2s move linear infinite alternate ;
                transition: all 0.1 ease;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 0;
                width: 11%;
                height: 20%;
                font-size: 16px;
                font-weight: 500;
                border-radius: 999px;
                background-color: #1e293b80;
                // background-color: pink;
                &:hover{
                    cursor: pointer;
                    transform: scale(1.04);
                }
                &:active{
                    transform: scale(0.96);
                }
                &.active{
                    background-color: #a855f7;
                    transition: all 0.2s ease !important;
                }
            }
            @keyframes move {
                50%{
                    transform: translatex(3px);
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