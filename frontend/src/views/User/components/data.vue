<script setup>
import { ref, onMounted } from 'vue'

// 引入Echarts
import * as echarts from 'echarts'

const chartRef = ref(null);
const discoverData = ref([
    { iconfont: 'iconfont icon-qianduankaifa',iconfontColor: '#4f46e5', bgc: '#4f46e530', title: '软件工程师', company: '技术星云', time: '今天', progress: 100, },
    { iconfont: 'iconfont icon-chart',iconfontColor: '#ec4899', bgc: '#ec489930', title: '市场营销', company: '商业星云', time: '昨天', progress: 60, },
    { iconfont: 'iconfont icon-jurassic_data',iconfontColor: '#10b981', bgc: '#10b98130', title: '数据分析师', company: '技术星云', time: '3天前', progress: 20, },
    { iconfont: 'iconfont icon-zhengfangti',iconfontColor: '#f59e0b', bgc: '#f59e0b30', title: '产品经理', company: '商业星云', time: '未开始', progress: 0, },
])

onMounted(() => {
    // 初始化图表实例
    const myChart = echarts.init(chartRef.value);
     // 提前定义雷达图维度（避免上下文依赖）
    //配置雷达图
    const option = {
        radar: {
            center: ['50%', '50%'],
            radius: '78%',
            indicator: [
                { name: '专业能力', max : 100},
                { name: '沟通能力', max: 100 },
                { name: '解决问题', max: 100 },
                { name: '团队协作', max: 100 },
                { name: '学习能力', max: 100 },
                { name: '抗压能力', max: 100 }
            ],
            name: {
                textStyle: {
                    color: '#94a3b8',
                    fontSize: 15,
                }
            }
        },
        series: [
            {
                type: 'radar',
                data: [
                    {
                        value: [85, 80, 90, 88, 92, 83] ,
                        name: '个人能力'
                    }
                ],
                lineStyle:{
                    color: '#8b5cf6',
                },
                itemStyle:{
                    color: '#8b5cf6',
                },
                areaStyle:{
                    color: '#8b5cf6'
                }
            }
        ],
    }
    // 渲染图表
    myChart.setOption(option);
})

</script>

<template>
    <div class="data-container">
        <div class="capality">
            <li>
                <div class="first">专业能力 <i class="iconfont icon-qianduankaifa"></i></div>
                <div class="second">65 <span>+5%<i class="iconfont icon-jiantou_liebiaoshouqi"></i></span></div>
            </li>
            <li>
                <div class="first">沟通能力<i class="iconfont icon-xiaoxi"></i></div>
                <div class="second">70<span>+3%<i class="iconfont icon-jiantou_liebiaoshouqi"></i></span></div>
            </li>
            <li>
                <div class="first">学习能力 <i class="iconfont icon-xuexi_nor"></i></div>
                <div class="second">80<span>+8%<i class="iconfont icon-jiantou_liebiaoshouqi"></i></span></div>
            </li>
            <li>
                <div class="first">团队协作 <i class="iconfont icon-sangeren"></i></div>
                <div class="second">75<span>+2%<i class="iconfont icon-jiantou_liebiaoshouqi"></i></span></div>
            </li>
        </div>
        <div class="model">
            <h3>我的能力模型</h3>
            <div class="chart" ref="chartRef">
            </div>
            <div class="button">
                查看详细能力报告
            </div>
        </div>
        <div class="middle-box">
            <div class="discover together">
                <div class="title">
                    <h3>探索足迹</h3>
                    <div class="button">
                        查看全部<i class="iconfont icon-youjiantou"></i>
                    </div>
                </div>
                <div class="loading">
                    <li v-for="i in discoverData">
                        <div class="first">
                            <div class="left">
                                <div class="tubiao">
                                    <i :class="i.iconfont" :style="{color: i.iconfontColor, backgroundColor: i.bgc}"></i>
                                </div>
                                <div class="text">
                                    <h4>{{i.title}}</h4>
                                    <p>{{i.company}}</p>
                                </div>
                            </div>
                            <div class="right">
                                <p>{{ i.time }}</p>
                                <span v-if="i.progress === 100">已完成</span>
                            </div>
                        </div>
                        <div class="second">
                            <p>完成进度 <span>{{i.progress}}%</span></p>
                            <div class="progress">
                                <div class="bgc" :style="{width: i.progress+'%'}"></div>
                            </div>
                        </div>
                    </li>
                </div>
            </div>
            <div class="system together">
                <div class="title">
                    <h3>成就系统</h3>
                    <div class="button">
                        查看全部<i class="iconfont icon-youjiantou"></i>
                    </div>
                </div>
                <div class="neiron">
                    <li>
                        <i class="iconfont icon-diqiu"></i>
                        <h4>初次探索</h4>
                        <p>完成第一个职业星球的探索</p>
                        <span>获得于 2025-09-15</span>
                    </li>
                                        <li>
                        <i class="iconfont icon-shoucang" style="color: #f59e0b;"></i>
                        <h4>职业新秀</h4>
                        <p>完成3次职业体验</p>
                        <span>获得于 2025-09-22</span>
                    </li>
                                        <li style="background-color: #3341554d;">
                        <i class="iconfont icon-gantanhaozhong" style="color: #64748b;"></i>
                        <h4>学习达人</h4>
                        <p>连续打卡7天</p>
                        <!-- <span>获得于 2025-09-15</span> -->
                    </li>
                                        <li style="background-color: #3341554d;">
                        <i class="iconfont icon-gantanhaozhong" style="color: #64748b;"></i>
                        <h4>社交之星</h4>
                        <p>绑定3个职业伙伴</p>
                        <!-- <span>获得于 2025-09-15</span> -->
                    </li>
                </div>
            </div>
        </div>
    </div>

