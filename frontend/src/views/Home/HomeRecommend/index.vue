<script setup>
import { ref } from 'vue';
const recommendList = ref([]);
const todayRecommend = ref([]);
recommendList.value = [
    {url:'https://space.coze.cn/api/coze_space/gen_image?image_size=landscape_4_3&prompt=Software%20engineer%20working%20on%20code%20with%20digital%20interface&sign=402e461ee359fbdd33b31d219f9a7719', text:'热门', iconfont:'iconfont icon-qianduankaifa',title:'软件工程师', p: '技术星云 · 适合探索者', desc:'负责设计、开发和维护软件系统，解决复杂技术问题，需要掌握多种编程语言和开发工具。',discovery:'2.4k 人正在探索'},
    {url:'https://space.coze.cn/api/coze_space/gen_image?image_size=landscape_4_3&prompt=Data%20analyst%20working%20with%20charts%20and%20graphs%20on%20computer&sign=8d4365b3f0ed21161e5afe9db5002efc', text:'新上线', iconfont:'iconfont icon-jurassic_data', title:'数据分析师', p:'技术星云 · 适合探索者', desc:'收集、处理和分析数据，提供业务决策支持，需要掌握数据分析方法和工具。', discovery:'1.8k 人正在探索'},
    {url:'https://space.coze.cn/api/coze_space/gen_image?image_size=landscape_4_3&prompt=UI%20designer%20creating%20digital%20interface%20design%20on%20tablet&sign=03f83daae9ee4af10099418f803cfe5d', text:'', iconfont:'iconfont icon-huaban', title:'UI设计师', p:'创意星云 · 适合探索者', desc:'负责设计、制作、优化用户界面，需要掌握多种设计工具和技能。', discovery:'1.2k 人正在探索'}
    ]

todayRecommend.value = [
    { iconfont:'iconfont icon-qianduankaifa',title:'前端开发学习组', p: '245 名成员', desc:'专注于前端技术学习与交流，包括HTML、CSS、JavaScript、React、Vue等技术栈。'},
    { iconfont:'iconfont icon-chart', title:'产品经理实战圈', p:'189 名成员', desc:'探讨产品规划、需求分析、用户体验设计等产品经理必备技能。'},
    { iconfont:'iconfont icon-jurassic_data', title:'数据分析师联盟', p:'156 名成员', desc:'交流数据分析方法、工具使用和数据驱动决策的实践经验。'},
    { iconfont:'iconfont icon-huaban', title:'UI设计师成长营', p:'132 名成员', desc:'分享UI设计心得、设计工具使用技巧和行业设计趋势。'}
    ]
</script>

<template>
    <div class="recommend">
        <div class="top">
            <div class="title">
                <h2>今日推荐</h2>
                <div class="button">
                    换一批<i class="iconfont icon-ziyuan"></i>
                </div>
            </div>
            <ul>
                <li v-for="i in recommendList">
                    <div class="photo">
                        <img :src="i.url" alt="">
                        <div class="text">
                            {{ i.text }}
                        </div>
                        <div class="bgc"></div>
                    </div>
                    <div class="career">
                        <div class="title">
                            <div class="tubiao">
                                <i :class="i.iconfont"></i>
                            </div>
                            <div class="right">
                                <h3>{{ i.title }}</h3>
                                <p>{{ i.p }}</p>
                            </div>
                        </div>
                        <div class="desc">
                            <p>{{ i.desc }}</p>
                        </div>
                        <div class="discover">
                            <div class="number">
                                <i class="iconfont icon-sangeren"></i>{{ i.discovery }}
                            </div>
                            <RouterLink>
                                <div class="going" @click="$router.push('/career')">
                                    探索详情<i class="iconfont icon-youjiantou"></i>
                                </div>
                            </RouterLink>
                        </div>
                    </div>
                </li>
            </ul>
        </div>
        <div class="bottom">
             <div class="title">
                <h2>今日推荐</h2>
                <div class="button">
                    查看全部<i class="iconfont icon-youjiantou"></i>
                </div>
            </div>
            <div class="main">
                <li v-for="i in todayRecommend">
                    <div class="career">
                        <div class="title">
                            <div class="tubiao">
                                <i :class="i.iconfont"></i>
                            </div>
                            <div class="right">
                                <h3>{{ i.title }}</h3>
                                <p>{{ i.p }}</p>
                            </div>
                        </div>
                        <div class="desc">
                            <p>{{ i.desc }}</p>
                        </div>
                        <RouterLink>
                            加入小组
                        </RouterLink>
                    </div>
                </li>
            </div>
        </div>
    </div>
