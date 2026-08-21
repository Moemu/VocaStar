<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCommunityStore } from '../../../stores/community';
import { ElMessage } from "element-plus";
const communityStore = useCommunityStore();
const baseUrl = ref(import.meta.env.VITE_API_BASE_URL || '');
const activeSlug = ref('all');
console.log(communityStore.teacherCategory);

const filterTeacher = computed(() => {
    if(activeSlug.value == 'all'){
        return communityStore.teacherList?.items;
    }

    return communityStore.teacherList?.items.filter( teacher =>
        teacher.domains.includes(activeSlug.value)
    )
})

// 搜索关键词
const searchKeyWord = ref('');

// 计算属性：过滤小组
const filteredteachers = computed((() => {
    const keyword = searchKeyWord.value.trim().toLowerCase();
    console.log('搜索关键词',filterTeacher);
    const baseList = filterTeacher.value;

    if(!keyword){
        return baseList;
    }

    return baseList.filter(item => {
        // 匹配姓名
        const matchName = item.name.toLowerCase().includes(keyword);
        // 匹配职业
        const matchProfession = item.profession.toLowerCase().includes(keyword);
        // 匹配技能
        const matchTechStack = item.tech_stack.some(skill => skill.toLowerCase().includes(keyword));

        return matchName || matchProfession || matchTechStack;
    })
}))



onMounted(() => {
    communityStore.getTeacherCategory();
    communityStore.getTeacherList();
    console.log(communityStore.teacherCategory);
})
</script>

<template>
    <div class="teacher">
        <div class="explore">
            <h3>导师搜索与筛选</h3>
            <div class="input">
                <input type="text" placeholder="搜索导师姓名,职位或专长..." v-model="searchKeyWord"> <i class="iconfont icon-search1"></i></input>
            </div>
            <h4>导师领域筛选</h4>
            <div class="catogory">
                <li @click ="activeSlug = 'all'":class="{ 'active': activeSlug == 'all' }">全部领域</li>
                <li v-for="(i,index) in communityStore.teacherCategory?.items" @click="activeSlug = i.slug"  :class="{ 'active': activeSlug == i.slug }">{{ i.name }}</li>
            </div>
            <div class="text">
                <h4>为什么选择职业导师</h4>
                <p>职业导师可以为您提供专业指导、职业规划建议和行业洞察，帮助您在职业发展道路上少走弯路，快速成长。</p>
            </div>
        </div>
        <div class="recommendT">
            <h3>推荐导师</h3>
            <div class="box">
                <li v-for="i in filteredteachers">
                    <img :src="baseUrl + i.avatar_url" alt="">
                    <div class="text">
                        <h3>{{ i.name }} <span><i class="iconfont icon-shoucang"></i> {{ i.rating }} <span class="number">({{ i.rating_count }})</span></span></h3>
                        <p>{{ i.profession }}</p>
                        <div class="skill"><span v-for="value in i.tech_stack">{{ value }}</span></div>
                        <div class="money">
                            <div class="left"><span>￥{{ i.fee_per_hour}}</span>/小时</div>
                            <div class="button">
                                <div class="anniu question" @click="() => { ElMessage.success(`已发送向 ${i.name} 提问的请求`)}">
                                    向导师提问
                                </div>
                                <div class="anniu consult" @click="() => { ElMessage.success(`已提交向 ${i.name} 预约的请求`)}">
                                    预约咨询
                                </div>
                            </div>
                        </div>
                    </div>
                </li>
                <div class="nogroups" v-if="!filteredteachers">
                    <i class="iconfont icon-search"></i>
                    <h3>未找到匹配的导师</h3>
                    <p>尝试调整搜索条件或浏览其他分类</p>
                </div>
            </div>
            <!-- <div class="footer">
                <div class="button">
                    查看更多伙伴
                </div>
            </div> -->
        </div>
    </div>

</template>