</template>

<style lang="scss">
    .data-container {
        width: 100%;
        .capality{
            margin-top: 25px;
            display: flex;
            justify-content: space-between;
            width: 100%;
            height: 106px;
            // background-color: pink;
            li{
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                padding: 16px;
                width: 24%;
                height: 100%;
                background-color: #1e293b80;
                border: 1px solid #33415580;
                border-radius: 12px;
                .first{
                    display: flex;
                    justify-content: space-between;
                    font-size: 14px;
                    color: #cbd5e1;
                    font-weight: 500;
                    .iconfont{
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        width: 32px;
                        height: 32px;
                        color: #4ade80;
                        border-radius: 999px;
                        background-color: #16a34a33;
                    }
                }
                .second{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    font-size: 22px;
                    font-weight: 700;
                    color: #fff;
                    span{
                        font-size: 14px;
                        color: #4ade80;
                        .iconfont{
                            color: #4ade80;
                            font-size: 18px;
                        }
                    }
                }
            }
        }
        .model{
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 24px;
            margin-top: 33px;
            height: 472px;
            background-color: #1e293b80;
            border-radius: 12px;
            h3{
                font-size: 20px;
                font-weight: 600;
            }
            .chart{
                margin: 30px auto 0;
                width: 350px;
                height: 300px;
            }
            .button{
                margin-top: 30px;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 8px;
                background-color: #9333ea;
                &:hover{
                    cursor: pointer;
                    background-color: #7e22ce;
                }
            }
        }
        .middle-box{
            display: flex;
            justify-content: space-between;
            margin-top: 35px;
            height: 629px;
            // background-color: pink;
            .together{
                padding: 24px;
                width: 49%;
                height: 100%;
                background-color: #1e293b4d;
                border-radius: 16px;
                border: 1px solid #334155;
                .title{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    h3{
                        font-size: 20px;
                        font-weight: 700;
                    }
                    .button{
                        font-size: 14px;
                        color: #c084fc;
                        i{
                            margin-left: 8px;
                            color: #c084fc;
                        }
                        &:hover{
                            cursor: pointer;
                            color: #d8b4fe;
                            i{
                                color: #d8b4fe;
                            }
                        }
                    }
                }
                .neiron{
                    margin-top: 25px;
                    padding-bottom: 25px;
                    display: flex;
                    flex-wrap: wrap;
                    gap: 13px;
                    border-bottom: 1px solid #33415580;
                    li{
                        padding: 16px;
                        text-align: center;
                        width:49%;
                        height: 186px;
                        background-color: #1e293b80;
                        border-radius: 12px;
                        border: 1px solid #33415580;
                        i{
                            margin: 0 auto 10px;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            width: 60px;
                            height: 60px;
                            color: #4f46e5;
                            font-size: 25px;
                            font-weight: 900;
                            border-radius: 50%;
                            background-image: linear-gradient(to bottom,#0f172a , #020617);
                        }
                        h4{
                            font-size: 16px;
                            font-weight: 500;
                        }
                        p{
                            margin-top: 5px;
                            margin-bottom: 16px;
                            color: #94a3b8;
                            font-size: 12px;
                            line-height: 16px;
                        }
                        span{
                            color: #64748b;
                            font-size: 12px;
                        }
                    }
                }
                .loading{
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    margin-top: 25px;
                    height: 527px;
                    // background-color: pink;
                    li{
                        transition: all 0.3s ease-in-out;
                        padding: 16px;
                        height: 23%;
                        background-color: #1e293b80;
                        border-radius: 12px;
                        border: 1px solid #33415580;
                        &:hover{
                            border: 1px solid #47556980;
                            transform: translateY(-4px);
                        }
                        .first{
                            display: flex;
                            justify-content: space-between;
                            .left{
                                display: flex;
                                .iconfont{
                                    margin-right: 13px;
                                    display: flex;
                                    justify-content: center;
                                    align-items: center;
                                    width: 40px;
                                    height: 40px;
                                    color: #4f46e5;
                                    font-size: 18px;
                                    background-color: #4f46e530;
                                    border-radius: 999px;
                                }
                                .text{
                                    h4{
                                        font-size: 17px;
                                        line-height: 28px;
                                    }
                                    p{
                                        font-size: 12px;
                                        color: #94a3b8;
                                    }
                                }
                            }
                            .right{
                                p{
                                    margin-bottom: 5px;
                                    text-align: end;
                                    font-size: 12px;
                                    color: #64748b;
                                }
                                span{
                                    display: flex;
                                    padding: 2px 8px;
                                    color: #4ade80;
                                    font-size: 12px;
                                    background-color: #16a34a33;
                                    border-radius: 999px;
                                }
                            }
                        }
                        .second{
                            margin-top: 16px;
                            p{
                                display: flex;
                                justify-content: space-between;
                                font-size: 12px;
                                color: #94a3b8;
                            }
                            .progress{
                                margin-top: 4px;
                                height: 6px;
                                width: 100%;
                                border-radius: 999px;
                                background-color: #33415580;
                                .bgc{
                                    height: 100%;
                                    // background-color: pink;
                                    background-image: linear-gradient(to right,#a855f7 , #3b82f6);
                                    border-radius: 100px;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
</style>