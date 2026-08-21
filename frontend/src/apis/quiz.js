import request from '../utils/http'
import qs from 'qs'

export const StartQuizAPI = ({slug}) => {
    return request({
        url: '/api/quiz/start?slug=' + slug,
        method: 'post',
        // data: qs.stringify({slug}),
        headers: {
            'Content-Type': 'application/json'
        }
    })
}

export const GetQuestionAPI = (session_id) =>{
    return request({
        url: '/api/quiz/questions',
        method: 'get',
        params: { session_id },
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    })
}

// 封装答案提交接口api
export const answerQuestionAPI = ({session_id, answers}) => {
    return request({
        url: '/api/quiz/answer',
        method: 'post',
        data: JSON.stringify({session_id, answers}),
        headers: {
            'Content-Type': 'application/json'
        }
    })
}

// 封装提交测试接口
export const submitQuizAPI = ({session_id}) => {
    return request({
        url: '/api/quiz/submit',
        method: 'post',
        data: JSON.stringify({session_id}),
        headers: {
            'Content-Type': 'application/json'
        }
    })
}

// 封装提交个性化档案接口
export const submitProfileAPI = ({career_stage,major,career_confusion,short_term_goals}) => {
    return request({
        url:'/api/quiz/profile',
        method: 'post',
        data: JSON.stringify({career_stage,major,career_confusion,short_term_goals}),
        headers: {'Content-Type': 'application/json'}
    })
}

export const getReportAPI = () => {
    return request({
        url: '/api/quiz/report',
        method: 'get',
    })
}