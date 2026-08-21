<script setup>
import { useCommunityStore } from '../../../stores/community';
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from "element-plus";

const communityStore = useCommunityStore();
const baseUrl = ref(import.meta.env.VITE_API_BASE_URL || '');
const partnerId = ref(null);


// 搜索关键词
const searchKeyWord = ref('');

// 计算属性：过滤小组
const filteredGroups = computed((() => {
    const keyword = searchKeyWord.value.trim().toLowerCase();
    console.log('搜索关键词',communityStore.groups?.items);
    const baseList = communityStore.recommendPartner?.items || [];
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




const isBoundArr = ref(new Array(filteredGroups.value.length).fill(false))

const toggleBind = async(index,id) => {
    isBoundArr.value[index] = !isBoundArr.value[index];
    if(isBoundArr.value[index]){
        await communityStore.getchoosePartner(id);
        await communityStore.getMyPartner();
        ElMessage.success('绑定成功');
    }else{
        await communityStore.getDeletePartner(id);
        await communityStore.getMyPartner();
        ElMessage.success('解除绑定成功');
    }
}
console.log(communityStore.recommendPartner?.items);





onMounted(async () => {
    await communityStore.getRecommendPartner();
    await communityStore.getPartnerSkill();
    await communityStore.getMyPartner();
});
</script>

<template>
    <div class="partner">
        <div class="left">
            <h2>我的伙伴</h2>
            <!-- <h3 v-if="!communityStore.myPartner?.items">你还没有伙伴，快去邀请你的伙伴吧！</h3> -->
            <li v-for="i in communityStore.myPartner?.items">
                <img :src="baseUrl + i.avatar_url" alt="">
                <div class="text">
                    <h3>{{ i.name }}</h3>
                    <p>{{ i.profession}}</p>
                    <div class="loading">
                        <div class="bgc" :style="{width: i.learning_progress + '%'}"></div>
                    </div>
                    <p>学习进度: {{i.learning_progress}}%</p>
                </div>
            </li>
        </div>
        <div class="right">
            <div class="new">
                <h2>寻找新伙伴</h2>
                <div class="input">
                    <input v-model="searchKeyWord" type="text" placeholder="搜索职业,技能或姓名..."> <i class="iconfont icon-search1"></i></input>
                </div>
                <p>热门技能: <span v-for="i in communityStore.skillList">{{i.skill}}</span></p>
            </div>
            <div class="recommend">
                <h3>推荐伙伴</h3>
                <div class="box">
                    <li v-for="(i, index) in filteredGroups">
                        <img :src=" baseUrl + i.avatar_url" alt="">
                        <div class="text">
                            <h3>
                                {{ i.name }}
                                <span @click="toggleBind(index,i.id)">{{ isBoundArr[index] ? '解除绑定' : '绑定伙伴' }}</span>
                            </h3>
                            <p>{{ i.profession }}</p>
                            <div class="skill"><span v-for="value in i.tech_stack">{{ value }}</span></div>
                        </div>
                    </li>
                </div>
                <!-- <div class="footer">
                    <div class="button">
                        查看更多伙伴
                    </div>
                </div> -->
            </div>
        </div>
    </div>

</template>

<style lang="scss">
    .partner {
        display: flex;
        padding: 0 16px;
        // height: 520px;
        width: 100%;
        // background-color: pink;
        .left{
            margin-right: 25px;
            padding: 16px;
            width: 32.3%;
            // height: 312px;
            background-color: #1f2937;
            border-radius: 12px;
            h2{
                color: #fff;
                margin-bottom: 16px;
                font-size: 18px;
                line-height: 28px;
            }
            li{
                margin-top: 16px;
                display: flex;
                // justify-content: space-between;
                align-items: center;
                height: 68px;
                width: 100%;
                img{
                    margin-right: 10px;
                    width: 48px;
                    height: 48px;
                    border-radius: 50%;
                    border: 2px solid #374151;
                }
                .text{
                    flex: 1;
                    h3{
                        font-size: 14px;
                        line-height: 20px;
                    }
                    .loading{
                        width: 100%;
                        height: 8px;
                        border-radius: 999px;
                        background-color: #374151;
                        .bgc{
                            width: 100%;
                            height: 100%;
                            background-color: #3b82f6;
                            border-radius: 999px;
                        }
                    }
                    p{
                        color: #9ca3af;
                        font-size: 12px;
                        line-height: 22px;
                    }
                }
            }
        }
        .right{
            min-height: 485px;
            flex: 1;
            display: flex;
            flex-direction: column;
            // background-color: pink;
            .new{
                padding: 16px;
                // height: 165px;
                background-color: #1f2937;
                border-radius: 12px;
                h2{
                    font-size: 18px;
                    line-height: 28px;
                }
                .input{
                    margin-top: 18px;
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
                p{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 8px;
                    margin-top: 15px;
                    font-size: 14px;
                    line-height: 20px;
                    color: #9ca3af;
                    span{
                        cursor: pointer;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        padding: 1px 12px 1px;
                        color: #d1d5db;
                        font-size: 12px;
                        background-color: #374151;
                        border-radius: 999px;
                        &:hover{
                            background-color: #4b5563;
                        }
                    }
                }
            }
            .recommend{
                margin-top: 30px;
                margin-bottom: 30px;
                flex: 1;
                // background-color: pink;
                h3{
                    margin-bottom: 12px;
                    font-size: 16px;
                    font-weight: 500;
                }
                .box{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 15px;
                    // height: 227px;
                    width: 100%;
                    // background-color: pink;
                    li{
                        display: flex;
                        padding: 16px;
                        width: 49%;
                        height: 105px;
                        border-radius: 12px;
                        background-color: #1f2937;
                        border: 1px solid #374151;
                        img{
                            margin-right: 10px;
                            width: 56px;
                            height: 56px;
                            border-radius: 50%;
                            border: 2px solid #374151;
                        }
                        .text{
                            flex: 1;
                            h3{
                                display: flex;
                                justify-content: space-between;
                                margin-bottom: 0px;
                                font-size: 16px;
                                // line-height: 20px;
                                span{
                                    color: #3b82f6;
                                    font-size: 14px;
                                    &:hover{
                                        color: #2563eb;
                                        cursor: pointer;
                                    }
                                }
                            }
                            p{
                                margin-bottom: 8px;
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
                        }
                    }
                }
                .footer{
                    display: flex;
                    margin-top: 10px;
                    .button{
                        margin: 0 auto;
                        display: flex;
                        padding: 8px 24px;
                        background-color: #374151;
                        border-radius: 8px;
                        border: 1px solid #374151;
                        &:hover{
                            cursor: pointer;
                            background-color: #1f2937;
                        }
                    }
                }
            }
        }
    }
    .sun{
        .left{
            background-color: #f3f4f6;
            border: 1px solid #e5e7eb;
            h2{
                color: #111827;
            }
            h3{
                color: #1f2937;
            }
            li{
                .text{
                    h3{
                        color: #111827;
                    }
                    p{
                        color: #6b7280;
                    }
                }
            }
        }
        .right{
            .new{
                background-color: #f3f4f6;
                border: 1px solid #e5e7eb;
                h2{
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
                p{
                    color: #6b7280;
                    span{
                        color: #6b7280;
                        border: 1px solid #e5e7eb;
                        background-color: #f9fafb;
                        &:hover{
                            color: #4b5563;
                            background-color: #e5e7eb;
                        }
                    }
                }
            }
            .recommend{
                h3{
                    color: #111827;
                }
                .box{
                    li{
                        background-color: #f9fafb;
                        border: 1px solid #e5e7eb;
                        .text{
                            h3{
                                color: #111827;
                            }
                            p{
                                color: #6b7280;
                            }
                            .skill{
                                span{
                                    color: #4b5563;
                                    border: 1px solid #e5e7eb;
                                    background-color: #f3f4f6;
                                }
                            }
                        }
                    }
                }
                // .footer{
                //     .button{
                //         color: #4b5563;
                //         background-color: #f3f4f6;
                //         border: 1px solid #e5e7eb;
                //         &:hover{
                //             background-color: #e5e7eb;
                //         }
                //     }
                // }
            }
        }
    }
</style>