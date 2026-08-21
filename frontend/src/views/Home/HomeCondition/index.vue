<script setup>
import { ref, onMounted } from 'vue'
// 引入Echarts
import * as echarts from 'echarts'

const chartRef = ref(null);

onMounted(() => {
    // 初始化图表实例
    const myChart = echarts.init(chartRef.value);
    //配置雷达图
    const option = {
        // 背景颜色
        // backgroundColor: '#c084fc',

        radar: {
            indicator: [
                { name: '专业能力', max : 100},
                { name: '沟通能力', max: 100 },
                { name: '解决问题', max: 100 },
                { name: '团队协作', max: 100 },
                { name: '学习能力', max: 100 },
                { name: '抗压能力', max: 100 }
            ],
            label: {
                color: '#94a3b8 !important' ,
                fontSize: 15,
            }
        },
        series: [
            {
                type: 'radar',
                // 雷达图填充色（第二张的紫色渐变风格）
                areaStyle: {
                color: {
                    type: 'linear',
                    x: 0,
                    y: 0,
                    x2: 0,
                    y2: 1,
                    colorStops: [
                    { offset: 0, color: '#c084fc' },
                    { offset: 1, color: '#c084fc' }
                    ]
                }
                },
                // 雷达图边框样式（蓝色线条）
                itemStyle: {
                color: '#6A5ACD'
                },

                data: [
                    {
                        value: [85, 80, 90, 88, 92, 83] ,
                        name: '个人能力'
                    }
                ]
            }
        ]
    }
    // 渲染图表
    myChart.setOption(option);
})


</script>

<template>
    <div class="condition">
        <div class="top">
            <div class="text">
                <h1>欢迎回来，Moemu！</h1>
                <p>今天也是探索职业星系的一天 ✨</p>
            </div>
            <div class="button">
                <div class="first">
                    <RouterLink>
                        <i class="iconfont icon-rili"></i>日程安排
                    </RouterLink>
                </div>
                <div class="first">
                    <RouterLink>
                        <i class="iconfont icon-jiangbei"></i>成就
                    </RouterLink>
                </div>
            </div>
        </div>
        <div class="bottom">
            <li class="box">
                <div class="text">
                    <div class="left">
                        <h4>探索进度</h4>
                        <span>5</span>/50
                    </div>
                    <div class="right">
                        <i class="iconfont icon-huojian"></i>
                    </div>
                </div>
                <div class="bar">
                    <div class="bgc"></div>
                </div>
                <p>已解锁5个职业星球，加油探索更多！</p>
            </li>
            <li class="box">
                <div class="text">
                    <div class="left">
                        <h4>能力值雷达图</h4>
                        <span>综合评分：82</span>
                    </div>
                    <div class="right second">
                        <i class="iconfont second"></i>
                    </div>
                </div>
                <div class="echarts-container" ref="chartRef">

                </div>
            </li>
            <li class="box">
                <div class="text">
                    <div class="left">
                        <h4>今日积分</h4>
                        <span>50</span>积分
                    </div>
                    <div class="right third">
                        <i class="iconfont icon-shoucang"></i>
                    </div>
                </div>
                <div class="middle">
                    <div class="day">
                        每日签到
                        <span>已完成</span>
                    </div>
                    <div class="day">
                        职业测评
                        <span class="noDone">未完成</span>
                    </div>
                </div>
                <p>再获得50积分，可解锁新徽章 🎯</p>
            </li>
        </div>
    </div>
</template>

<style lang="scss">
    .condition {
        padding: 96px 16px 32px;
        width: 100%;
        height: 490px;
        // background-color: pink;
        .top{
            display: flex;
            justify-content: space-between;
            align-items: center;
            .text{
                h1{
                    padding: 0;
                }
                p{
                    color: #94a3b8;
                    font-size: 16px;
                }
            }
            .button{
                display: flex;
                justify-content: space-between;
                align-items: center;
                width: 212px;
                height: 36px;
                .first{
                    padding: 8px 16px;
                    background-color: #1e293b;
                    font-size: 14px;
                    border-radius: 8px;
                    &:hover{
                        background-color: #334155;
                    }
                    a{
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        color: #fff;
                        i{
                            font-size: 20px;
                            margin-right: 6px;
                        }
                    }
                }
            }
        }
        .bottom{
            display: flex;
            justify-content: space-between;
            margin-top: 35px;
            width: 100%;
            height: 238px;
            // background-color: pink;
            li{
                padding: 20px;
                width: 32.6%;
                height: 100%;
                border-radius: 12px;
                border: 1px solid #33415580;
                background-color: #1e293b80;
            }
            .box{
                .text{
                    display: flex;
                    justify-content: space-between;
                   .left{
                        font-size: 18px;
                        line-height: 28px;
                        color: #94a3b8;
                        h4{
                            margin-bottom: 7px;
                            font-size: 14px;
                            color: #94a3b8;
                            line-height: 20px;
                        }
                        span{
                            font-size: 22px;
                            font-weight: 700;
                        }
                   }
                   .right{
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        width: 40px;
                        height: 40px;
                        background-color: #9333ea33;
                        border-radius: 999px;
                        i{
                            color: #c084fc;
                            font-weight: 900;
                            font-size: 18px;
                        }
                   }
                   .second{
                            background-color: #2563eb33;
                    }
                    .third{
                        background-color: #d9770633;
                        .iconfont{
                            color: #fbbf24;
                        }
                    }
                }
                .bar{
                    margin-top: 18px;
                    height: 8px;
                    width: 100%;
                    border-radius: 999px;
                    background-color: #33415580;
                    .bgc{
                        width: 5/50*100%;
                        height: 100%;
                        background-image: linear-gradient(to right, #a855f7 , #3b82f6);
                        border-radius: 999px;
                    }
                }
                p{
                    margin-top: 8px;
                    font-size: 12px;
                    color: #64748b;
                }
                .echarts-container{
                    margin: 0 auto;
                    width: 200px;
                    height: 160px;
                }
                .middle{
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    margin-top: 16px;
                    padding: 12px;
                    width: 100%;
                    height: 72px;
                    background-color: #3341554d;
                    border-radius: 8px;
                    .day{
                        display: flex;
                        justify-content: space-between;
                        font-size: 14px;
                        span{
                            display: flex;
                            padding: 2px 8px;
                            color: #4ade80;
                            font-size: 12px;
                            background-color: #16a34a33;
                            border-radius: 999px;
                        }
                        .noDone{
                            color: #94a3b8;
                            background-color: #47556933;
                        }
                    }
                }
            }
        }
    }
</style>