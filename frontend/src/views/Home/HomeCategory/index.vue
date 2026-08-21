<script setup>
import { ref } from 'vue'

const category = ref([]);
category.value = [{photo: '🪐', title: '职业星球', desc: '探索50+职业星球'},
            {photo: '✨', title: '趣味测评', desc: '发现你的职业倾向'},
            {photo: '🎭', title: 'Cosplay', desc: '角色扮演职业体验'},
            {photo: '👥', title: '学习社区', desc: '加入兴趣小组'}
            ];


</script>

<template>
    <div class="category">
        <div class="top">
            <div class="bgc"></div>
            <img src="https://space.coze.cn/api/coze_space/gen_image?image_size=landscape_16_9&prompt=Starry%20night%20sky%20with%20galaxy%20and%20nebula%20in%20space&sign=86c1be47f4082a079a8353700b02fe3f" alt="">
            <div class="text">
                <h1>发现你的职业星轨</h1>
                <p>一次测评，一场角色扮演，探索适合你的职业星球</p>
                <div class="button">
                    <router-link to="/document">
                        <li class="career">开启职业测评 <i class="iconfont icon-youjiantou"></i></li>
                    </router-link>
                    <router-link to="/career-explore">
                        <li class="plant">探索职业星球</li>
                    </router-link>
                </div>
            </div>
        </div>
        <div class="bottom">
            <li v-for="i in category">
                    <RouterLink>
                        <span class="photo">{{ i.photo }}</span>
                        <h3>{{ i.title }}</h3>
                        <p>{{ i.desc }}</p>
                    </RouterLink>
            </li>
        </div>
    </div>
</template>

<style>
    .category {
        padding-top: 10px;
        width: 100%;
        height: 580px;
        /* background-color: pink; */
        .top{
            position: relative;
            text-align: center;
            height: 320px;
            border-radius: 24px;
            .bgc{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-image: linear-gradient(to right, #0f1a2b , rgb(15 26 43 / 0.7) , #0f1a2b);
                border-radius: 24px;
            }
            img{
                width: 100%;
                height: 100%;
                object-fit: cover;
                border-radius: 24px;
            }
            .text{
                position: absolute;
                top: 21.5%;
                left: 0;
                text-align: center;
                width: 100%;
                height: 186px;
                /* background-color: pink; */
                h1{
                    font-size: 48px;
                }
                p{
                    font-size: 20px;
                    color: #cbd5e1;
                }
                .button{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin-top: 22px;
                    li{
                        transition: all 0.5s;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        padding: 16px 30px;
                        width: 200px;
                        height: 65px;
                        font-size: 18px;
                        font-weight: 500;
                        background-color: #fff;
                        border-radius: 12px;
                        &:hover{
                            transform: scale(1.05);
                        }
                        &:active{
                            transform: scale(0.95);
                        }

                    }
                    .career{
                        margin-right: 5px;
                        background-image: linear-gradient(to right, #5e17eb , #00f5ff);
                        i{
                            margin-left: 10px;
                            font-size: 18px;
                        }
                        &:hover{
                            background-image: linear-gradient(to right, #7c3aed , #22d3ee);
                        }
                    }
                    .plant{
                        margin-left: 10px;
                        background-color: #1e293b;
                        border: 1px solid #334155;
                        &:hover{
                            background-color:#334155;
                        }
                    }
                }
            }
        }
        .bottom{
            display: flex;
            justify-content: space-between;
            margin-top: 50px;
            padding: 0 16px;
            width: 100%;
            height: 182px;
            /* background-color: pink; */
            li{
                text-align: center;
                transition: all 0.3s;
                padding: 24px;
                width: 23.8%;
                background-color: #fff;
                border-radius: 16px;
                border: 1px solid #33415580;
                background-color: #1e293b80;
                &:hover{
                    transform: scale(1.05);
                    background-color: #1e293bcc;
                    box-shadow: 0px 10px 25px -5px #5e17eb33;
                }
                .photo{
                    display: inline-block;
                    text-align: center;
                    padding-top: 8px;
                    width: 64px;
                    height: 64px;
                    font-size: 30px;
                    border-radius: 99px;
                    background-color: #9333ea33;
                }
                h3{
                    margin-top: 16px;
                }
                p{
                    margin-top: 8px;
                    font-size: 14px;
                    color: #94a3b8;
                }
            }
        }
    }
</style>