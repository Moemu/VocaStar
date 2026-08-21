<script setup>
import { useCommunityStore } from '../../../stores/community';
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
const router = useRouter();
const communityStore = useCommunityStore();
const id = ref(0);
const baseUrl = ref(import.meta.env.VITE_API_BASE_URL || '');

console.log(communityStore.groupsCategory);
// 搜索关键词
const searchKeyWord = ref('');

// 计算属性：过滤小组
const filteredGroups = computed((() => {
    const keyword = searchKeyWord.value.trim().toLowerCase();
    console.log('搜索关键词',communityStore.groups?.items);
    const baseList = id.value === 0 ? communityStore.groups?.items || [] : [communityStore.groups?.items[6-id.value]]?.filter(Boolean) || [];
    const validList = baseList.filter(item => {
        return item && item.category;
    });

    if(!keyword){
        return baseList;
    }

    return validList.filter(item => {
        return( item.title.toLowerCase().includes(keyword) || item.category.name.toLowerCase().includes(keyword));
    })
}))





onMounted(async () => {await communityStore.getGroupsCategory() , await communityStore.getGroups()})
</script>

<template>
    <div class="study">
        <div class="explore">
            <div class="input">
                <input type="text" placeholder="搜索学习小组..." v-model="searchKeyWord"> <i class="iconfont icon-search1"></i></input>
            </div>
            <div class="catogory">
                <li @click ="id = 0":class="{ 'active': id == 0 }">全部</li>
                <li  v-for="(i) in communityStore.groupsCategory?.items" @click="id = i.id" :class="{ 'active': id == i.id }">{{ i.name }}</li>
            </div>
        </div>
        <div class="groups">
            <div class="group" v-for="i in filteredGroups" :key="i.id">
                <div class="img">
                    <img :src="baseUrl + i.cover_url" alt="">
                </div>
                <div class="bottom">
                    <h3>{{ i?.title }} <span>{{ i.category?.name }}</span></h3>
                    <p>{{ i?.summary }}</p>
                    <div class="middle">
                        <div class="left number"><i class="iconfont icon-sangeren"></i> {{ i.members_count }} 成员</div>
                        <div class="right number"><i class="iconfont icon-clock"></i>最新: 一天前</div>
                    </div>
                    <div class="button" @click="() => { if(i.category?.name == '前端') router.push('/group') }">
                        加入小组
                    </div>
                </div>
            </div>
            <div class="nogroups" v-if="!filteredGroups.length">
                <i class="iconfont icon-search"></i>
                <h3>未找到匹配的学习小组</h3>
                <p>尝试调整搜索条件或浏览其他分类</p>
            </div>
        </div>
    </div>

</template>

<style lang="scss">
    .study{
        padding: 0 16px;
        width: 100%;
        // height: 500px;
        // background-color: pink;
        .explore{
            padding: 16px;
            height: 134px;
            background-color: #1f2937;
            border-radius: 12px;
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
        }
        .groups{
            display: flex;
            flex-wrap: wrap;
            gap: 24px;
            margin-top: 24px;
            width: 100%;
            .group{
                transition: all 0.3s ease;
                display: flex;
                flex-direction: column;
                height: 340px;
                width: 32.2%;
                background-color: #1f2937;
                border-radius: 12px;
                &:hover{
                    transform: translateY(-4px);
                }
                .img{
                    height: 160px;
                    width: 100%;
                    border-radius: 12px 12px 0 0;
                    img{
                        height: 100%;
                        width: 100%;
                        object-fit: cover;
                        border-radius: 12px 12px 0 0;
                    }
                }
                .bottom{
                    flex : 1;
                    padding: 16px;
                    // background-color: pink;
                    border-radius: 0 0 12px 12px;
                    h3{
                        display: flex;
                        justify-content: space-between;
                        font-size: 18px;
                        font-weight: 600;
                        line-height: 28px;
                        span{
                            padding: 1px 8px;
                            color: #d1d5db;
                            font-size: 12px;
                            background-color: #374151;
                            border-radius: 999px;
                        }
                    }
                    p{
                        margin-top: 8px;
                        color: #9ca3af;
                        font-size: 14px;
                        line-height: 20px;
                    }
                    .middle{
                        margin-top: 18px;
                        display: flex;
                        justify-content: space-between;
                        .number{
                            font-size: 12px;
                            line-height: 16px;
                            color: #9ca3af;
                            i{
                                color: #9ca3af;
                            }
                        }
                    }
                    .button{
                        margin-top: 20px;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        padding: 8px 16px;
                        width: 100%;
                        font-size: 14px;
                        font-weight: 500;
                        background-color: #3b82f6;
                        border-radius: 8px;
                        &:hover{
                            cursor: pointer;
                            background-color: #2563eb;
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
    }
    .sun{
        .explore{
            background-color: #f9fafb;
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
        }
        .groups{
            .group{
                background-color: #f3f4f6;
                border: 1px solid #e5e7eb;
                .bottom{
                    h3{
                        color: #111827;
                        span{
                            color: #4b5563;
                            border: 1px solid #e5e7eb;
                            background-color: #f3f4f6;
                        }
                    }
                    p{
                        color: #6b7280;
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
    }
</style>