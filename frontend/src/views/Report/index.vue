<script setup>
import { ref, onMounted } from 'vue'
import { useQuizStore } from '../../stores/quiz';
import { ElMessage } from 'element-plus';
import { getReportAPI } from '../../apis/quiz'
// 引入Echarts
import * as echarts from 'echarts'

const chartRef = ref(null);
const quizStore = useQuizStore();
const reportList = ref({});

const report = quizStore.report?.report;
console.log(report);
const holland_code = report?.holland_code;
const dimension = report?.dimension_scores;
const dimensionData = Object.values(dimension);
const recommendation = ref(report?.recommendations);

console.log(dimensionData);

console.log('这是:',quizStore.report);
ElMessage({type:'success', message: '恭喜你获得'+ report?.reward_points + '积分！'})
ElMessage({type: 'success',message: '恭喜完成了测评内容'});
ElMessage({type: 'info', message: '报告生成中，请稍后'});

let retryCount = 0;
const maxRetry = 12;
const retryInterval = 3000;
const getReport = async() => {
    const res = await getReportAPI();
    reportList.value = res.data;
    console.log(reportList.value);
    if(reportList.value?.report?.holland_report){
        ElMessage({type: 'success', message: '报告已完整生成'});
        return;
    }
        if(retryCount < maxRetry){
            retryCount++;
            setTimeout(getReport, retryInterval);
        }else{
            ElMessage({type: 'error', message: '报告超时，请稍后再试'});
         }

}


onMounted(() => {
    getReport();

    // 初始化图表实例
    const myChart = echarts.init(chartRef.value);
     // 提前定义雷达图维度（避免上下文依赖）
    const radarIndicators = [
        { name: '艺术型(A)', max: 100 },
        { name: '常规型(C)', max: 100 },
        { name: '企业型(E)', max: 100 },
        { name: '研究型(I)', max: 100 },
        { name: '现实型(R)', max: 100 },
        { name: '社会型(S)', max: 100 },
    ];
    //配置雷达图
    const option = {
        radar: {
            center: ['50%', '50%'],
            radius: '64%',
            indicator: radarIndicators,
            name: {
                textStyle: {
                    color: '#d1d5db',
                    fontSize: 12,
                }
            }
        },
        series: [
            {
                type: 'radar',
                data: [
                    {
                        value: dimensionData,
                        name: '研究型(I),社会型(S),企业型(E),艺术型(A),常规型(C),现实型(R)',
                        // name: ['研究型(I)','社会型(S)','企业型(E)','艺术型(A)','常规型(C)','现实型(R)']
                    }
                ],
                lineStyle:{
                    color: '#00e396',
                },
                itemStyle:{
                    color: '#00e396',
                },
                areaStyle:{
                    color: '#00e396'
                }
            }
        ],
        tooltip: {
                trigger: 'item',
                formatter: function(params) {
                // params.dataIndex 是当前维度在 indicator 中的索引
                return `${params.name}` + '<br/>兴趣指数' + `${params.value}`;
            }
        },
    }
    // 渲染图表
    myChart.setOption(option);
})



</script>

