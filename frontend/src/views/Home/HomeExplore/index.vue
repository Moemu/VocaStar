<script setup>
import { ref } from 'vue';
const commentList = ref([]);
commentList.value = [
    {url:'https://space.coze.cn/api/coze_space/gen_image?image_size=square&prompt=User%20avatar%201&sign=7cc5e5e9d261bde8ce5fccdb28c709aa', name:'张三', time:'刚刚',contentOne:'刚刚解锁了',task:'软件工程师', color:'#c084fc',contentTwo:'星球',iconfont:'iconfont icon-diqiu',like:24,comment:24},
    {url:'https://space.coze.cn/api/coze_space/gen_image?image_size=square&prompt=User%20avatar%20professional&sign=715bc8643e19b13f1c1480c3feefde0f', name:'产品经理小组', time:'2小时前',contentOne:'发布了新的学习任务',task:'《用户需求分析实战》',color:'#60a5fa',contentTwo:'，完成可获得30积分',iconfont:'',like:15,comment:5},
    {url:'https://space.coze.cn/api/coze_space/gen_image?image_size=square&prompt=User%20avatar%203&sign=c8bb87cc81bc89d5d3d3ceaa37903fe2', name:'李四', time:'昨天',contentOne:'分享了新的学习资源：',task:'《React Hooks完全指南》',color:'#60a5fa',contentTwo:'，快来一起学习吧！',iconfont:'',like:42,comment:12},
]


</script>

<template>
    <div class="home-explore">
        <div class="title">
            <h2>探索动态</h2>
            <div class="button">
                查看全部<i class="iconfont icon-youjiantou"></i>
            </div>
        </div>
        <div class="comment">
            <li v-for="i in commentList">
                <div class="user">
                    <img :src="i.url" alt="">
                </div>
                <div class="text">
                    <div class="top">
                        {{ i.name }}
                        <span class="time">{{ i.time }}</span>
                    </div>
                    <div class="middle">
                        {{ i.contentOne }}<span class="color" :style="{color: i.color}"> {{ i.task }} </span> {{ i.contentTwo }} <i :class="i.iconfont" :style="{color: i.color}"></i>
                    </div>
                    <div class="bottom">
                        <div class="button">
                            <i class="iconfont icon-dianzan"></i> {{ i.like }}
                        </div>
                         <div class="button">
                            <i class="iconfont icon-icon_comment"></i> {{ i. comment}}
                        </div>
                    </div>
                </div>
            </li>
        </div>
    </div>

</template>

<style lang="scss">
    .home-explore{
        padding: 0 16px;
        width: 100%;
        // background-color: pink;
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
        .comment{
            margin-top: 22px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            width: 100%;
            height: 450px;
            padding: 24px;
            background-color: #1e293b4d;
            border: 1px solid #33415580;
            border-radius: 16px;
            li{
                display: flex;
                height: 84px;
                // background-color: pink;
                .user{
                    margin-right: 16px;
                    img{
                        width: 40px;
                        height: 40px;
                        border-radius: 999px;
                    }
                }
                .text{
                    .top{
                        display: flex;
                        justify-content: start;
                        align-items: center;
                        font-size: 17px;
                        font-weight: 500;
                        .time{
                            margin-left: 8px;
                            color: #64748b;
                            font-size: 12px;
                            line-height: 18px;

                        }
                    }
                    .middle{
                        margin-top: 5px;
                        color: #cbd5e1;
                        font-size: 16px;
                        font-weight: 500;
                    }
                    .bottom{
                        display: flex;
                        margin-top: 10px;
                        .button{
                            margin-right: 25px;
                            color: #94a3b8;
                            .iconfont{
                                color: #94a3b8;
                            }
                            &:hover{
                                cursor: pointer;
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
</style>