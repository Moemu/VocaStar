<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import Data from "./components/data.vue";
const router = useRouter();


const tableData = ['数据看版']
const id = ref(0);
const changeTable = (index) => {
    id.value = index;
}

</script>

<template>
    <div class="user-container">
        <div class="box">
            <div class="left">
                <img src="../../assets/iconfont/地球.svg" alt="">
                <h1>职业探索宇宙</h1>
            </div>
            <div class="middle">
                <ul>
                    <li>
                        <RouterLink to="/">
                            <i class="iconfont icon-shouye-shouye second"> 职业探索</i>
                        </RouterLink>
                    </li>
                    <li>
                        <RouterLink to="/evaluation">
                            <i class="iconfont icon-pingjiaceping second"> 职业测评</i>
                        </RouterLink>
                    </li>
                    <li>
                        <RouterLink>
                            <i class="iconfont icon-sangeren second"> 学习社区</i>
                        </RouterLink>
                    </li>
                    <li>
                        <RouterLink to="/user">
                            <i class="iconfont icon-customer-fill first"> 个人中心</i>
                        </RouterLink>
                    </li>
                </ul>
            </div>
        </div>
        <div class="top">
            <div class="insight">
                <div class="left">
                    <img src="https://space.coze.cn/api/coze_space/gen_image?image_size=square&prompt=User%20avatar%20professional&sign=715bc8643e19b13f1c1480c3feefde0f" alt="">
                    <div class="check">
                        <i class="iconfont icon-check"></i>
                    </div>
                    <div class="text">
                        <h2>Moemu</h2>
                        <p>计算机科学专业·大二学生</p>
                        <div class="button">
                            <div class="button1">
                                <i class="iconfont icon-zhuce"></i>编辑资料
                            </div>
                            <div class="button2">
                                <i class="iconfont icon-huangguan"></i>升级会员
                            </div>
                        </div>
                    </div>
                </div>
                <div class="right">
                    <div class="points">
                        <i class="iconfont icon-jifen"></i>
                        <div class="number"><p>总积分</p><span>320</span></div>
                    </div>
                    <div class="level">
                        <i class="iconfont icon-shoucang"></i>
                        <div class="number"><p>等级</p><span>Lv.4</span></div>
                    </div>
                </div>
            </div>
            <div class="table">
                <li v-for="(i,index) in tableData" :key="index" :class="{active: id == index}" @click="changeTable(index)">{{ i }}</li>
            </div>
            <div class="main" v-if="id == 0" :class="{active: id == 0}">
                <Data/>
            </div>
            <div class="footer">
                <p>与志同道合的伙伴一起，探索职业无限可能</p>
                <div class="tubiao">
                    <i class="iconfont icon-wenhao"></i>
                    <i class="iconfont icon-shezhi"></i>
                </div>
            </div>
        </div>
    </div>
</template>

