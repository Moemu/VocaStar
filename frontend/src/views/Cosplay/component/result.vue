<script setup>
import { ref,computed } from 'vue';
import { useCosplayStore } from '../../../stores/cosplay';
const cosplayStore = useCosplayStore();

//先定义字母->能力项的能力
const changePoint = {
    'T': "技术决策",
    'S': "沟通协作",
    'P': "项目管理",
    'Q': "工匠精神",
};

const changePointList = computed(() => {
    return Object.entries(cosplayStore.cosplayChoice.score_changes);
})

const nextScene = () => {
    cosplayStore.component = 'first';
}

</script>

<template>
    <div class="result">
        <h2>{{ cosplayStore.lastTitle }}</h2>
        <div class="tiao">
        </div>
        <div class="main-text">
            <h3>选择结果</h3>
            <div class="text">
                <p>{{ cosplayStore.cosplayChoice.outcome }}</p>
            </div>
            <div class="up">
                <li v-for="([key,score],index) in changePointList">{{ changePoint[key] }} <span :class="{ 'top': score > 0, 'down': score < 0 }">{{ score > 0 ? '+' : '' }}{{ score }}{{ score>0 ? '↑' : '↓' }}</span></li>
            </div>
        </div>
        <div class="submit" @click="nextScene()">
            下一个场景
            <i class="iconfont icon-youjiantou"></i>
        </div>
    </div>
</template>

<style lang="scss">
    .result{
        padding: 32px 16px;
        height: 602px;
        width: 100%;
        h2{
            text-align: center;
            font-size: 24px;
            font-weight: 32px;
        }
        .tiao{
            margin: 5px auto 0;
            // margin-top: 5px;
            width: 80px;
            height: 4px;
            background-image: linear-gradient(to right,#a855f7 , #3b82f6);
            border-radius: 999px;
        }
        .main-text{
            margin: 32px auto 0;
            padding: 32px;
            height: 338px;
            width: 44%;
            background-color: #1e293b80;
            border-radius: 16px;
            h3{
                text-align: center;
                font-size: 20px;
            }
            .text{
                margin-top: 16px;
                padding: 24px;
                height: 102px;
                background-color: #0f172ab3;
                border: 1px solid #334155;
                border-radius: 12px;
                p{
                    color: #cbd5e1;
                    font-size: 16px;
                    line-height: 26px;
                }
            }
            .up{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-top: 25px;
                height: 104px;
                // background-color: pink;
                li{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    width: 48%;
                    height: 44px;
                    font-size: 14px;
                    line-height: 29px;
                    // background-color: pink;
                    span{
                        margin-left: 10px;
                        color: #4ade80;
                        font-size: 14px;
                        line-height: 20px;
                        i{
                            font-size: 14px;
                            font-weight: 700;
                            color: #4ade80;
                        }
                    }
                    .down{
                        color:#f87171;
                    }

                }
            }
        }
        .submit{
            transition: all 0.3s ease;
            padding: 12px 32px;
            margin: 35px auto 0;
            width: 10.8%;
            // height: 48px;
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