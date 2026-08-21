import { defineStore } from "pinia";
import {  StartQuizAPI, GetQuestionAPI, answerQuestionAPI, submitQuizAPI, submitProfileAPI } from "../apis/quiz"
import { ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";

export const useQuizStore = defineStore('quiz', () =>{
    const router = useRouter();
     //定义目前的题目数据state
    const currentQuestion = ref({});
    //定义当前题目的index
    const currentIndex = ref(0);
    //定义当前题目的总数
    const totalQuestion = ref(0);


    //定义提交答案的state数据
    let session_id =ref("");
    const answers = ref([]);

    //定义测评结束的state数据
    const report = ref({});



    //定义开始测评的数据
    const message = ref({});

    //定义开始测评的action函数
    const startQuiz = async ({slug}) => {
        const res = await StartQuizAPI({slug})
        message.value = res.data;
        // console.log(message.value.session_id);
        await getQuestion(message.value.session_id);
        //给session_id赋值
        session_id.value = message.value.session_id;
        console.log(session_id.value);
    }

    const questions = ref({});
    //定义获取测评题目的action函数
    const getQuestion = async (session_id) => {
        const res = await GetQuestionAPI(session_id);
        questions.value = res.data;
        console.log(questions.value.questions);
        console.log("这是" , questions.value.questions)
        // 初始化数据
        if(questions.value.questions){
            currentQuestion.value = questions.value.questions[0];
            totalQuestion.value = questions.value.questions.length;
            currentIndex.value = 0;
        }
        answers.value = [];
    }

    //定义下一题的action函数
    const nextQuestion = async () => {
        if(currentIndex.value + 1 < totalQuestion.value){
            currentIndex.value ++;
            currentQuestion.value = questions.value.questions[currentIndex.value];
        }else{
            console.log(session_id)
            await submitAnswer();
            await submitQuiz();
            router.push({path: '/report'})
            ElMessage({message: '已生成你的个人职业发展报告', type:'success'})
            console.log('提交答案');
            console.log(report);
            return;
        }
        if(currentQuestion.value){
            if(currentQuestion.value.type == 'time_allocation'){
                router.push({path: '/time_allocation'});
            }else if(currentQuestion.value.type == 'value_balance'){
                router.push({path: '/value_balance'});
            }else{
                router.push({path: '/question'})
            }
        }
    }

    //定义上一题的action函数
    const prevQuestion = () => {
        if(currentIndex.value > 0){
            currentIndex.value --;
            currentQuestion.value = questions.value.questions[currentIndex.value];
        }else{
            router.push({path: '/evaluation'})
        }
    }


    // 定义提交答案的action函数
    const submitAnswer = async () => {
        const res = await answerQuestionAPI({session_id: session_id.value, answers: answers.value});
        // answers.value = [];
    }

    // 定义提交测评的action函数
    const submitQuiz = async () => {
        console.log(session_id.value)
        const res = await submitQuizAPI({session_id: session_id.value});
        report.value = res.data;
    }

    //定义完善星际档案的state数据
    const questionN = ref('first');
    const qN = ref(0);
    const firstId = ref(-1);
    const firstAS = ref('');
    const secondAS = ref('');
    const thirdAS = ref('');
    const fourthAS = ref([]);
    const fourthId = ref([]);
    // 保存可以下一步的state数据
    const firstNext = ref(false);
    const secondNext = ref(false);
    const thirdNext = ref(false);
    const fourthNext = ref(false);
     console.log(questionN.value)
    //定义下一个星际档案题目的action函数
    const nextQN = () => {
        if(questionN.value == 'first'){
            questionN.value = 'second';
        }else if(questionN.value =='second'){
            questionN.value = 'third';
        }else if(questionN.value == 'third'){
            questionN.value = 'fourth';
        }
        console.log(questionN.value)
        console.log('调用了nextQN');
    }
    //定义上一个星际档案题目的action函数
    const prevQN = () => {
        if(questionN.value == 'fourth'){
            questionN.value = 'third';
        }else if(questionN.value == 'third'){
            questionN.value ='second';
        }else if(questionN.value =='second'){
            questionN.value = 'first';
        }
    }

    //定义提交星际档案的action函数
    const subProfile = async () => {
        const res = await submitProfileAPI({career_stage: firstAS.value, major: secondAS.value, career_confusion: thirdAS.value, short_term_goals: fourthAS.value});
    }

    return {
        message,
        questions,
        currentQuestion,
        totalQuestion,
        currentIndex,
        answers,
        report,
        session_id,
        questionN,
        qN,
        firstId,
        secondAS,
        thirdAS,
        fourthId,
        firstAS,
        fourthAS,
        firstNext,
        secondNext,
        thirdNext,
        fourthNext,

        startQuiz,
        getQuestion,
        nextQuestion,
        prevQuestion,
        submitAnswer,
        submitQuiz,
        nextQN,
        prevQN,
        subProfile,
    }
},{
    persist: true,
})