<template>
    <div class="report-container">
        <div class="top">
             <h1>个性化职业发展报告</h1>
             <p>基于您的霍兰德测评与个人背景</p>
             <div class="word">
                <li class="first">
                    {{ holland_code[0] }}
                </li>
                <li class="second">
                    {{ holland_code[1] }}
                </li>
                <li class="third">
                    {{ holland_code[2] }}
                </li>
             </div>
             <div class="point">
                研究型<span>({{dimensionData[3]}}分)</span> / 社会型<span>({{dimensionData[5]}}分)</span> / 企业型<span>({{dimensionData[2]}}分)</span>
             </div>
        </div>
        <div class="quiz-report">
            <div class="box">
                <p>霍兰德兴趣测评结果</p>
                <div class="chart" ref="chartRef">
                </div>
                <div class="bottom">
                    <span></span>兴趣指数
                </div>
            </div>
        </div>
        <div class="advantage">
            <div class="box">
                <h2>🎯 你的独特优势</h2>
                <div class="text">
                    <p>{{ report?.unique_advantage }}</p>
                </div>
            </div>
        </div>
        <div class="direction">
            <h2>💡 为你量身打造的职业方向</h2>
            <p>基于你的优势，我强烈推荐你关注那些需要同时运用技术能力和人际技能的"桥梁型"角色：</p>
            <div class="first">
                <h3>方向一: {{ reportList?.report?.holland_report?.career_directions?.[0]?.career}}</h3>
                <div class="text">
                    <div class="title">
                        描述：
                    </div>
                    <p>{{ reportList?.report?.holland_report?.career_directions?.[0]?.description}}</p>
                    <div class="title-second">
                        立即可以做的事：
                    </div>
                    <li v-for='i in reportList?.report?.holland_report?.career_directions?.[0]?.recommended_action'>{{ i }}</li>
                </div>
            </div>
            <div class="first second">
                <h3>方向二：{{ reportList?.report?.holland_report?.career_directions?.[1]?.career }}</h3>
                <div class="text">
                    <div class="title">
                        描述：
                    </div>
                    <p>{{ reportList?.report?.holland_report?.career_directions?.[1]?.description }}</p>
                    <div class="title-second">
                        立即可以做的事：
                    </div>
                   <li v-for='i in reportList?.report?.holland_report?.career_directions?.[1]?.recommended_action'>{{ i }}</li>
                </div>
            </div>
        </div>
        <div class="recommend1">
            <div class="box">
                <h2>🔍 推荐岗位匹配：{{holland_code}}特质的其他职业选择</h2>
                <ul>
                    <li>
                        <div class="tubiao">
                            <i class="iconfont icon-lianxixiangmujingli"></i>
                        </div>
                        <h3>{{ reportList?.report?.recommendations?.[0]?.name }}</h3>
                        <p>{{ reportList?.report?.recommendations?.[0]?.description }}</p>
                        <div class="button">
                            立即探索<i class="iconfont icon-youjiantou"></i>
                        </div>
                    </li>
                    <li class="second">
                        <div class="tubiao">
                            <i class="iconfont icon-sangeren"></i>
                        </div>
                        <h3>{{ reportList?.report?.recommendations?.[1]?.name }}</h3>
                        <p>{{ reportList?.report?.recommendations?.[1]?.description }}</p>
                        <div class="button">
                            立即探索<i class="iconfont icon-youjiantou"></i>
                        </div>
                    </li>
                    <li class="third">
                        <div class="tubiao">
                            <i class="iconfont icon-xiangmujingli"></i>
                        </div>
                        <h3>{{ reportList?.report?.recommendations?.[2]?.name }}</h3>
                        <p>{{ reportList?.report?.recommendations?.[2]?.description }}</p>
                        <div class="button">
                            立即探索<i class="iconfont icon-youjiantou"></i>
                        </div>
                    </li>
                </ul>
            </div>
        </div>
        <div class="route">
            <h2>🚀 你的行动路线图</h2>
            <p>别担心未来，专注于眼前能抓住的机会。</p>
            <h3>接下来一个月的小目标：</h3>
            <div class="top">
                <div class="left">
                    <div class="tubiao">
                        <i class="iconfont icon-sangeren"></i>
                    </div>
                    <div class="text">
                        <h4>{{ reportList?.report?.holland_report?.action_roadmap?.small_goals?.[0]?.title }}</h4>
                        <p> {{ reportList?.report?.holland_report?.action_roadmap?.small_goals?.[0]?.content }}</p>
                    </div>
                </div>
                <div class="left right">
                    <div class="tubiao">
                        <i class="iconfont icon-sangeren"></i>
                    </div>
                    <div class="text">
                        <h4>{{ reportList?.report?.holland_report?.action_roadmap?.small_goals?.[1]?.title  }}</h4>
                        <p>{{ reportList?.report?.holland_report?.action_roadmap?.small_goals?.[1]?.content  }}</p>
                    </div>
                </div>
            </div>
            <div class="middle">
                <h3>最需要关注的成长点：</h3>
                <p>{{ reportList?.report?.holland_report?.action_roadmap?.need_attention }}</p>
            </div>
            <div class="bottom">
                <p>{{ reportList?.report?.holland_report?.action_roadmap?.conclusion}}</p>
            </div>
        </div>
        <div class="xiamianbutton" @click="$router.push('/career-explore')">
            进入职业星系，开启职业之旅
        </div>
        <div class="footer">
            © 2025 个性化职业发展报告 | 基于霍兰德职业兴趣测评
        </div>
    </div>
