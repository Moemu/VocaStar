import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
// 导入重置样式
import '@/assets/resets.css'

//  导入element-plus里的icon图标
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

//  导入覆盖elMessage样式的scss
import './assets/element-variables.scss'
import 'element-plus/theme-chalk/el-message.css'

//引入pinia状态管理插件
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

const app = createApp(App)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

const pinia = createPinia()

//注册持久化插件
pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.use(router)

app.mount('#app')
