import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home/index.vue'
import Login from '../views/Login/index.vue'
import Register from '../views/Register/index.vue'
import RegisterExplorer from '../views/Register-explorer/index.vue'
import Evaluation from '../views/Evaluation/index.vue'
import Time from '../views/Evaluation/Game/time_allocation.vue'
import Values from '../views/Evaluation/Game/value_balance.vue'
import Question from '../views/Evaluation/Game/question.vue'
import Report from '../views/Report/index.vue'
import User from '../views/User/index.vue'
import Document from '../views/Evaluation/Document/index.vue'
import CareerExplore from '../views/CareerExplore/index.vue'
import Career from '../views/Career/index.vue'
import Cosplay from '../views/Cosplay/index.vue'
import Community from '../views/Comunity/index.vue'
import Group from '../views/Comunity/group.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component : Home
    },{
      path: '/login',
      name: 'Login',
      component: Login
    },{
      path: '/register-option',
      name: 'Register-option',
      component: Register
    },{
      path: '/register-explorer',
      name: 'Register-explorer',
      component: RegisterExplorer
    },{
      path: '/evaluation',
      name: 'Evaluation',
      component: Evaluation,
    },{
      path: '/time_allocation',
      component: Time
    },{
      path: '/value_balance',
      component: Values
    },{
      path: '/question',
      component: Question
    },{
      path: '/report',
      component: Report
    },{
      path: '/user',
      component: User
    },{
      path: '/document',
      component: Document,
    },{
      path: '/career-explore',
      component: CareerExplore,
    },{
      path: '/career',
      component: Career,
    },{
      path: '/cosplay',
      component: Cosplay,
    },{
      path:'/community',
      component: Community,
    },{
      path:'/group',
      component: Group,
    }
  ],

   //路由滚动行为定制
  scrollBehavior(){
    return{
      top: 0
    }
  }
})

export default router
