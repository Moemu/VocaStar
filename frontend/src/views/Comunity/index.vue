<script setup>
import { ref } from 'vue'
import { useCommunityStore } from '../../stores/community';
import study from './component/study.vue'
import partner from './component/partner.vue'
import teacher from './component/teacher.vue'

const groups = ['学习小组','职业伙伴','职业导师'];
const componentMap = [study,partner,teacher];
const mapIndex = ref(0);
const communityStore = useCommunityStore();

</script>

<template>
    <div class="community" :class="{ 'sun': communityStore.isSun }">
        <div class="top">
            <div class="text">
                <h1>学习社区</h1>
                <p>连接志同道合的学习者，共同成长</p>
            </div>
            <div class="button" @click="communityStore.isSun =!communityStore.isSun" v-if="!communityStore.isSun">
                <i class="iconfont icon-taiyang"></i>
            </div>
            <div class="button yueliang" @click="communityStore.isSun = !communityStore.isSun" v-if="communityStore.isSun">
                <i class="iconfont icon-yueliang"></i>
            </div>
        </div>
        <div class="choice">
            <div class="button">
                <li tabindex="0" v-for="(i,index) in groups" @click="mapIndex = index" :class="{ 'active': mapIndex == index }">{{ i }}</li>
            </div>
        </div>
        <component :is="componentMap[mapIndex]" />
    </div>

</template>

<style>
    .community {
        background-color: #111827;
        .top{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 24px 16px;
            height: 108px;
            border-bottom: 1px solid #4b5563;
            h1{
                font-size: 24px;
                line-height: 32px;
            }
            p{
                margin-top: 4px;
                color: #9ca3af;
                font-size: 16px;
            }
            .button{
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 10px;
                color: #d1d5db;
                border-radius: 999px;
                cursor: pointer;
                background-color: #1f2937;
                .iconfont{
                    font-size: 20px;
                }
                &:hover{
                    background-color: #374151;
                }

            }
            .yueliang{
                background-color: #f3f4f6;
                color: #374151;
                .iconfont{
                    color: #374151;
                }
                &:hover{
                    background-color: #e5e7eb;
                }
            }
        }
        .choice{
            margin: 0 auto;
            padding: 27px 0 33px;
            width: 30%;
            height: 110px;
            /* background-color: pink; */
            .button{
                display: flex;
                padding: 4px;
                height: 100%;
                background-color: #1f2937;
                border-radius: 8px;
                li{
                    flex: 1;
                    display: flex;
                    justify-content: center;
                    padding: 12px 16px;
                    font-size: 14px;
                    line-height: 20px;
                    color: #9ca3af;
                    font-weight: 500;
                    border-radius: 6px;
                    cursor: pointer;
                    &:hover{
                        color: #e5e7eb;
                    }
                    &:focus,&.active{
                        box-shadow: 0 0 0 calc(2px + 2px) rgb(59 130 246 / 1);
                        color: #e5e7eb;
                    }
                }
            }
        }
    }
    .sun{
        background-color: #fff;
        .top{
            border-color: #e5e7eb;
            h1{
                color: #111827;
            }
            p{
                color: #4b5563;
            }
        }
        .choice{
            .button{
                background-color: #f9fafb;
                border: 1px solid #e5e7eb;
                li{
                    color: #6b7280;
                    &:hover,&:focus{
                        color: #374151;
                    }
                }
            }
        }
    }

</style>