<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts/core';
onMounted(() => {
  // 初始化图表容器
  const myChart = echarts.init(document.getElementById('salaryChart'));

  // 配置图表数据+样式
  const option = {
    tooltip: {
      // 自定义提示框内容（对应“初级 薪资:12000元/月”的样式）
      formatter: function (params) {
        return `${params.name}<br/>薪资: ${params.value}元/月`;
      }
    },
    // 坐标轴配置
    xAxis: {
      type: 'category',
      data: ['初级', '中级', '高级'],
      axisLabel: { color: '#fff' }, // 坐标轴文字颜色
      axisLine: { lineStyle : { color: '#fff' } }, // y坐标轴文字颜色
    },
    yAxis: {
      show: true,
      type: 'value',
      name: '薪资水平',
      nameTextStyle: { color: '#fff' },
      axisLine: { lineStyle : { color: '#111' } }, // y坐标轴文字颜色
      axisLabel: {
        color: '#fff',
        formatter: '{value}w' // 坐标轴数值显示为“w（万）”
      },
    splitLine: { show: false }
    },
    // 柱状图数据+样式
    series: [
      {
        type: 'bar',
        data: [12000, 25000, 45000], // 对应初/中/高薪资（单位：元）
        itemStyle: {
          color: function(params) {
            // 自定义柱状图颜色（比如渐变/纯色）
            const colorList = [
              new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset:0,color:'#9370DB'},{offset:1,color:'#483D8B'}]),
              new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset:0,color:'#9370DB'},{offset:1,color:'#483D8B'}]),
              new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset:0,color:'#9370DB'},{offset:1,color:'#483D8B'}])
            ];
            return colorList[params.dataIndex];
          }
        },
        // 柱状图高度/宽度配置
        barWidth: 140
      }
    ],
    // 背景样式（对应图中的深色背景）
    // backgroundColor: '#1e293b80'
  };

  // 渲染图表
  myChart.setOption(option);

  // 监听窗口 resize，自适应图表
  window.addEventListener('resize', () => {
    myChart.resize();
  });
});



</script>
<template>
    <div class="salery">
        <div class="left third">
            <h3>薪资水平</h3>
            <div class="salary-chart" id="salaryChart"></div>
            <p>软件工程师不同级别薪资范围（一线城市）</p>
        </div>
        <div class="right third">
            <h3>热门城市分布</h3>
            <div class="solider">
                <div class="solid">
                    <p><span>北京</span><span class="number">1200 个岗位</span></p>
                    <div class="progress"><div class="bgc"></div></div>
                </div>
                <div class="solid">
                    <p><span>上海</span><span class="number">1050 个岗位</span></p>
                    <div class="progress"><div class="bgc" style="width: 80%"></div></div>
                </div>
                <div class="solid">
                    <p><span>广州</span><span class="number">800 个岗位</span></p>
                    <div class="progress"><div class="bgc" style="width: 60%"></div></div>
                </div>
                <div class="solid">
                    <p><span>深圳</span><span class="number">950 个岗位</span></p>
                    <div class="progress"><div class="bgc"style="width: 70%"></div></div>
                </div>
                <div class="solid">
                    <p><span>杭州</span><span class="number">700 个岗位</span></p>
                    <div class="progress"><div class="bgc"style="width: 55%"></div></div>
                </div>
                <div class="solid">
                    <p><span>成都</span><span class="number">650 个岗位</span></p>
                    <div class="progress"><div class="bgc" style="width: 48%"></div></div>
                </div>
            </div>
            <div class="border"></div>
            <h4>薪资影响因素</h4>
            <div class="infactor">
                <span><i class="iconfont icon-qiyeguanli-qiyeleixing" style="color: #60a5fa;"></i> 企业类型</span>
                <span><i class="iconfont icon-weizhi" style="color: #f87171;"></i> 城市级别</span>
                <span><i class="iconfont icon-edu-line" style="color: #4ade80;"></i> 学历背景</span>
                <span><i class="iconfont icon-gongzuojingyan" style="color: #facc15;"></i> 工作经验</span>
            </div>
        </div>
    </div>
</template>
<style lang="scss">
    .salery {
        margin-top: 24px;
        display: flex;
        justify-content: space-between;
        height: 529px;
        .third{
            padding: 24px;
            width: 49%;
            background-color: #1e293b80;
            border-radius: 12px;
             h3{
                margin-bottom: 24px;
                font-size: 20px;
                font-weight: 600;
            }
            .salary-chart{
                width: 100%;
                height: 320px;
                // background-color: pink;
            }
             p{
                margin-top: 20px;
                text-align: center;
                font-size: 14px;
                color: #94a3b8;
            }
            .solider{
                display: flex;
                flex-direction: column;
                // gap: 20px;
                justify-content: space-between;
                height: 296px;
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
                        .number{
                            color: #ffffff;
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
                margin-top: 24px;
                margin-bottom: 12px;
                font-size: 16px;
            }
            .infactor{
                display: flex;
                flex-wrap: wrap;
                span{
                    margin: 2px 0;
                    display: flex;
                    align-items: center;
                    width: 50%;
                    font-size: 14px;
                    color: #cbd5e1;
                    .iconfont{
                        margin-right: 5px;
                        font-size: 16px;
                    }
                }
            }
        }
    }
</style>