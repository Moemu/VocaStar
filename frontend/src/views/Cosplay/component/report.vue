<script setup>
import { onMounted, ref } from 'vue'
import { useCosplayStore } from '../../../stores/cosplay';
import { useRouter } from 'vue-router';
const router = useRouter();
const cosplayStore = useCosplayStore();



onMounted(() => {
    console.log(cosplayStore.cosplaySession?.state?.session_id);
    cosplayStore.FinalReport(cosplayStore.cosplaySession?.state?.session_id);
})

const again = async() => {
    await cosplayStore.CreateCosplay(1);
    cosplayStore.component = 'first';
}

const returnPlant = async () => {
    router.push('/career');
    await cosplayStore.CreateCosplay(1);
}

</script>

<template>
    <div class="report">
        <div class="report-box">
            <div class="tubiao">
                <i class="iconfont icon-jiangbei"></i>
            </div>
            <h2>职业体验完成！</h2>
            <p>恭喜你完成了软件工程师的职业体验</p>
            <div class="text-report">
                <h3>你的能力评估</h3>
                <div class="solider">
                    <div class="solid" v-for="i in cosplayStore.cosplaySession?.state?.abilities">
                        <p><span>{{ i.name }}</span><span class="number">{{  cosplayStore.cosplaySession?.state?.scores[i.code] <= 50 ? '一般' : '优秀' }}</span></p>
                        <div class="progress"><div class="bgc" :style="{width: cosplayStore.cosplaySession?.state?.scores[i.code] + '%'}"></div></div>
                    </div>
                </div>
                <div class="border"></div>
                <h4>职业发展建议</h4>
                <p>{{ cosplayStore.finalReport?.advice }}</p>
            </div>
            <div class="button">
                <div class="again anniu" @click="again()">
                    再次体验
                </div>
                <div class="return anniu" @click="returnPlant()">
                    返回星球
                </div>
            </div>
        </div>
    </div>
</template>

<style lang="scss">
    .report{
        padding: 32px 16px;
        height: 923px;
        // background-color: pink;
        .report-box{
            margin: 0 auto;
            padding: 32px;
            width: 45%;
            height: 827px;
            // background-color: pink;
            background-image: linear-gradient(to bottom  right,rgb(147 51 234 / 0.2) , rgb(37 99 235 / 0.2));
            border-radius: 24px;
            border: 1px solid #a855f74d;
            .tubiao{
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 0 auto;
                width: 80px;
                height: 80px;
                border-radius: 999px;
                background-image: linear-gradient(to right,#a855f7 , #3b82f6);
                i{
                    font-size: 35px;
                }
            }
            h2{
                margin-top: 25px;
                text-align: center;
                font-size: 24px;
                line-height: 32px;
            }
            p{
                margin-top: 8px;
                text-align: center;
                font-size: 16px;
                color: #cbd5e1;
            }
            .text-report{
                margin-top: 26px;
                padding: 24px;
                height: 490px;
                border-radius: 12px;
                background: #0f172ab3;
                h3{
                    text-align: center;
                    font-size: 20px;
                }
                .solider{
                    display: flex;
                    flex-direction: column;
                    // gap: 20px;
                    justify-content: space-between;
                    margin-top: 15px;
                    height: 272px;
                    // background-color: pink;
                    .solid{
                        height: 36px;
                        p{
                            margin-top: 0px;
                            display: flex;
                            justify-content: space-between;
                            color: #cbd5e1;
                            font-size: 16px;
                            font-weight: 500;
                            span{
                                font-size: 14px;
                                color: #cbd5e1;
                            }
                            .number{
                                color: #ffffff;
                                font-size: 14px;
                                font-weight: 500;
                            }
                        }
                        .progress{
                            margin-top: 2px;
                            height: 8px;
                            border-radius: 999px;
                            background-color: #33415580;
                            .bgc{
                                width: 100%;
                                height: 100%;
                                border-radius: 999px;
                                background-image: linear-gradient(to right,#a855f7 , #3b82f6);
                            }
                        }
                    }
                }
                .border{
                    height: 25px;
                    border-bottom: 1px solid #334155;
                }
                h4{
                    margin-top: 30px;
                    font-size: 16px;
                }
                p{
                    text-align: start;
                    font-size: 14px;
                    color: #cbd5e1;
                }
            }
            .button{
                display: flex;
                justify-content: center;
                gap: 15px;
                height: 48px;
                margin-top: 30px;
                .anniu{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 12px 24px;
                    font-size: 16px;
                    background-color: #1e293b;
                    cursor: pointer;
                    border-radius: 12px;
                }
                .again:hover{
                    background-color: #334155;
                }
                .return{
                    background-image: linear-gradient(to right,#9333ea , #2563eb);
                    &:hover{
                        background-image: linear-gradient(to right,#7e22ce , #1d4ed8);
                    }
                }
            }
        }
    }
</style>