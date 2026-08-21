<script setup>
import img1 from '../../assets/plant/屏幕截图 2025-10-01 115709_20251001115720.png'
import img2 from '../../assets/plant/屏幕截图 2025-10-01 115644_20251001115720.png'
import img3 from '../../assets/plant/d93c4ea63126ae8fb4409a6debe9685a.png'
import img4 from '../../assets/plant/b7154a55d44ba1d7af286effdffe1dd0.png'
import { getPlantsAPI } from '../../apis/plant'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter();


const baseUrl = ref(import.meta.env.VITE_API_BASE_URL || '');
const plantsList = ref({});
const getPlants = async () => {
    const res = await getPlantsAPI();
    plantsList.value = res.data;
    console.log('这个是',plantsList);
    console.log('这个是value',plantsList.value);
    console.log('这个是value.data',plantsList.value);
    console.log('这个是value.data.galaxies',plantsList.value.galaxies[0].planets);
}
const plantId = ref(0);


const last = () => {
    if(plantId.value >= 0 && plantId.value < 3){
        plantId.value ++;
    }else if(plantId.value == 3){
        plantId.value = 0;
    }
}

const next = () => {
    if(plantId.value > 0 && plantId.value <= 3){
        plantId.value --;
    }else if(plantId.value == 0){
        plantId.value = 3;
    }
}

// 1. 职业分类（多选）：用数组存选中的分类
const selectedCates = ref(['互联网·通信', '金融·建筑·工程', '医疗·生物·化工', '农·林·牧·渔']);

// 2. 薪资范围：用ref存滑块的选中值（对应50k+）
const salary_avg = ref(200); // 示例：滑块当前值

// 3. 推荐开关：布尔值
const isRecommend = ref(false);
const isRuanjian = (name) => {
    if(name == '软件工程师'){
        router.push('/career')
    }
}


onMounted(() => getPlants());
</script>

<template>
    <div class="career-container">
        <div class="menu">
            <h3>职业星球探索</h3>
            <p>发现属于你的职业星系</p>
            <input class="search-input" type="text" placeholder="搜索职业或技能...">
            <h4>职业分类</h4>
            <label class="box4" for="category1">
                <input class="checkbox" type="checkbox" id="category1" value="selectedCates[0]" v-model="selectedCates">
                互联网·通信
            </label>
            <label class="box4" for="category2">
                <input class="checkbox" type="checkbox" id="category2" value="selectedCates[1]" v-model="selectedCates">
                金融·建筑·工程
            </label>
            <label class="box4" for="category3">
                <input class="checkbox" type="checkbox" id="category3" value="selectedCates[2]" v-model="selectedCates">
                医疗·生物·化工
            </label>
            <label class="box4" for="category4">
                <input class="checkbox" type="checkbox" id="category4" value="selectedCates[3]" v-model="selectedCates">
                农·林·牧·渔
            </label>
            <h4 class="money">薪资范围<span>50k+</span></h4>
            <input class="range" type="range" min="0" max="50000" step="1000" v-model="salary_avg">
            <p class="money-text"><span>0</span><span>{{ salary_avg }}</span></p>
            <div class="blank">
            </div>
            <div class="left-bottom">
                <div class="left"><h4>推荐给我</h4><p>基于你的兴趣推荐</p></div>
                <div class="right"><el-switch class="switch" v-model="switch1" :active-icon="Check" :inactive-icon="Close"/></div>
            </div>
        </div>
        <div class="plant">
            <div class="nav">
                <li @click="router.push('/')">职业宇宙</li>
                <i class="iconfont icon-arrow-right"></i>
                <li>{{plantsList?.galaxies?.[plantId].name}}</li>
                <i class="iconfont icon-arrow-right"></i>
                <span>软件开发星域</span>
            </div>
            <h2>探索星系<div class="right"><i class="iconfont icon-arrow-left-bold" @click="next"></i><i class="iconfont icon-arrow-right" @click="last"></i></div></h2>
            <div class="plant-list">
                <li v-for="(i,index) in plantsList.galaxies" :key="i.id" @click="plantId = index">
                    <div class="img"><img :class="{active:plantId == index}" :src="baseUrl + i.cover_image_url" alt="" ></img></div>
                    <div class="text"><h4>{{ i.name }}</h4><p>{{ i.category }}</p><div class="dot" v-show="plantId == index"></div></div>
                </li>
            </div>
            <div class="second-plant">
                <h2>职业星球</h2>
                <div class="second-list" >
                    <li v-for="i in plantsList?.galaxies?.[plantId].planets" :key="i.id"  @click="isRuanjian(i.name)">
                        <div class="tupian"><img :src="baseUrl + i.planet_image_url" alt=""></div><h3>{{ i.name }}</h3>
                        <div class="introduction">
                            <h4>{{ i.name }}</h4>
                            <p>薪资范围: {{i.salary_min}}-{{ i.salary_max }}</p>
                            技能要求:
                            <div class="bottom4"><div class="box-item" v-for="value in i.skills_snapshot">{{ value }}</div></div>
                        </div>
                    </li>
                </div>
            </div>
        </div>

    </div>