</template>

<style lang="scss">
    .recommend{
        width: 100%;
        height: 790px;
        // background-color: pink;
        .top{
            margin-top: 45px;
            padding: 0 16px;
            height: 434px;
            .title{
                display: flex;
                justify-content: space-between;
                align-items: center;
                h2{
                    font-size: 24px;
                    font-weight: 700;
                }
                .button{
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
            ul{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 22px;
                height: 378px;
                // background-color: #fff;
                li{
                    overflow: hidden;
                    transition: all 0.5s;
                    height: 100%;
                    width: 32%;
                    background-color: #1e293b4d;
                    border-radius: 16px;
                    border: 1px solid #33415580;
                    &:hover{
                        transform: translateY(-5px);
                        box-shadow: 0px 10px 25px -5px #5e17eb33;
                            img{
                                transform: scale(1.1);
                            }
                    }
                    .photo{
                        position: relative;
                        overflow: hidden;
                        height: 192px;
                        img{
                            transition: all 0.3s linear;
                            width: 100%;
                            height: 100%;
                            object-fit: cover;
                        }
                        .text{
                            position: absolute;
                            left: 18px;
                            bottom: 15px;
                            z-index: 15;
                            padding: 4px 8px;
                            font-size: 12px;
                            font-weight: 500;
                            color: #fff;
                            border-radius: 999px;
                            background-color: #9333eacc;
                        }
                        .bgc{
                            position: absolute;
                            left: 0;
                            top: 0;
                            z-index: 10;
                            width: 100%;
                            height: 100%;
                            background-image: linear-gradient(to top, #0f172a , transparent);
                        }
                    }
                    .career{
                        padding: 24px;
                        .title{
                            display: flex;
                            align-items: center;
                            justify-content: start;
                            .tubiao{
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                margin-right: 10px;
                                width: 40px;
                                height: 40px;
                                font-size: 20px;
                                background-color: #4f46e533;
                                border-radius: 999px;
                            }
                            .right{
                                h3{
                                    font-size: 20px;
                                    color: #fff;
                                }
                                p{
                                    font-size: 12px;
                                    color: #94a3b8;
                                }
                            }
                        }
                        .desc{
                            margin: 12px 0 15px 0;
                            font-size: 14px;
                            color: #cbd5e1;
                            line-height: 20px;
                        }
                        .discover{
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            .number{
                                font-size: 14px;
                                color: #94a3b8;
                                .iconfont{
                                    margin-right: 4px;
                                    font-size: 20px;
                                    color: #94a3b8;
                                }
                            }
                            .going{
                                font-size: 14px;
                                color: #c084fc;
                                .iconfont{
                                    margin-left: 4px;
                                    color: #c084fc;
                                }
                                &:hover{
                                    color: #fff;
                                    .iconfont{
                                        color: #fff;
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        .bottom{
            margin-top: 65px;
            padding: 0 16px;
            .title{
                display: flex;
                justify-content: space-between;
                align-items: center;
                h2{
                    font-size: 24px;
                    font-weight: 700;
                }
                .button{
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
            .main{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 22px;
                height: 174px;

                li{
                    transition: all 0.5s linear;
                    height: 174px;
                    width: 24.2%;
                    padding: 20px;
                    border: 1px solid #33415580;
                    border-radius: 12px;
                    background-color: #1e293b4d;
                    &:hover{
                        border-color: #47556980;
                        transform: translateY(-5px);
                    }
                    .career{

                        .title{
                            display: flex;
                            align-items: center;
                            justify-content: start;
                            .tubiao{
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                margin-right: 10px;
                                width: 40px;
                                height: 40px;
                                font-size: 20px;
                                background-color: #4f46e533;
                                border-radius: 999px;
                            }
                            .right{
                                h3{
                                    font-size: 17px;
                                    color: #fff;
                                }
                                p{
                                    font-size: 12px;
                                    color: #94a3b8;
                                }
                            }
                        }
                        .desc{
                            margin: 12px 0 15px 0;
                            font-size: 12px;
                            color: #cbd5e1;
                            line-height: 20px;
                            p{
                                color:#cbd5e1;
                                line-height: 16px;
                            }
                        }
                        a{
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 28px;
                            font-size: 12px;
                            background-color: #334155;
                            border-radius: 8px;
                            &:hover{
                                background-color: #475569;
                            }
                        }
                    }
                }
            }
        }
    }

</style>