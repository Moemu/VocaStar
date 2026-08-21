<script setup>
import assignment from './component/assignment.vue';
import result from './component/result.vue';
import report from './component/report.vue'
import { useCosplayStore } from '../../stores/cosplay';
import { ref,onMounted,computed, watch } from 'vue';
const cosplayStore = useCosplayStore();
const componentList = {
    first: assignment,
    second: result,
    third: report
}

// const questionType = ref(cosplayStore.cosplaySession?.state?.current_scene_index)
// // 监听题目题
// watch(questionType,async (newVal,oldVal) =>{
//     console.log("题目重新为1，重新创建对话");
//     if(newVal  == 0 && newVal != oldVal){
//         await cosplayStore.CreateCosplay(1);
//     }
// },{immediate: false})


cosplayStore.component = 'first';
const component = ref('');
component.value = cosplayStore?.component;

const getCosplayList = async () => {
    await cosplayStore.CosPlayList(1);
    await cosplayStore.CreateCosplay(1);
    console.log('这是',cosplayStore.cosplaySession);
    console.log('这是',cosplayStore.cosplayList);
}

// 根据pinia中的题型类型，动态获取对应的组件
const type = computed(() => {
    if(cosplayStore.component){
        const cosplayType = cosplayStore.component;
        return componentList[cosplayType] || null;//无匹配时返回null
    }
    return null;//无匹配时返回null
})

onMounted(() => {
    getCosplayList();
})
</script>

<template>
    <div class="cosplay">
        <div class="box">
            <div class="left" @click="$router.push('/career')">
                <i class="iconfont icon-xiangzuojiantou"></i>返回星球
            </div>
            <p>情景{{cosplayStore.cosplaySession?.state?.current_scene_index + 1}}/{{ cosplayStore.cosplaySession?.state?.total_scenes}}</p>
        </div>
        <div class="top-loading">
            <div class="loading-container">
                <div class="capacity" v-for="i in cosplayStore.cosplaySession?.state?.abilities">
                    {{ i.name }}
                    <div class="loading">
                        <div class="bgc" :style="{width: cosplayStore.cosplaySession?.state?.scores[i.code] + '%'}"></div>
                    </div>
                    <span>{{ cosplayStore.cosplaySession?.state?.scores[i.code] }}</span>
                </div>
            </div>
        </div>
        <component :is="type"/>
    </div>

</template>
<style lang="scss">
    .cosplay{
        width: 100%;
        background-image: linear-gradient(to bottom, #0f172a , #020617);
        .box{
            position: fixed;
            top: 0;
            left: 0;
            z-index: 999;
            display: flex;
            align-items: center;
            // justify-content: space-between;
            padding: 12px 16px;
            width: 100%;
            height: 52px;
            background: #0f1a2bcc;
            backdrop-filter: blur(12px);
            border-bottom: 1px solid #1e293b;
            .left{
                display: flex;
                align-items: center;
                width: 12%;
                font-size: 16px;
                color: #cbd5e1;
                .iconfont{
                    margin-right: 10px;
                    font-size: 20px;
                    font-weight: 700;
                    color: #cbd5e1;
                }
                &:hover{
                    cursor: pointer;
                    color: #fff;
                    .iconfont{
                        color: #fff;
                    }
                }
            }
             p{
                    position: absolute;
                    left: 50%;
                    top: 50%;
                    transform: translate(-25%, -50%);
                    font-size: 14px;
                    font-weight: 500;
                    color: #94a3b8;
            }
        }
        .top-loading{
            padding-top: 52px;
            height: 93px;
            .loading-container{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0 16px;
                height: 41px;
                background-color: #1e293b80;
                border-bottom: 1px solid #1e293b;
                .capacity{
                    display: flex;
                    align-items: center;
                    color: #94a3b8;
                    font-size: 12px;
                    .loading{
                        margin-top: 4px;
                        margin-left: 25px;
                        margin-right: 20px;
                        width: 96px;
                        height: 6px;
                        border-radius: 999px;
                        background-color: #33415580;
                        .bgc{
                            transition: all 1s ease;
                            width: 100%;
                            height: 100%;
                            border-radius: 999px;
                            background-image: linear-gradient(to right,#a855f7 , #3b82f6);
                        }
                    }
                }
            }
        }
    }
</style>