<style lang="scss">
    .teacher {
        padding: 0 16px;
        .explore {
            padding: 16px;
            height: 301px;
            width: 100%;
            background-color: #1f2937;
            border-radius: 12px;
            h3{
                font-size: 16px;
                margin-bottom: 16px;
            }
            .input{
                position: relative;
                input{
                    padding-left: 40px;
                    width: 100%;
                    height: 50px;
                    color: #9ca3af;
                    font-size: 16px;
                    font-weight: 500;
                    border-radius: 8px;
                    background-color: #111827;
                    border: 1px solid #374151;
                    &:focus{
                        box-shadow: 0 0 0 calc(1.5px + 1.5px) rgb(59 130 246 / 1);
                        border: 0px;
                        outline: transparent;
                    }
                }
                i{
                    position: absolute;
                    top: 12px;
                    left: 10px;
                    font-size: 25px;
                    font-weight: 700;
                    color: #9ca3af;
                }
            }
            h4{
                padding: 0px;
                text-align: start;
                margin: 15px 0 8px;
                font-weight: 500;
            }
            .catogory{
                display: flex;
                gap: 10px;
                margin-top: 15px;
                // height: 36px;
                // background-color: pink;
                li{
                    transition: all 0.3s ease;
                    padding: 8px 16px;
                    font-size: 14px;
                    color: #d1d5db;
                    border-radius: 999px;
                    background-color: #384252;
                    &:hover{
                        background-color: #4b5563;
                        cursor: pointer;
                    }
                    &.active{
                        background-color: #1e3a8a4d;
                        color: #60a5fa;
                        i{
                            color: #60a5fa;
                        }
                    }
                }
            }
            .text{
                padding: 16px;
                margin-top: 14px;
                height: 80px;
                background-color: #111827;
                border-radius: 8px;
                h4{
                    margin: 0;
                }
                p{
                    line-height: 30px;
                    font-size: 14px;
                    color: #9ca3af;
                }
            }
        }
        .recommendT {
            padding-bottom: 50px;
            margin-top: 20px;
            h3{
                font-size: 16px;
                margin-bottom: 16px;
            }
            .box{
                display: flex;
                flex-wrap: wrap;
                gap: 23px;
                li{
                    transition: all 0.3s ease;
                    display: flex;
                    padding: 16px;
                    width: 49.2%;
                    height: 164px;
                    background-color: #1f2937;
                    border: 1px solid #374151;
                    border-radius: 12px;
                    &:hover{
                        transform: translateY(-4px);
                        box-shadow: 0 4px 6px -1px #1f2937, 0 2px 4px -2px #1f2937;
                    }
                    img{
                            margin-right: 10px;
                            width: 64px;
                            height: 64px;
                            border-radius: 50%;
                            border: 2px solid #374151;
                    }
                    .text{
                        flex: 1;
                        h3{
                            display: flex;
                            justify-content: space-between;
                            margin-bottom: 0px;
                            font-size: 18px;
                            font-weight: 600;
                            // line-height: 20px;
                            span{
                                padding: 4px 8px;
                                color: #facc15;
                                font-size: 14px;
                                line-height: 20px;
                                background-color: #713f1233;
                                border-radius: 8px;
                                i{
                                    color: #facc15;
                                }
                                .number{
                                    padding: 0;
                                    color: #9ca3af;
                                    font-size: 12px;
                                    font-weight: normal;
                                    background-color: transparent;
                                }
                            }
                        }
                        p{
                            margin-top: 3px;
                            margin-bottom: 12px;
                            color: #9ca3af;
                            font-size: 14px;
                            // line-height: 22px;
                        }
                        .skill{
                            margin-top: 5px;
                            display: flex;
                            gap: 8px;
                                span{
                                // cursor: pointer;
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                padding: 1px 12px 1px;
                                color: #d1d5db;
                                font-size: 12px;
                                background-color: #374151;
                                border-radius: 999px;
                            }
                        }
                        .money{
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            margin-top: 10px;
                            .left{
                                color: #9ca3af;
                                font-size: 14px;
                                span{
                                    font-size: 18px;
                                    font-weight: 700;
                                }
                            }
                            .button{
                                display: flex;
                                gap: 10px;
                                .anniu{
                                    padding: 8px 16px;
                                    border-radius: 8px;
                                    background-color: #374151;
                                    &:hover{
                                        background-color: #4b5563;
                                        cursor: pointer;
                                    }
                                }
                                .consult{
                                    background-color: #3b82f6;
                                    &:hover{
                                        background-color: #2563eb;
                                    }
                                }
                            }
                        }
                    }
                }
                .nogroups{
                    text-align: center;
                    margin-top: 10px;
                    margin-bottom: 65px;
                    padding: 64px 0;
                    width: 100%;
                    height: 244px;
                    background-color: #1f2937;
                    border-radius: 12px;
                    i{
                        color: #4b5563;
                        font-size: 40px;
                        font-weight: 900;
                    }
                    h3{
                        margin-top: 18px;
                        font-size: 18px;
                        font-weight: 600;
                    }
                    p{
                        margin-top: 8px;
                        color: #9ca3af;
                        font-size: 16px;
                    }
                }
            }
            // .footer{
            //     padding: 0 0 10px 0;
            //     display: flex;
            //     height: 50px;
            //     margin-top: 20px;
            //     // margin-bottom: 20px;
            //     .button{
            //         margin: 0 auto;
            //         display: flex;
            //         padding: 8px 24px;
            //         background-color: #374151;
            //         border-radius: 8px;
            //         border: 1px solid #374151;
            //         &:hover{
            //             cursor: pointer;
            //             background-color: #1f2937;
            //         }
            //     }
            // }
        }
    }
    .sun{
        .explore{
            background-color: #f9fafb;
            border: 1px solid #e5e7eb;
            h3,h4{
                color: #111827;
            }
            .input{
                // border: 1px solid #e5e7eb;
                input{
                    background-color: #f9fafb;
                    border-color: #e5e7eb;
                    color: #1f2937;
                }
            }
            .catogory{
                li{
                    color: #4b5563;
                    background-color: #f3f4f6;
                    border: 1px solid #e5e7eb;
                    &:hover{
                        background-color: #e5e7eb;
                    }
                }
            }
            .text{
                background-color: #f9fafb;
                border: 1px solid #e5e7eb;
                p{
                    color: #4b5563;
                }
            }
        }
        .recommendT{
            h3{
                color: #111827;
            }
            .box{
                li{
                    transition: all 0.3s ease;
                    background-color: #f3f4f6;
                    border: 1px solid #e5e7eb;
                    &:hover{
                        transform: translateY(-4px);
                        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
                    }
                    .text{
                        h3{
                            span{
                                color: #ca8a04;
                                background-color: #fefce8;
                                i{
                                    color: #ca8a04;
                                }
                                .number{
                                    color: #6b7280;
                                }
                            }
                        }
                        p{
                            color: #6b7280;
                        }
                        .skill{
                            span{
                                color: #6b7280;
                                background-color: #f3f4f6;
                                border: 1px solid #e5e7eb;
                            }
                        }
                        .money{
                            .left{
                                border: 0px;
                                color: #6b7280;
                                span{
                                    color: #111827;
                                    background-color: transparent;
                                    border: 0px;
                                }
                            }
                            .button{
                                .anniu{
                                    color: #374151;
                                    background-color: #e5e7eb;
                                    &:hover{
                                        background-color: #d1d5db;
                                    }
                                }
                                .consult{
                                    color: #fff;
                                    background-color: #3b82f6;
                                    &:hover{
                                        background-color: #2563eb;
                                    }
                                }
                            }
                        }
                    }
                }
                .nogroups{
                    background-color:#f3f4f6;
                    border: 1px solid #e5e7eb;
                    i{
                        color: #d1d5db;
                    }
                    h3{
                        color: #111827;
                    }
                    p{
                        color: #6b7280;
                    }
                }
            }
            .footer{
                .button{
                    color: #4b5563;
                    background-color: #f3f4f6;
                    border: 1px solid #e5e7eb;
                    &:hover{
                        background-color: #e5e7eb;
                    }
                }
            }
        }
    }
</style>