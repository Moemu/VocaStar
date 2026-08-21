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
        radar: {
            indicator: [
                { name: '专业能力', max : 100},
                { name: '沟通能力', max: 100 },
                { name: '解决问题', max: 100 },
                { name: '团队协作', max: 100 },
                { name: '学习能力', max: 100 },
                { name: '抗压能力', max: 100 }
            ]
        },
        series: [
            {
                type: 'radar',
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


</template>

<style lang="scss">


</style>