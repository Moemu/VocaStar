<script setup>
import { ref, onMounted } from 'vue'

// 引入Echarts
import * as echarts from 'echarts'

const chartRef = ref(null);

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
    <div class="requiry">
        <div class="left capality">
            <h3>核心能力雷达图</h3>
            <div class="ladar" ref="chartRef">
                <!-- 雷达区域 -->
            </div>
            <p>软件工程师所需的各项核心能力分布</p>
        </div>
        <div class="right capality">
            <div class="advice">
                <h3>能力培养建议</h3>
                <li>
                    <div class="tubiao3"><i class="iconfont icon-qianduankaifa"></i></div>
                    <div class="text">
                        <h4>专业能力</h4>
                        <p>系统学习数据结构与算法，深入掌握至少一种编程语言和框架</p>
                    </div>
                </li>
                 <li>
                    <div class="tubiao3" :style="{ backgroundColor: '#2563eb33' }"><i class="iconfont icon-goutong" style="color: #2563eb;"></i></div>
                    <div class="text">
                        <h4>沟通能力</h4>
                        <p>练习清晰表达复杂技术概念，参与团队讨论和技术分享</p>
                    </div>
                </li>
                 <li>
                    <div class="tubiao3" :style="{ backgroundColor: '#16a34a33'}"><i class="iconfont icon-dengpao1" style="color: #4ade80;"></i></div>
                    <div class="text">
                        <h4>解决问题</h4>
                        <p>通过实际项目积累经验，学习调试技巧和问题分析方法</p>
                    </div>
                </li>
            </div>
            <div class="quiz">
                <h3>开始能力测评</h3>
                <p>完成我们的能力测评，了解自己在各项核心能力上的表现，获取个性化提升建议。</p>
                <div class="button">
                    立即测评 <i class="iconfont icon-youjiantou"></i>
                </div>
            </div>
        </div>

    </div>
</template>
<style lang="scss">
    .requiry {
        display: flex;
        justify-content: space-between;
        margin-top: 24px;
        height: 456px;
        // background-color: pink;
        .capality {
            padding: 24px;
            width: 49%;
            height: 100%;
            border-radius: 12px;
            h3{
                font-size: 20px;
                font-weight: 600;
            }
            .ladar{
                width: 100%;
                height: 320px;
                margin-top: 20px;
            }
            p{
                margin-top: 20px;
                text-align: center;
                font-size: 14px;
                color: #94a3b8;
            }
        }
        .left{
             background-color: #1e293b80;
        }
        .right {
            padding: 0;
            background-color: none;
            .advice{
                padding: 24px;
                height: 248px;
                background-color: #1e293b80;
                border-radius: 12px;
                h3{
                    margin-bottom: 10px;
                }
                li{
                    margin-bottom: 5px;
                    display: flex;
                    .tubiao3{
                        margin-right: 8px;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        padding: 8px;
                        border-radius: 8px;
                        background-color: #9333ea33;
                        .iconfont{
                            font-size: 18px;
                            color: #c084fc;
                        }
                    }
                    h4{
                        font-size: 17px;
                    }
                    p{
                        margin-top: 0px;
                        font-size: 14px;
                        color: #94a3b8;
                        line-height: 28px;
                    }
                }
            }
            .quiz{
                margin-top: 24px;
                padding: 24px;
                height: 174px;
                border-radius: 12px;
                background-image: linear-gradient(to right,rgb(30 41 59 / 0.5) , rgb(88 28 135 / 0.3));
                border: 1px solid #581c874d;
                 p{
                    text-align: start;
                    margin: 16px 0;
                    font-size: 16px;
                    color: #cbd5e1;
                }
                .button{
                    width: 120px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 8px 16px;
                    color: #0f172a;
                    font-weight: 500;
                    border-radius: 8px;
                    background-color: #fff;
                    .iconfont{
                        margin-left: 4px;
                        color: #0f172a;
                    }
                    &:hover{
                        cursor: pointer;
                    }
                }
            }
        }
    }
</style>