</template>

<style lang="scss">
    .report-container {
        width: 100%;
        background-image: linear-gradient(to right, #0f172a , #020617);
        text-align: center;
        .top{
            width: 100%;
            height: 350px;
            h1{
                padding-top: 20px;
                height: 100px;
                font-size: 48px;
                font-weight: 700;
                color: transparent;
                background-image: linear-gradient(to right,#60a5fa , #6366f1 , #9333ea);
                background-clip: text;
            }
            p{
                font-size: 20px;
                line-height: 25px;
                color: #d1d5db;
            }
            .word{
                display: flex;
                justify-content: space-between;
                margin: 35px auto 0;
                height: 80px;
                width: 276px;
                // background-color: pink;
                li{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    width: 80px;
                    height: 80px;
                    font-size: 30px;
                    font-weight: 700;
                    border-radius: 12px;
                    background-color: pink;
                }
                .first{
                    background: linear-gradient(135deg, rgba(79, 70, 229, 0.3) 0%, rgba(67, 56, 202, 0.3) 100%);
                    border: 2px solid #818cf8;
                }
                .second{
                    background: linear-gradient(135deg, rgba(34, 197, 94, 0.3) 0%, rgba(22, 163, 74, 0.3) 100%);
                    border: 2px solid #4ade80;
                }
                .third{
                    background: linear-gradient(135deg, rgba(234, 179, 8, 0.3) 0%, rgba(217, 119, 6, 0.3) 100%);
                    border: 2px solid #facc15;
                }
            }
            .point{
                margin-top: 32px;
                font-size: 16px;
                color: #9ca3af;
                span{
                    font-style: italic;
                    color: #9ca3af;
                }
            }
        }
        .quiz-report{
            height: 386px;
            width: 100%;
            // background-color: pink;
            .box{
                margin: 0 auto;
                padding: 12px;
                width: 57%;
                height: 100%;
                background-color: #ffffff0d;
                border-radius: 12px;
                border: 1px solid #ffffff1a;
                p{
                    font-size: 18px;
                    line-height: 28px;
                    color: #ffffff;
                    font-weight: 600;
                }
                .chart{
                    margin: 30px auto 0;
                    width: 300px;
                    height: 280px;
                    // background-color: pink;
                }
                .bottom{
                    position: relative;
                    margin: 5px auto 0;
                    font-size: 17px;
                    color: #00e396;
                    span{
                        position: absolute;
                        top: 25%;
                        left: 43.5%;
                        display: flex;
                        width: 14px;
                        height: 14px;
                        border-radius: 999px;
                        background-color: #4ade80;
                    }
                }
            }
        }
        .advantage{
            padding: 50px 0 35px;
            width: 100%;
            height: 300px;
            // background-color: pink;
            .box{
                margin: 0 auto;
                padding: 24px;
                width: 57%;
                height: 100%;
                background-color: #ffffff0d;
                border: 1px solid #ffffff1a;
                border-radius: 12px;
                text-align: start;
                &:hover{
                    border-color: #ffffff33;
                }
                h2{
                    font-size: 24px;
                    line-height: 32px;
                }
                .text{
                    margin-top: 18px;
                    height: 112px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    font-size: 16px;
                    color: #e5e7eb;
                }
            }
        }
        .direction{
            margin: 50px auto 0;
            padding: 24px;
            height: 693px;
            width: 57%;
            background-color: #ffffff0d;
            border: 1px solid #ffffff1a;
            border-radius: 12px;
            text-align: start;
            &:hover{
                border-color: #ffffff33;
            }
            h2{
                font-size: 24px;
                line-height: 32px;
            }
            p{
                margin-top: 18px;
                font-size: 16px;
                color: #e5e7eb;
            }
            .first{
                margin-top: 20px;
                height: 278px;
                width: 100%;
                padding: 20px;
                background-image: linear-gradient(to bottom,rgb(30 58 138 / 0.3) , rgb(49 46 129 / 0.3));
                border-radius: 12px;
                border: 1px solid #3b82f64d;
                h3{
                    color: #93c5fd;
                    font-weight: 700;
                    font-size: 20px;
                    line-height: 28px;
                }
                .text{
                    margin-top: 12px;
                    font-weight: 500;
                    font-size: 16px;
                    p{
                        margin-top: 3px;
                        color: #d1d5db;
                        font-size: 16px;
                    }
                    .title-second{
                        margin-top: 14px;
                    }
                    li{
                        margin-top: 8px;
                        margin-left: 24px;
                        color: #d1d5db;
                        font-size: 16px;
                        list-style-type: disc;
                    }
                }
            }
            .second{
                margin-top: 23px;
                height: 254px;
                background-image: linear-gradient(to bottom,rgb(20 83 45 / 0.3) , rgb(19 78 74 / 0.3));
                border: 1px solid #22c55e4d;
                h3{
                    color: #86efac;
                }
            }
        }
        .recommend1{
            padding: 24px 0;
            // height: 428px;
            width: 100%;
            .box{
                margin: 0 auto;
                padding: 24px;
                width: 57%;
                // height: 100%;
                background-color: #ffffff0d;
                border: 1px solid #ffffff1a;
                border-radius: 12px;
                text-align: start;
                &:hover{
                    border-color: #ffffff33;
                }
                h2{
                    font-size: 24px;
                    line-height: 32px;
                }
                ul{
                    display: flex;
                    justify-content: space-between;
                    margin-top: 23px;
                    // height: 274px;
                    // background-color: pink;
                    li{
                        padding: 24px;
                        width: 31%;
                        height: 100%;
                        // background-color: pink;
                        border-radius: 12px;
                        background-image: linear-gradient(to bottom,rgb(30 58 138 / 0.3) , rgb(49 46 129 / 0.3));
                        border: 1px solid #3b82f64d;
                        &:hover{
                            border-color: #60a5fa80;
                            box-shadow: 0 10px 15px -3px rgb(59 130 246 / 0.1), 0 4px 6px -4px rgb(59 130 246 / 0.1);
                        }
                        .tubiao{
                            height: 36px;
                            .iconfont{
                                font-size: 36px;
                                color: #60a5fa;
                            }
                        }
                        h3{
                            margin-top: 20px;
                            font-size: 20px;
                            font-weight: 700;
                            line-height: 28px;
                        }
                        p{
                            margin-top: 10px;
                            font-size: 14px;
                            line-height: 20px;
                            color: #d1d5db;
                        }
                        .button{
                            transition: all 0.8 linear;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            margin-top: 18px;
                            padding: 8px 16px;
                            height: 40px;
                            color: #fff;
                            font-weight: 500;
                            font-size: 16px;
                            background-image: linear-gradient(to right,#3b82f6 , #4f46e5);
                            border-radius: 8px;
                            gap: 8px;
                            &:hover{
                                background-image: linear-gradient(to right,#2563eb , #4338ca);
                                transform: scale(1.04);
                                cursor: pointer;
                            }
                        }
                    }
                    .second{
                        background-image: linear-gradient(to right,rgb(20 83 45 / 0.3) , rgb(19 78 74 / 0.3));
                        border-color: #22c55e4d;
                        &:hover{
                            box-shadow: 0 10px 15px -3px rgb(34 197 94 / 0.1), 0 4px 6px -4px rgb(34 197 94 / 0.1);
                            border-color: #4ade8080;
                        }
                        .tubiao{
                            .iconfont{
                                color: #4ade80;
                            }
                        }
                        .button{
                            background-image: linear-gradient(to right,#22c55e , #0d9488);
                            &:hover{
                                background-image: linear-gradient(to right, #16a34a , #0f766e);
                            }
                        }
                    }
                    .third{
                        background-image: linear-gradient(to right, rgb(88 28 135 / 0.3) , rgb(131 24 67 / 0.3));
                        border-color: #a855f74d;
                        &:hover{
                            box-shadow: 0 10px 15px -3px rgb(168 85 247 / 0.1), 0 4px 6px -4px rgb(168 85 247 / 0.1);
                            border-color: #c084fc80;
                        }
                        .tubiao{
                            .iconfont{
                                color: #c084fc;
                            }
                        }
                        .button{
                            background-image: linear-gradient(to right,#a855f7 , #db2777);
                            &:hover{
                                background-image: linear-gradient(to right, #9333ea , #be185d);
                            }
                        }
                    }
                }
            }
        }
        .route{
            margin: 0 auto;
            padding: 24px;
            height: 587px;
            width: 57%;
            background-color: #ffffff0d;
            border: 1px solid #ffffff1a;
            border-radius: 12px;
            text-align: start;
            &:hover{
                border-color: #ffffff33;
            }
            h2{
                font-size: 24px;
                line-height: 32px;
            }
            p{
                margin-top: 18px;
                font-size: 16px;
                color: #e5e7eb;
            }
            h3{
                margin-top: 25px;
                color: #86efac;
                font-weight: 700;
                font-size: 20px;
                line-height: 28px;
            }
            .top{
                display: flex;
                justify-content: space-between;
                margin-top: 18px;
                height: 121px;
                // background-color: pink;
                .left{
                    display: flex;
                    padding: 16px;
                    width: 49%;
                    height: 100%;
                    background-color: #14532d33;
                    border: 1px solid #22c55e4d;
                    border-radius: 8px;
                    .tubiao{
                        margin-right: 12px;
                        padding: 8px;
                        width: 36px;
                        height: 40px;
                        background-color: #22c55e33;
                        border-radius: 999px;
                        .iconfont{
                            font-weight: 900;
                            font-size: 18px;
                            color: #4ade80;
                        }
                    }
                    h4{
                        font-weight: 700;
                    }
                    p{
                        margin-top: 5px;
                        color: #d1d5db;
                        font-size: 14px;
                        line-height: 20px;
                    }
                }
                .right{
                    background-color: #1e3a8a33;
                    border-color: #3b82f64d;
                    .tubiao{
                        background-color: #3b82f633;
                        .iconfont{
                            color: #60a5fa;
                        }
                    }
                }
            }
            .middle{
                margin-top: 15px;
                padding: 20px;
                height: 154px;
                background-image: linear-gradient(to right, rgb(88 28 135 / 0.4) , rgb(49 46 129 / 0.4));
                border: 1px solid #a855f74d;
                border-radius: 12px;
                h3{
                    margin-top: 0px;
                    color: #d8b4fe;
                    font-weight: 700;
                    font-size: 20px;
                    line-height: 28px;
                }
                p{
                    margin-top: 13px;
                    color: #d1d5db;
                }
            }
            .bottom{
                padding: 20px;
                margin-top: 10px;
                height: 98px;
                border-radius: 12px;
                border: 1px solid #3b82f64d;
                background-image: linear-gradient(to right,rgb(30 58 138 / 0.4) , rgb(88 28 135 / 0.4));
                p{
                    margin-top: 0;
                    font-size: 18px;
                    line-height: 28px;
                    color: #d1d5db;
                }
            }
        }
        .xiamianbutton{
            width: 19%;
            margin-top: 20px;
            // background-color: pink;
            border-radius: 12px;
            padding: 12px 20px;
            margin: 60px auto 0 ;
            font-size: 18px;
            background-image: linear-gradient(to right, #9333ea , #2563eb);
            &:hover{
                background-image: linear-gradient(to right, #7e22ce , #1d4ed8);
                transform: scale(1.04);
                cursor: pointer;
            }
        }

        .footer{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 150px;
            font-size: 14px;
            color: #6b7280;
        }
    }
</style>