</template>

<style lang="scss">
    .career-container{
        overflow: hidden;
        display: flex;
        background-color: #050812;
        background: url(../../assets/plant/bf0b5b69adee9b7d22971134c48ec52f.png) no-repeat;
        background-size: cover;
        min-height: 100vh;
        .menu{
            padding: 16px;

            width: 16.5%;
            // background-color: pink;
            border-right: 1px solid #374151;
            h3{
                margin-bottom: 16px;
                font-size: 20px;
                line-height: 28px;
                font-weight: 700;
            }
            p{
                font-size: 14px;
                line-height: 20px;
                color: #9ca3af;
            }
            .search-input{
                margin-top: 32px;
                width: 100%;
                height: 38px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 700;
                line-height: 20px;
                background-color: #1f2937;
                outline: 1px transparent solid;
                outline-offset: 1px;
                border: 1px solid #374151;
                border-radius: 8px;
                &:focus{
                    border: 2px solid #3b82f6;
                    outline: 2px solid transparent;
                }
            }
            h4{
                display: flex;
                margin-top: 32px;
                font-size: 18px;
                line-height: 28px;

            }
            .box4{
                display: flex;
                align-items: center;
                margin-top: 10px;
                font-size: 16px;
                .checkbox{
                    display: block;
                    margin-top: 3px;
                    margin-right: 8px;
                }
            }
            .money{
                display: flex;
                justify-content: space-between;
                align-items: center;
                span{
                    font-size: 14px;
                    color: #9ca3af;
                }
            }
            .range{
                width: 100%;
                margin-top: 18px;
                background-color: #374151;
            }
            .money-text{
                margin-top: 0px;
                display: flex;
                justify-content: space-between;
                span{
                    font-size: 12px;
                    color: #6b7280;
                }
            }
            input[type='range']::-webkit-slider-runnable-track{
                background-color: #374151;
                border-radius: 999px;
            }
            .blank{
                height: 60px;
                border-bottom: 1px solid #374151;
            }
            .left-bottom{
                margin-top: 16px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                h4{
                    margin: 0;
                    font-size: 16px;
                    font-weight: 500;
                    color: #e5e7eb;
                }
                p{
                    font-size: 12px;
                    line-height: 12px;
                    color: #9ca3af;
                }
                .el-switch__core{
                    height: 23px;
                    background-color: #374151;
                    border-color: #374151;
                    border-radius: 999px;
                }
                .el-switch.is-checked .el-switch__core{
                    background-color: #409eff;
                    border-color: #409eff;
                }
            }
        }
        .plant{
            flex: 1;
            padding: 24px;
            .nav{
                display: flex;
                margin-top: 5px;
                height: 10px;
                align-items: center;
                font-size: 14px;
                line-height: 20px;
                li{
                    color: #9ca3af;
                    &:hover{
                        color: #60a5fa;
                    }
                }
                .iconfont{
                    margin: 2px 4px 0 15px;
                    color: #6b7280;
                    font-weight: 700;
                    font-size: 13px;
                }
                span{
                    color: #60a5fa;
                }
            }
            h2{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 40px;
                font-size: 24px;
                .right{
                    display: flex;
                    i{
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        margin-left: 8px;
                        height: 40px;
                        width: 40px;
                        border-radius: 999px;
                        background-color: #1f293780;
                        &:hover{
                            background: #37415180;
                            cursor: pointer;
                        }
                    }
                }
            }
            .plant-list{
                display: flex;
                height: 354px;
                justify-content: space-between;
                align-items: center;
                margin-top: 20px;
                li{
                    width: 22.5%;
                    height: 100%;
                    // background-color: pink;
                    background-image: radial-gradient(circle at center, rgba(255, 255, 255, 0.1), transparent 70%);
                    &:hover{
                        cursor: pointer;
                        .img{
                            img{
                                transform: scale(1.10);
                                box-shadow:  0 0 25px rgba(59, 130, 246, 0.5);
                            }
                        }
                    }
                    .img{
                        width: 100%;
                        height: 280px;
                        animation: xuanzhuan 20s linear infinite;
                        img{
                            transition: transform 0.3s ease;
                            object-fit: cover;
                            width: 100%;
                            height: 100%;
                            border-radius: 999px;
                            &.active{
                                transform: scale(1.05);
                            }
                        }
                    }
                    .text{
                        position: relative;
                        text-align: center;
                        margin-top: 15px;
                        h4{
                            font-weight: 500;
                            font-size: 16px;
                        }
                        p{
                            font-size: 14px;
                            line-height: 20px;
                            color: #d1d5db;
                        }
                        .dot{
                            animation: pulse 2s ease-in-out infinite;
                            position: absolute;
                            bottom: -8px;
                            left: 50%;
                            transform: translateX(-50%);
                            width: 13px;
                            height: 13px;
                            border-radius: 999px;
                            background-color: #facc15;
                        }
                    }
                }
            }
            .second-plant{
                h2{
                    margin-top: 30px;
                    font-size: 24px;
                }
                .second-list{
                    display: flex;
                    // justify-content: space-between;
                    flex-wrap: wrap;
                    gap: 30px;
                    margin-top: 25px;
                    margin-bottom: 32px;
                    width: 100%;
                    li{
                        position: relative;
                        text-align: center;
                        height: 215px;
                        width: 15%;
                        // background-color: pink;
                        .tupian{
                            height: 182px;
                            border-radius: 999px;
                            animation: xuanzhuan 20s linear infinite;
                            img{
                                width: 100%;
                                height: 100%;
                                object-fit: cover;
                                border-radius: 999px;
                                box-shadow: 0 0 0 calc(2px + 0px) rgb(59 130 246 / 0.5);
                            }
                        }
                         h3{
                            margin-top: 5px;
                            font-size: 16px;
                            font-weight: 500;
                        }
                         &:hover{
                            cursor: pointer;
                            .introduction{
                                display: block;
                            }
                        }
                        .introduction{
                            display: none;
                            text-align: start;
                            position: absolute;
                            left: 50%;
                            top: -75%;
                            transform: translate(-50%);
                            padding: 14px;
                            width: 100%;
                            // height: 150px;
                            font-size: 14px;
                            color: #969ca9;
                            background-color: #111827;
                            border-radius: 8px;
                            h4{
                                font-size: 14px;
                            }
                            p{
                                line-height: 28px;
                                font-size: 14px;
                                color: #b7bcc3;
                            }
                            .bottom4{
                                margin-top: 5px;
                                display: flex;
                                gap: 4px;
                                width: 100%;
                                flex-wrap: wrap;
                                .box-item{
                                    display: flex;
                                    align-items: center;
                                    padding: 1px 5px;
                                    color: #bcc0c7;
                                    background-color: #1f293c;
                                    border-radius: 999px;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    @keyframes xuanzhuan {
                                100% {
                                    transform: rotate(360deg);
                                }
                            }
    @keyframes pulse {
        0%, 100% {
        opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
</style>