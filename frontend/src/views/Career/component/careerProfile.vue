<script setup>

</script>
<template>
    <div class="career-profile">
        <div class="introduction">
            <h3>职业描述</h3>
            <p>软件工程师负责设计、开发和维护软件系统，解决复杂技术问题。他们需要掌握多种编程语言和开发工具，持续学习新技术，并与团队协作完成项目。 软件工程师需要具备扎实的编程基础，能够理解和实现复杂的业务逻辑，同时需要具备良好的沟通能力和团队协作精神。</p>
            <p>随着技术的不断发展，软件工程师需要保持持续学习的热情，关注行业动态和新技术趋势，不断提升自己的专业技能和解决问题的能力。</p>
        </div>
        <div class="main-text">
            <div class="left hezi">
                <h3>工作内容</h3>
                <li><i class="iconfont icon-dui"></i><p>参与软件系统的设计与开发，编写高质量代码</p></li>
                <li><i class="iconfont icon-dui"></i><p>进行代码审查，确保代码质量和性能</p></li>
                <li><i class="iconfont icon-dui"></i><p>诊断和修复软件缺陷，优化系统性能</p></li>
                <li><i class="iconfont icon-dui"></i><p>与产品经理和设计师协作，理解需求并转化为技术方案</p></li>
                <li><i class="iconfont icon-dui"></i><p>参与技术文档的编写和维护</p></li>
            </div>
            <div class="right hezi">
                <h3>职业前景</h3>
                <p>随着数字化转型的加速，软件工程师的需求持续增长。职业发展路径清晰，可向资深工程师、技术专家、架构师或技术管理方向发展。</p>
                <div class="route">
                    <h4>常见发展路径</h4>
                    <span>初级工程师 <i class="iconfont icon-youjiantou"></i></span>
                    <span>中级工程师 <i class="iconfont icon-youjiantou"></i></span>
                    <span>高级工程师 <i class="iconfont icon-youjiantou"></i></span>
                    <span style="color: #c084fc;">技术专家/架构师 </span>
                </div>
            </div>
        </div>
    </div>
</template>
<style lang="scss">
    .career-profile {
        margin-top: 24px;
        height: 480px;
        // background-color: pink;
        .introduction {
            padding: 24px;
            height: 186px;
            background-color: #1e293b80;
            border-radius: 12px;
            h3{
                font-size: 20px;
                font-weight: 600;
            }
            p{
                margin: 16px 0;
                font-size: 16px;
                color: #cbd5e1;
                // line-height: 30px;
            }
        }
        .main-text{
            margin-top: 30px;
            display: flex;
            justify-content: space-between;
            height: 260px;
            // background-color: #1e293b80;
            // border-radius: 12px;
            .hezi{

                padding: 24px;
                width: 49%;
                height: 100%;
                background-color: #1e293b80;
                border-radius: 12px;
                 h3{
                    margin-bottom: 12px;
                    font-size: 20px;
                    font-weight: 600;
                }
            }
            .left{
                li{
                    margin-bottom: 14px;
                    display: flex;
                    align-items: center;
                    .iconfont{
                        margin-top: 3px;
                        margin-right: 10px;
                        font-size: 17px;
                        color: #22c55e;
                    }
                     p{
                        font-size: 16px;
                        color: #cbd5e1;
                        // line-height: 30px;
                    }
                }
            }
            .right{
                  p{
                    margin: 16px 0;
                    font-size: 16px;
                    color: #cbd5e1;
                    // line-height: 30px;
                }
                .route{
                    padding: 16px;
                    margin-top: 15px;
                    height: 84px;
                    background-color: #0f172acc;
                    border-radius: 8px;
                    h4{
                        margin-bottom: 4px;
                    }
                    span{
                        align-items: center;
                        margin-right: 5px;
                        font-size: 14px;
                        color: #cbd5e1;
                        .iconfont{
                            font-size: 13px;
                        }
                    }
                }
            }
        }
    }
</style>