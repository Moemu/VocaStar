<script setup>

</script>

<template>
    <div class="home-footer">
        <div class="top">
            <div class="left">
                <div class="logo">
                    <i class="iconfont icon-diqiu"></i>
                    <h1>职趣星航</h1>
                </div>
                <p>通过游戏化和场景化的方式，帮助你探索自身职业兴趣与能力，发现适合你的职业星球。</p>
                <div class="tubiao">
                    <RouterLink to="/">
                        <div class="button">
                            <i class="iconfont icon-weixin"></i>
                        </div>
                    </RouterLink>
                    <RouterLink to="/">
                        <div class="button">
                            <i class="iconfont icon-xinlangweibo"></i>
                        </div>
                    </RouterLink>
                    <RouterLink to="/">
                        <div class="button">
                            <i class="iconfont icon-xiaomao"></i>
                        </div>
                    </RouterLink>
                </div>
            </div>

            <div class="right">
                <ul class="first">
                    <li class="first-li">
                        <h4>快速链接</h4>
                        <ul class="second">
                            <li class="seccond-li"><RouterLink to="/">首页</RouterLink></li>
                            <li class="seccond-li"><RouterLink to="//career-explore">职业星球</RouterLink></li>
                            <li class="seccond-li"><RouterLink to="/document">职业测评</RouterLink></li>
                            <li class="seccond-li"><RouterLink to="/">学习社区</RouterLink></li>
                            <li class="seccond-li"><RouterLink to="/user">个人中心</RouterLink></li>
                        </ul>
                    </li>
                    <li class="first-li">
                        <h4>支持与帮助</h4>
                        <ul class="second">
                            <li class="seccond-li"><RouterLink to="/">使用指南</RouterLink></li>
                            <li class="seccond-li"><RouterLink to="/">常见问题</RouterLink></li>
                            <li class="seccond-li"><RouterLink to="/">联系我们</RouterLink></li>
                            <li class="seccond-li"><RouterLink to="/">反馈建议</RouterLink></li>
                        </ul>
                    </li>
                    <li class="first-li">
                        <h4>法律信息</h4>
                        <ul class="second">
                            <li class="seccond-li"><RouterLink to="/">用户协议</RouterLink></li>
                            <li class="seccond-li"><RouterLink to="/">隐私政策</RouterLink></li>
                            <li class="seccond-li"><RouterLink to="/">Cookie政策</RouterLink></li>
                            <li class="seccond-li"><RouterLink to="/">版权声明</RouterLink></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
        <div class="bottom">
            <p>© 2025 职趣星航 版权所有 | 职业探索平台</p>
        </div>
    </div>
</template>

<style lang="scss">
    .home-footer {
        margin-top: 62px;
        padding: 32px 16px;
        height: 342px;
        background-color: #fff;
        background-color: #0f1a2bcc;
        border: 1px solid #1e293b;
        .top{
            display: flex;
            justify-content: space-between;
            height: 192px;
            .left{
                width: 23%;
                height: 100%;
                // background-color: pink;
                .logo{
                    display: flex;
                    align-items: center;
                    i{
                        font-size: 24px;
                        color: #a855f7;
                    }
                    h1{
                        margin-left: 6px;
                        font-size: 20px;
                        font-weight: 700;
                        color: transparent;
                        background-image: linear-gradient(to right,#c084fc,#3b82f6);
                        background-clip: text;
                    }
                }
                p{
                    margin-top: 16px;
                    font-size: 14px;
                    line-height: 20px;
                    color: #94a3b8;
                }
                .tubiao{
                        display: flex;
                        margin-top: 16px;
                        .button{
                            margin-right: 14px;
                            color: #94a3b8;
                            .iconfont{
                                font-size: 20px;
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
            .right{
                width: 74%;
                // background-color: #fff;
                .first{
                    height: 100%;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    .first-li{
                        width: 31.6%;
                        height: 100%;
                        // background-color: pink;
                        h4{
                            margin-bottom: 16px;
                            font-size: 16px;
                        }
                        .second{
                            height: 80%;
                            a{
                                display: flex;
                                margin-top: 13.5px;
                                font-size: 14px;
                                color: #94a3b8;
                                &:hover{
                                    color: #fff;
                                }
                            }
                        }
                    }
                }
            }
        }
        .bottom{
            margin-top: 30px;
            border-top:1px solid #1e293b;
            p{
                margin-top: 32px;
                text-align: center;
                font-size: 14px;
                color: #64748b;
            }
        }
    }

</style>