<style lang="scss">
    .user-container {
        // height: 200px;
        width: 100%;
        background-image: linear-gradient(to bottom, #0f172a , #020617);
        .box{
            position: fixed;
            top: 0;
            left: 0;
            z-index: 999;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 16px;
            width: 100%;
            height: 56px;
            background: #0f1a2bcc;
            backdrop-filter: blur(12px);
            border-bottom: 1px solid #1e293b;
            .left{
                display: flex;
                align-items: center;
                width: 12%;
                img{
                    width: 40px;
                    height: 40px;
                }
                h1{
                    margin-left: 2px;
                    font-size: 20px;
                    font-weight: 700;
                    color: transparent;
                    background-image: linear-gradient(to right,#c084fc,#3b82f6);
                    background-clip: text;
                }
            }

            .middle{
                width: 29%;
                // background-color: pink;
                ul{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    li{
                        .iconfont{
                            font-size: 17px;
                        }
                        .first:hover{
                            color: #c084fc;
                        }
                        .second{
                            color: #cbd5e1;
                            &:hover{
                                color: #fff;
                            }
                        }
                    }
                }

            }

            .right{
                display: flex;
                align-items: center;
                width: 13.5%;
                // background-color: pink;
                .iconfont{
                    color: #cbd5e1;
                    position: relative;
                    margin-left: 40px;
                    font-size: 25px;
                    &:hover{
                        color: #fff;
                        .number{
                            color: #fff;
                        }
                    }
                    .number{
                        position: absolute;
                        right: 0px;
                        top: -5px;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        width: 16px;
                        height: 16px;
                        font-size: 12px;
                        color: #cbd5e1;
                        border-radius: 999px;
                        background-color: #ef4444;
                    }
                }
                .user{
                    position: relative;
                    display: flex;
                    align-items: center;
                    margin-left: 12px;
                    img{
                        width: 40px;
                        height: 40px;
                        border-radius: 999px;
                        border: 2px solid #a855f74d;
                    }
                    p{
                        margin-left: 8px;
                        font-size: 14px;
                    }
                    .iconfont{
                        margin-left: 2px;
                        margin-top: 3px;
                        &:hover{
                            color: #cbd5e1;
                        }
                    }
                    &:hover{
                        cursor: pointer;
                        .iconfont{
                            color: #fff;
                        }
                        .second-menu{
                            visibility: visible;
                        }
                    }
                    .second-menu{
                        transition: all .3s;
                        visibility: hidden;
                        position: absolute;
                        right: 4px;
                        bottom: -140px;
                        padding: 6px 0;
                        width: 192px;
                        height: 132px;
                        background-color: #1e293b;
                        border-radius: 8px;
                        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
                        li{
                            display: flex;
                            align-items: center;
                            padding: 7px 0 7px 12px;
                            color: #cbd5e1;
                            .iconfont{
                                font-size: 17px;
                                margin-right: 6px;
                                &:hover{
                                    color: #cbd5e1;
                                }
                            }
                            &:hover{
                                background-color: #334155;
                                color:#fff;
                                .iconfont{
                                    color: #fff;
                                }
                            }
                        }
                        .line{
                            margin: 5px 0;
                            border-top: 1px solid #334155;
                        }
                        .third{
                            color: #f87171;
                            .iconfont{
                                color: #f87171;
                            }
                            &:hover{
                                color: #f87171;
                                .iconfont{
                                    color: #f87171;
                                }
                            }
                        }
                    }
                }
            }
            .right-second{
                font-size: 17px;
                color: #cbd5e1;
                .iconfont{
                    margin-left: 8px;
                    font-size: 18px;
                    color: #cbd5e1;
                }
                &:hover{
                    color: #fff;
                    cursor: pointer;
                    .iconfont{
                        color: #fff;
                    }
                }
            }
        }
        .top{
            position: relative;
            padding: 90px 16px 0;
            width: 100%;
            // height: 420px;
            .insight{
                display: flex;
                justify-content: space-between;
                padding:30px;
                width: 100%;
                height: 178px;
                background-image: linear-gradient(to right,rgb(30 41 59 / 0.7) , rgb(88 28 135 / 0.3));
                border: 1px solid #581c874d;
                border-radius: 16px;
                .left{
                    height: 100%;
                    position: relative;
                    display: flex;
                    align-items: center;
                    img{
                        margin-right: 30px;
                        width: 92px;
                        height: 92px;
                        border-radius: 999px;
                        border: 4px solid #a855f74d;
                    }
                    .check{
                        position: absolute;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        left: 70px;
                        top: 80px;
                        width: 32px;
                        height: 32px;
                        border-radius: 999px;
                        background-color: #16a34a;
                        border: 2px solid #0f172a;
                    }
                    .text{
                        // background-color: pink;
                        h2{
                            margin-bottom: 5px;
                            line-height: 32px;
                            font-size: 24px;
                        }
                        p{
                            font-size: 17px;
                            color: #94a3b8;
                        }
                        .button{
                            margin-top: 20px;
                            display: flex;
                            .button1,
                            .button2 {
                                padding: 8px 16px;
                                font-size: 14px;
                                border-radius: 8px;
                                .iconfont{
                                    margin-right: 5px;
                                }
                            }
                            .button1{
                                margin-right: 10px;
                                background-color: #1e293b;
                                &:hover{
                                    background-color: #334155;
                                }
                            }
                            .button2{
                                background-color: #9333ea;
                                &:hover{
                                    background-color: #7e22ce;
                                }
                            }
                        }
                    }
                }
                .right{
                    margin-top: 20px;
                    display: flex;
                    .points{
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        width: 92px;
                        height: 56px;
                        background-color: #1e293bb3;
                        border-radius: 8px;
                        .iconfont{
                            margin-right: 5px;
                            color: #facc15;
                            font-size: 18px;
                        }
                        .number{
                            p{
                                font-size: 12px;
                                line-height: 16px;
                                color: #94a3b8;
                            }
                            span{
                                font-weight: 500;
                            }
                        }

                    }
                    .level{
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        margin-left: 10px;
                        width: 92px;
                        height: 56px;
                        background-color: #1e293bb3;
                        border-radius: 8px;
                        .iconfont{
                            color: #facc15;
                            margin-right: 5px;
                        }
                        .number{
                            p{
                                font-size: 12px;
                                line-height: 16px;
                                color: #94a3b8;
                            }
                            span{
                                font-weight: 500;
                            }
                        }
                    }
                }
            }
            .table{
                margin-top: 58px;
                display: flex;
                width: 100%;
                height: 42px;
                border-bottom: 1px solid #1e293b;
                // background-color: pink;
                li{
                    transition: 0.1s ease;
                    margin-right: 35px;
                    height: 35px;
                    font-size: 14px;
                    font-weight: 500;
                    line-height: 20px;
                    color: #9dabbf;
                     cursor: pointer;
                    // border: 1px solid #581c874d;
                    &:hover{
                        color: #cbd5e1;
                    }
                    &.active{
                        border-bottom: 2px solid #a855f7;
                        color: #fff;
                    }
                }
            }
            .main{
                transform: translateY(20px);
                opacity: 0;
                transition: all 0.3s ease;
                width: 100%;
                height: 1400px;
                // background-color: #fff;
                &.active{
                    opacity: 1;
                    transform: translate(0px);
                }
            }
            .footer{
                position: absolute;
                bottom: 0px;
                left: 0px;
                height: 49px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 16px;
                width: 100%;
                background-color: #0f172acc;
                border: 1px solid #1e293b;
                p{
                    font-size: 14px;
                    color: #94a3b8;
                }
                .tubiao{
                    .iconfont{
                        margin-left: 14px;
                        font-size: 18px;
                        color: #94a3b8;
                        &:hover{
                            color: #fff;
                            cursor: pointer;
                        }
                    }
                }
            }
        }
    }
</style>