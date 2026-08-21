<script setup>

</script>
<template>
    <div class="technique">
        <div class="require">
            <h3>核心技能要求</h3>
            <div class="bottom">
                <div class="dot">JavaScript <span>90%</span></div>
                <div class="dot">React <span>85%</span></div>
                <div class="dot">TypeScript <span>80%</span></div>
                <div class="dot">Node.js <span>75%</span></div>
                <div class="dot">HTML/CSS <span>85%</span></div>
                <div class="dot">WebPack <span>70%</span></div>
                <div class="dot">Git <span>80%</span></div>
            </div>
        </div>
        <div class="recommend">
            <div class="xiangzi left">
                <h3>学习资源推荐</h3>
                    <li>
                        <div class="tubiao3" style="background-color: #2563eb33;"><i class="iconfont icon-xuexi_nor" style="color: #60a5fa;"></i></div>
                        <div class="text">
                            <h4>《算法导论》</h4>
                            <p>深入理解计算机算法的经典教材</p>
                        </div>
                    </li>
                    <li>
                        <div class="tubiao3" style="background-color: #16a34a33;"><i class="iconfont icon-qianduankaifa" style="color: #4ade80;"></i></div>
                        <div class="text">
                            <h4>前端开发实战课程</h4>
                            <p>React和Vue实战项目教程</p>
                        </div>
                    </li>
                    <li>
                        <div class="tubiao3" style="background-color: #ca8a0433;"><i class="iconfont icon-sangeren" style="color: #facc15;"></i></div>
                        <div class="text">
                            <h4>开源项目贡献</h4>
                            <p>参与GitHub上的开源项目，提升实战经验</p>
                        </div>
                    </li>
            </div>
            <div class="xiangzi right">
                <h3>技能提升路径</h3>
                <div class="tree">
                    <div class="border"></div>
                    <li>
                        <div class="ball">1</div>
                        <h4>基础阶段</h4>
                        <p>掌握HTML/CSS/JavaScript基础</p>
                        <div class="button">
                            <div class="lizi">HTML5</div>
                            <div class="lizi">CSS3</div>
                            <div class="lizi">JavaScript</div>
                            <div class="lizi">基础算法</div>
                        </div>
                    </li>
                    <li>
                        <div class="ball">2</div>
                        <h4>进阶阶段</h4>
                        <p>学习前端框架和工程化</p>
                        <div class="button">
                            <div class="lizi">React/Vue</div>
                            <div class="lizi">TypeScript</div>
                            <div class="lizi">WebPacl</div>
                            <div class="lizi">HTTP</div>
                        </div>
                    </li>
                    <li>
                        <div class="ball">3</div>
                        <h4>高级阶段</h4>
                        <p>深入学习性能优化和架构设计</p>
                        <div class="button">
                            <div class="lizi">性能优化</div>
                            <div class="lizi">架构设计</div>
                            <div class="lizi">微前端</div>
                            <div class="lizi">跨端开发</div>
                        </div>
                    </li>
                </div>
            </div>
        </div>
    </div>
</template>
<style lang="scss">
    .technique {
        margin-top: 24px;
        height: 564px;
        // background-color: pink;
        .require{
            padding: 24px;
            height: 136px;
            background-color: #1e293b80;
            border-radius: 12px;
            h3{
                font-size: 20px;
                font-weight: 600;
            }
            .bottom{
                margin-top: 20px;
                display: flex;
                gap: 10px;
                .dot{
                    padding: 8px 16px;
                    font-size: 15px;
                    background-color: #8b5cf68f;
                    border-radius: 999px;
                    span{
                        font-size: 12px;
                    }
                }
            }
        }
        .recommend{
            display: flex;
            justify-content: space-between;
            margin-top: 30px;
            height: 396px;
             h3{
                margin-bottom: 20px;
                font-size: 20px;
                font-weight: 600;
            }
            .xiangzi{
                padding: 24px;
                width: 49%;
                background-color: #1e293b80;
                border-radius: 12px;
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
            .right{
                .tree{
                    position: relative;
                    height: 304px;
                    .border{
                        position: absolute;
                        top: 0;
                        left: 15px;
                        height: 100%;
                        width: 1.5px;
                        background-color: #334155;
                    }
                    li{
                        margin: 0;
                        position: relative;
                        display: block;
                        padding-left: 48px;
                        padding-bottom: 32px;
                        // height: 112px;
                        width: 100%;
                        // background-color: pink;
                        .ball{
                            position: absolute;
                            top: 0;
                            left: 15px;
                            transform: translateX(-50%);
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            width: 32px;
                            height: 32px;
                            border-radius: 999px;
                            background-color: #9333ea;
                        }
                        h4{
                            font-size: 16px;
                        }
                        p{
                            margin-top: 0px;
                            font-size: 14px;
                            color: #94a3b8;
                            line-height: 28px;
                        }
                        .button{
                            display: flex;
                            gap: 5px;
                            .lizi{
                                display: inline-block;
                                font-size: 12px;
                                padding: 4px 8px;
                                border-radius: 4px;
                                background-color: #334155;
                            }
                        }
                    }

                }
            }
        }
    }
</style>