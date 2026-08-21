<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useGroupStore } from '../../stores/group'
import { ElMessage } from "element-plus";

const groupStore = useGroupStore();
const baseUrl = ref(import.meta.env.VITE_API_BASE_URL || '');

const menuId = ref(0);
const islianjie = ref(false);
const isDianzan = ref(false);
const iscomment = ref(false);
const secondDz = ref(false);

// 菜单切换到对应的位置
const activeRef = ref(null);
const stutyRef = ref(null);
const memberRef = ref(null);
const taskRef = ref(null);

const scrollToSection = (ref) => {
    const targetTop = ref.value.offsetTop;
    window.scrollTo({ top: targetTop-130, behavior:'smooth' });
}

const changeMenu = (index,ref) => {
    menuId.value = index;
    scrollToSection(ref);
}

const isJoin = ref(false)
const joinGroup = () => {
    if(!isJoin.value){
        groupStore.joinGroup(1);
        isJoin.value = true;
        ElMessage.success('加入小组成功');
    }else{
        groupStore.leaveGroup(1);
        isJoin.value = false;
        ElMessage.success('退出小组成功');
    }
}

const activeTitle = ref('');
const activeContent = ref('');
const attachments = ref([]);
const linkUrl = ref('');
const linkTitle = ref('');

const publishActive = async () => {
    if(!activeTitle.value || !activeContent.value) {
        ElMessage.error('标题和内容不能为空');
        return;
    }
    await groupStore.createActive({
        group_id: 1,
        title: activeTitle.value,
        content: activeContent.value,
        attachments: attachments.value,
    });

    await groupStore.getCommunityActive();

    ElMessage.success('发布成功');
    activeTitle.value = '';
    activeContent.value = '';
    attachments.value = [];
    linkUrl.value = '';
    linkTitle.value = '';
    islianjie.value = false;
}

const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if(file) {
        attachments.value.push({
            type: 'image',
            url: URL.createObjectURL(file),
            title: file.name,
            file_size: file.size,
        });
        linkUrl.value = '';
        linkTitle.value = '';
        islianjie.value = false;
    }
}

const addLink =() => {
    if(linkUrl.value){
        attachments.value.push({
            type: 'url',
            url: linkUrl.value,
            title: linkTitle.value || '未命名链接',
            file_size: null,
        })
    }
}


//滚动监听，自动切换菜单
const handleScroll = () => {
    const scrollY = window.scrollY+130;//视口偏移
    const sections = [activeRef, stutyRef, memberRef, taskRef];

    sections.forEach((ref, index) => {
        if(ref.value){
            const sectionTop = ref.value.offsetTop;
            const sectionBottom = sectionTop + ref.value.offsetHeight;

            if(scrollY >= sectionTop && scrollY < sectionBottom){
                menuId.value = index;
            }
        }
    })
}

onMounted(async () => {
    window.addEventListener('scroll', handleScroll);
    await groupStore.getGroupDetail(1);
    await groupStore.getGroupMembers(1);
    await groupStore.getCommunityActive();
});

onUnmounted(() => {
    window.removeEventListener('scroll', handleScroll);
});


const menuList = [
    {iconfont: 'iconfont icon-shouye-shouye',  title: '首页动态',ref: activeRef},
    {iconfont: 'iconfont icon-xuexi_nor', title: '学习资料', ref: stutyRef},
    {iconfont: 'iconfont icon-sangeren', title: '成员列表', ref: memberRef},
    {iconfont: 'iconfont icon-liebiao', title: '作业任务', ref: taskRef}
]
</script>

<template>
    <div class="group">
        <div class="header">
            <div class="top">
                <div class="left">
                    <h1>前端开发学习小组</h1>
                    <p>前端</p>
                </div>
                <div class="right">
                    <div class="tubiao">
                        <i class="iconfont icon-JC_054"></i>
                    </div>
                    <div class="tubiao">
                        <i class="iconfont icon-heart-fill"></i>
                    </div>
                    <div class="button" @click="joinGroup()" :class="{active: isJoin}">
                        加入小组
                    </div>
                </div>
            </div>
            <div class="menu">
                <li v-for="(i,index) in menuList" @click="changeMenu(index,i.ref)" :class="{ active : index == menuId}"><i :class="i.iconfont"></i> {{ i.title }}</li>
            </div>
        </div>
        <div class="main">
            <div class="blank"></div>
            <div class="img">
                <img :src="baseUrl + groupStore.detailGroup?.cover_url" alt="">
            </div>
            <div class="jieshao">
                <h2>{{ groupStore.detailGroup?.title }}</h2>
                <p>{{ groupStore.detailGroup?.summary }}</p>
                <div class="skill">
                    <span><i class="iconfont icon-sangeren"></i> {{groupStore.detailGroup?.members_count}}成员</span>
                    <span class="time"><i class="iconfont icon-shijian"></i> 最近: {{ groupStore.detailGroup?.last_activity_at }}</span>
                    <span class="life"><i class="iconfont icon-redu"></i> 高活跃度</span>
                </div>
            </div>
            <div class="content">
                <div class="left">
                    <div class="xiangqing">
                        <h3><i class="iconfont icon-gantanhaozhong"></i> 小组详情</h3>
                        <div class="time">
                            <p>创建时间</p>
                            <span>{{ groupStore.detailGroup?.meta?.created_at }}</span>
                        </div>
                        <div class="captain">
                            <p>组长信息</p>
                            <div class="text">
                                <img :src="baseUrl + groupStore.detailGroup?.meta?.owner?.avatar_url" alt="">
                                <div class="wenzi">
                                    {{ groupStore.detailGroup?.meta?.owner?.name }}
                                    <p>组长</p>
                                </div>
                            </div>
                        </div>
                        <div class="catogory">
                            <p>小组分类</p>
                            {{ groupStore.detailGroup?.meta?.category.name }}
                        </div>
                    </div>
                    <div class="rule">
                        <h3><i class="iconfont icon-a-shenpanchuizi"></i> 小组规则</h3>
                        <li v-for="i in groupStore.detailGroup?.rules"><i class="iconfont icon-dui"></i><p>{{ i }}</p></li>
                    </div>
                    <div class="member">
                        <h3><i class="iconfont icon-xiangmujingli"></i>热门成员</h3>
                        <div class="content">
                            <li v-for="i in groupStore.membersList?.items?.slice(0,6)">
                                <img :src="baseUrl + i.avatar_url" alt="">
                                <p>{{ i.username }}</p>
                                <span>{{ i.role }}</span>
                            </li>
                        </div>
                    </div>
                    <div class="allmb" ref="memberRef">
                        <h3>
                            <div class="text"><i class="iconfont icon-sangeren"></i> 所有成员 (128)</div>
                            <div class="shousuo">
                                <div class="input">
                                    <input type="text" placeholder="搜索成员..."> <i class="iconfont icon-search1"></i></input>
                                </div>
                            </div>
                        </h3>
                        <div class="membership">
                            <li v-for="i in groupStore.membersList?.items">
                                <img :src=" baseUrl + i.avatar_url" alt="">
                                <div class="text">
                                    <p>{{ i.username }}</p>
                                    <span>{{ i.role }}</span>
                                </div>
                            </li>
                        </div>
                    </div>
                </div>
                <div class="right">
                    <div class="dynamic" ref="activeRef">
                        <h3>首页动态 <div class="button"><span>最新发布</span><span>最热内容</span></div></h3>
                        <div class="comment">
                            <img src="https://space.coze.cn/api/coze_space/gen_image?image_size=square&prompt=User%20Avatar&sign=f1f81b57b203e2aa336aa3ec3f6e3f7f" alt="">
                            <div class="text">
                                <div class="input">
                                    <input type="text" placeholder="添加标题..." v-model="activeTitle"></input>
                                    <textarea class="textarea" placeholder="分享你的想法,问题或经验..." v-model="activeContent"></textarea>
                                </div>
                                <div class="lianjie" v-if="islianjie">
                                    <input type="text" placeholder="输入链接地址..." v-model="linkUrl"></input>
                                    <input type="text" placeholder="链接名称 (可选) ..." v-model="linkTitle"></input>
                                    <div class="button" @click="islianjie = !islianjie"><span>取消</span><span class="submit" @click="addLink">添加</span></div>
                                </div>
                                <div class="shangchuang">
                                    <div class="tubiao">
                                        <!-- 图片上传 -->
                                        <label for="image-upload" class="image">
                                            <i class="iconfont icon-shangchuantupian"></i>
                                        </label>
                                        <input type="file" id="image-upload" accept="image/*" hidden @click="handleImageUpload">
                                        <!-- 链接上传 -->
                                        <i class="iconfont icon-lianjie" @click="islianjie = !islianjie"></i>
                                        <!-- 文件上传 -->
                                        <label for="file-upload">
                                            <i class="iconfont icon-wenjian"></i>
                                        </label>
                                        <input type="file" id="file-upload" accept=".pdf,.doc" hidden>
                                    </div>
                                    <span @click="publishActive()">发布</span>
                                </div>
                            </div>
                        </div>
                        <div class="comment-text" v-for="i in groupStore.communityActive?.items">
                            <div class="top">
                                <img :src="baseUrl + i.author.avatar_url" alt="">
                                <div class="text">
                                    {{ i.author.username }}
                                    <span>{{ i.created_at }}</span>
                                </div>
                            </div>
                            <h4>{{ i.title }}</h4>
                            <p>{{ i.content }}</p>
                            <div class="type" v-for="value in i.attachments">
                                <div class="tupian" v-if="value.type == 'image'" >
                                    <img :src="value.url" alt="">
                                </div>
                                <div class="wangzhi" v-if-else="value.type == 'url'">
                                    <a :href="value.url" target="_blank">
                                        <div class="tubiao">
                                            <i class="iconfont icon-lianjie"></i>
                                        </div>
                                        <div class="wenzi"><p>{{ value.title }}</p><span>{{ value.url }}</span></div>
                                    </a>
                                </div>
                            </div>
                            <div class="dianzhan">
                                <span class="first" @click="isDianzan = !isDianzan" :class="{ active : isDianzan}" ><i class="iconfont icon-dianzan"></i> {{ i.likes_count}}</span>
                                <span @click="iscomment = !iscomment"><i class="iconfont icon-biaoqiankuozhan_luntan-328"> {{ i.comments.length + 1 }}</i></span>
                            </div>
                            <div class="second-comment" v-if="iscomment">
                                <li v-for="value in 1">
                                    <img src="https://space.coze.cn/api/coze_space/gen_image?image_size=square&prompt=Female%20Frontend%20Developer%20Avatar%20Asian&sign=5c5260bb2c04d8a8a7f1883bfc93e7e5" alt="">
                                    <div class="neiron">
                                        <p>李华 <span>1小时前</span></p>
                                        <span>感谢分享！我最近也在研究React 18，自动批处理这个特性确实很实用。</span>
                                        <div class="second-dz">
                                            <span class="first" @click="secondDz = !secondDz" :class="{ active : secondDz}" ><i class="iconfont icon-dianzan"></i> 24</span>
                                            <span>回复</span>
                                        </div>
                                    </div>
                                </li>
                                <div class="pinglun">
                                    <img src="https://space.coze.cn/api/coze_space/gen_image?image_size=square&prompt=User%20Avatar&sign=f1f81b57b203e2aa336aa3ec3f6e3f7f" alt="">
                                    <input type="text" placeholder="写下你的评论..."></input>
                                    <div class="button">
                                        发送
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="button3">
                            <div class="anniu">
                                加载更多
                            </div>
                        </div>
                    </div>
                    <div class="database" ref="stutyRef">
                        <h3>资料库</h3>
                        <div class="catogory1">
                            <li v-for="value in 10">全部</li>
                        </div>
                        <div class="wenjian" v-for="value in 5">
                            <li>
                                <div class="tubiao">
                                    <i class="iconfont icon-lianjie"></i>
                                </div>
                                <div class="wenzi"><p>React 18官方发布说明</p>
                                    <span>450MB</span><span>1周前</span><span>下载 90</span>
                                </div>
                            </li>
                        </div>
                        <div class="button4">
                            <div class="anniu">
                                查看全部资料
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

</template>

<style lang="scss">
    .group {
        position: relative;
        .header{
            display: flex;
            flex-direction: column;
            position: fixed;
            top: 0;
            left: 0;
            z-index: 1000;
            width: 100%;
            // padding: 0 16px;
            height: 123px;
            background-color: #1f2937;
            border: 1px solid #374151;
            .top{
                display: flex;
                justify-content: space-between;
                padding: 12px 16px;
                height: 72px;
                border-bottom: 1px solid #374151;
                .left{
                    h1{
                        color: #60a5fa;
                        font-size: 20px;
                        line-height: 28px;
                        font-weight: 700;
                    }
                    p{
                        color: #9ca3af;
                        font-size: 14px;
                        line-height: 20px;
                    }
                }
                .right{
                    height: 40px;
                    display: flex;
                    gap: 10px;
                    .tubiao{
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        width: 40px;
                        // padding: 10px;
                        border-radius: 999px;
                        background-color: #4b5563;
                        &:hover{
                            background-color: #374151;
                            cursor: pointer;
                        }
                    }
                    .button{
                        transition: all 0.3s ease;
                        padding: 8px 16px;
                        border-radius: 8px;
                        background-color: #3b82f6;
                        &:hover{
                            background-color: #2563eb;
                            transform: translateY(-4px);
                            cursor: pointer;
                        }
                        &.active{
                            background-color: #ef4444;
                        }
                    }
                }
            }
            .menu{
                display: flex;
                gap: 20px;
                flex: 1;
                padding: 0 16px;
                li{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    color: #9ca3af;
                    font-size: 16px;
                    &:hover{
                        color: #fff;
                        cursor: pointer;
                        i{
                            color: #fff;
                        }
                    }
                    i{
                        margin-right: 5px;
                        color: #9ca3af;
                        font-size: 18px;
                    }
                    &.active{
                        color: #60a5fa;
                        border-bottom: 2px solid #60a5fa;
                        i{
                            color: #60a5fa;
                        }
                    }
                }
            }
        }
        .main{
            // display: flex;
            // flex-direction: column;
            padding: 0 16px 0;
            width: 100%;
            // height: 500px;
            background-color: #111827;
            .blank{
                height: 148px;
            }
            .img{
                height: 256px;
                border-radius: 12px;
                img{
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    border-radius: 12px;
                }
            }
            .jieshao{
                margin-top: 24px;
                padding: 24px;
                height: 156px;
                border-radius: 12px;
                background-color: #1f2937;
                h2{
                    margin-bottom: 10px;
                    color: #60a5fa;
                    font-size: 24px;
                    line-height: 32px;
                    font-weight: 700;
                }
                p{
                    color: #d1d5db;
                    font-size: 16px;
                    margin-bottom: 16px;
                }
                .skill{
                    display: flex;
                    gap: 15px;
                    span{
                        padding: 4px 6px;
                        border-radius: 999px;
                        color: #60a5fa;
                        background-color: #1e3a8a4d;
                        i{
                            color: #60a5fa;
                        }
                    }
                    .time{
                        color: #4ade80;
                        background-color: #14532d4d;
                        i{
                            color: #4ade80;
                        }
                    }
                    .life{
                        color: #c084fc;
                        background-color: #581c874d;
                        i{
                            color: #c084fc;
                        }
                    }
                }
            }
            .content{
                display: flex;
                gap: 24px;
                margin-top: 30px;
                .left{
                    width: 32%;
                    // background-color: pink;
                    .xiangqing{
                        padding: 24px;
                        height: 309px;
                        background-color: #1f2937;
                        border-radius: 12px;
                        h3{
                            display: flex;
                            font-size: 18px;
                            font-weight: 700;
                            color: #60a5fa;
                            i{
                                margin-right: 5px;
                                padding-top: 2.5px;
                                color: #60a5fa;
                                font-size: 25px;
                            }
                        }
                        .time{
                            margin-top: 18px;
                            p{
                                margin-bottom: 4px;
                                color: #9ca3af;
                                font-size: 14px;
                                line-height: 20px;
                            }
                            span{
                                font-size: 16px;
                            }
                        }
                        .captain{
                            margin-top: 17px;
                            padding-top: 15px;
                            border-top: 1px solid #374151;
                            p{
                                color: #9ca3af;
                                font-size: 14px;
                            }
                            .text{
                                display: flex;
                                margin-top: 4px;
                                img{
                                    width: 40px;
                                    height: 40px;
                                    border-radius: 50%;
                                    margin-right: 10px;
                                }
                                .wenzi{
                                    p{
                                        font-size: 12px;
                                    }
                                }
                            }
                        }
                        .catogory{
                            margin-top: 17px;
                            padding-top: 15px;
                            font-size: 16px;
                            border-top: 1px solid #374151;
                            p{
                                margin-bottom: 4px;
                                color: #9ca3af;
                                font-size: 14px;
                            }
                        }
                    }
                    .rule{
                        margin-top: 30px;
                        padding: 24px;
                        width: 100%;
                        height: 260px;
                        background-color: #1f2937;
                        border-radius: 12px;
                        h3{
                            margin-bottom: 18px;
                            display: flex;
                            font-size: 18px;
                            font-weight: 700;
                            color: #60a5fa;
                            i{
                                margin-right: 5px;
                                padding-top: 2.5px;
                                color: #60a5fa;
                                font-size: 25px;
                            }
                        }
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
                    .member{
                        margin-top: 30px;
                        padding: 24px;
                        width: 100%;
                        height: 308px;
                        background-color: #1f2937;
                        border-radius: 12px;
                        h3{
                            margin-bottom: 18px;
                            display: flex;
                            font-size: 18px;
                            font-weight: 700;
                            color: #60a5fa;
                            i{
                                margin-right: 5px;
                                padding-top: 2.5px;
                                color: #60a5fa;
                                font-size: 25px;
                            }
                        }
                        .content{
                            display: flex;
                            flex-wrap: wrap;
                            gap: 10px;
                            // justify-content: space-between;
                            li{
                                text-align: center;
                                height: 100px;
                                width: 31.5%;
                                // background-color: pink;
                                img{
                                    // margin-bottom: 10px;
                                    width: 56px;
                                    height: 56px;
                                    border-radius: 50%;
                                    border: 2px solid #374151;
                                }
                                p{
                                    margin-top: 8px;
                                    font-size: 14px;
                                    line-height: 10px;
                                }
                                span{
                                    margin: 0;
                                    color: #9ca3af;
                                    font-size: 12px;
                                    line-height: 16px;
                                }
                            }
                        }
                    }
                    .allmb{
                        margin-top: 30px;
                        padding: 24px;
                        width: 100%;
                        height: 485px;
                        background-color: #1f2937;
                        border-radius: 12px;
                        h3{
                            margin-bottom: 18px;
                            display: flex;
                            justify-content: space-between;
                            font-size: 18px;
                            font-weight: 700;
                            color: #60a5fa;
                            .text{
                                font-size: 18px;
                                font-weight: 700;
                                color: #60a5fa;
                                i{
                                    margin-right: 5px;
                                    padding-top: 2.5px;
                                    color: #60a5fa;
                                    font-size: 25px;
                                }
                            }
                            .shousuo{
                                .input{
                                    width: 144px;
                                    position: relative;
                                    input{
                                        padding-left: 27px;
                                        width: 100%;
                                        height: 30px;
                                        color: #9ca3af;
                                        font-size: 12px;
                                        font-weight: 500;
                                        border-radius: 8px;
                                        background-color: #111827;
                                        border: 1px solid #374151;
                                        &:focus{
                                            box-shadow: 0 0 0 calc(0.5px + 0.5px) rgb(59 130 246 / 1);
                                            border: 0px;
                                            outline: transparent;
                                        }
                                    }
                                    i{
                                        position: absolute;
                                        top: 8px;
                                        left: 8px;
                                        font-size: 16px;
                                        font-weight: 700;
                                        color: #9ca3af;
                                    }
                                }
                            }
                        }
                        .membership{
                            overflow-y: auto;
                            height: 400px;
                            li{
                                margin-bottom: 10px;
                                display: flex;
                                height: 56px;
                                padding: 8px;
                                // background-color: pink;
                                border-radius: 8px;
                                img{
                                    margin-right: 10px;
                                    width: 40px;
                                    height: 40px;
                                    border-radius: 50%;
                                }
                                .text{
                                    p{
                                    margin-top: 8px;
                                    font-size: 14px;
                                    line-height: 10px;
                                    }
                                    span{
                                        margin: 0;
                                        color: #9ca3af;
                                        font-size: 12px;
                                        line-height: 16px;
                                    }
                                }
                                &:hover{
                                    background-color: #37415180;
                                    cursor: pointer;
                                }
                            }
                        }
                    }
                }
                .right{
                    flex: 1;
                    margin-bottom: 40px;
                    .dynamic{
                        padding: 24px;
                        background-color: #1f2937;
                        border-radius: 12px;
                        h3{
                            margin-bottom: 18px;
                            display: flex;
                            justify-content: space-between;
                            font-size: 18px;
                            font-weight: 700;
                            color: #60a5fa;
                            .button{
                                display: flex;
                                gap: 10px;
                                span{
                                    display: flex;
                                    padding: 6px 12px;
                                    color: #d1d5db;
                                    font-size: 14px;
                                    border-radius: 8px;
                                    background-color: #374151;
                                    cursor: pointer;
                                    &:hover{
                                        background-color: #4b5563;
                                    }
                                    &.active{
                                        color: #60a5fa;
                                        background-color: #1e3a8a4d;
                                    }
                                }
                            }
                        }
                        .comment{
                            display: flex;
                            margin: 24px 0;
                            padding: 16px;
                            // height: 240px;
                            background-color: #37415180;
                            border-radius: 8px;
                            img{
                                width: 40px;
                                height: 40px;
                                border-radius: 50%;
                                margin-right: 10px;
                            }
                            .text{
                                flex: 1;
                                .input{
                                    position: relative;
                                    input{
                                        padding: 12px;
                                        width: 100%;
                                        height: 50px;
                                        color: #9ca3af;
                                        font-size: 16px;
                                        font-weight: 500;
                                        border-radius: 8px;
                                        background-color: #1f2937;
                                        border: 1px solid #4b5563;
                                        &:focus{
                                            box-shadow: 0 0 0 calc(1px + 1px) rgb(59 130 246 / 1);
                                            border: 0px;
                                            outline: transparent;
                                        }
                                        &::placeholder{
                                            color: #9ca3af;
                                            font-weight: 500;
                                            font-size: 16px;
                                        }
                                    }
                                    .textarea{
                                        // vertical-align: top;
                                        resize: none;
                                        margin-top: 15px;
                                        height: 97px;
                                        padding: 12px;
                                        width: 100%;
                                        color: #9ca3af;
                                        font-size: 16px;
                                        font-weight: 500;
                                        border-radius: 8px;
                                        background-color: #1f2937;
                                        border: 1px solid #4b5563;
                                        &:focus{
                                            box-shadow: 0 0 0 calc(1px + 1px) rgb(59 130 246 / 1);
                                            border: 0px;
                                            outline: transparent;
                                        }
                                        &::placeholder{
                                            color: #9ca3af;
                                            font-weight: 700;
                                            font-size: 16px;
                                        }
                                    }
                                }
                                .lianjie{
                                    margin-top: 15px;
                                    input{
                                        margin: 0 0 10px 0;
                                        padding: 12px;
                                        width: 100%;
                                        height: 50px;
                                        color: #9ca3af;
                                        font-size: 16px;
                                        font-weight: 500;
                                        border-radius: 8px;
                                        background-color: #1f2937;
                                        border: 1px solid #4b5563;
                                        &:focus{
                                            box-shadow: 0 0 0 calc(1px + 1px) rgb(59 130 246 / 1);
                                            border: 0px;
                                            outline: transparent;
                                        }
                                        &::placeholder{
                                            color: #9ca3af;
                                            font-weight: 500;
                                            font-size: 16px;
                                        }
                                    }
                                    .button{
                                        display: flex;
                                        justify-content: end;
                                        gap: 10px;
                                        span{
                                            display: flex;
                                            padding: 6px 12px;
                                            color: #d1d5db;
                                            font-size: 14px;
                                            border-radius: 8px;
                                            background-color: #374151;
                                            cursor: pointer;
                                            &:hover{
                                                background-color: #4b5563;
                                            }
                                            &.active{
                                                color: #60a5fa;
                                                background-color: #1e3a8a4d;
                                            }
                                        }
                                        .submit{
                                            background: #3b82f6;
                                            &:hover{
                                                background-color: #2563eb;
                                            }
                                        }
                                    }
                                }
                                .shangchuang{
                                    display: flex;
                                    justify-content: space-between;
                                    margin-top: 12px;
                                    .tubiao{
                                        i{
                                            margin-right: 15px;
                                            color: #9ca3af;
                                            font-size: 18px;
                                            &:hover{
                                                color: #fff;
                                                cursor: pointer;
                                            }
                                        }
                                    }
                                    span{
                                        display: flex;
                                        padding: 6px 12px;
                                        color: #d1d5db;
                                        font-size: 14px;
                                        border-radius: 8px;
                                        background-color: #374151;
                                        cursor: pointer;
                                        &:hover{
                                            background-color: #4b5563;
                                        }
                                        &.active{
                                            color: #60a5fa;
                                            background-color: #1e3a8a4d;
                                        }
                                    }
                                }
                            }
                        }
                        .comment-text{
                            padding-bottom: 20px;
                            border-bottom: 1px solid #37415180;
                            margin-top: 24px;
                            .top{
                                display: flex;
                                img{
                                    width: 36px;
                                    height: 36px;
                                    border-radius: 50%;
                                    margin-right: 10px;
                                    border: 2px solid #374151;
                                }
                                .text{
                                    span{
                                        margin-left: 5px;
                                        color: #9ca3af;
                                        font-size: 12px;
                                    }
                                }
                            }
                            h4{
                                margin-top: 15px;
                                margin-bottom: 12px;
                                font-size: 18px;
                                font-weight: 700;
                                line-height: 28px;
                            }
                            p{
                                color: #d1d5db;
                                font-size: 16px;
                            }
                            .tupian{
                                margin-top: 20px;
                                display: flex;
                                justify-content: center;
                                padding: 5px 0;
                                height: 272px;
                                background-color: #37415180;
                                border-radius: 8px;
                                img{
                                    width: 50%;
                                    height: 100%;
                                }
                            }
                            .wangzhi{
                                padding: 8px;
                                margin-top: 16px;
                                height: 80px;
                                background-color: #37415180;
                                border-radius: 8px;
                                a{
                                    padding: 12px;
                                    display: flex;
                                    align-items: center;
                                    background-color: #1e3a8a33;
                                    width: 100%;
                                    height: 100%;
                                    .tubiao{
                                        display: flex;
                                        justify-content: center;
                                        align-items: center;
                                        margin-right: 10px;
                                        width: 40px;
                                        height: 40px;
                                        background-color: #1e3a8a4d;
                                        border-radius: 4px;
                                        i{
                                            color: #60a5fa;
                                            font-size: 18px;
                                        }
                                    }
                                    .wenzi{
                                        p{
                                            font-size: 16px;
                                        }
                                        span{
                                            font-size: 12px;
                                            color: #60a5fa;
                                        }
                                    }
                                }
                            }
                            .dianzhan{
                                margin-top: 10px;
                                span{
                                    margin-right: 20px;
                                    color: #9ca3af;
                                    font-size: 16px;
                                    i{
                                        color: #9ca3af;
                                        font-size: 18px;
                                    }
                                    &:hover{
                                        cursor: pointer;
                                        color: #60a5fa;
                                        i{
                                            color: #60a5fa;
                                        }
                                    }
                                }
                                .first{
                                    transition: all 0.3s ease;
                                    &:active{
                                        transform: scale(1.04);
                                    }
                                    &.active{
                                        color: #f87171;
                                        i{
                                            color: #f87171;
                                        }
                                    }
                                }
                            }
                            .second-comment{
                                margin-top: 20px;
                                li{
                                    margin-bottom: 25px;
                                    display: flex;
                                    height: 92px;
                                    img{
                                        margin-right: 10px;
                                        width: 28px;
                                        height: 28px;
                                        border-radius: 50%;
                                        border: 2px solid #374151;
                                    }
                                    .neiron{
                                        padding: 12px;
                                        flex: 1;
                                        background-color: #37415180;
                                        border-radius: 8px;
                                        p{
                                            display: flex;
                                            justify-content: space-between;
                                            color: #fff;
                                            font-size: 14px;
                                            line-height: 20px;
                                            span{
                                                color: #9ca3af;
                                                font-size: 12px;
                                            }
                                        }
                                        span{
                                            margin-top: 2px;
                                            color: #d1d5db;
                                            font-size: 14px;
                                        }
                                        .second-dz{
                                            margin-top: 5px;
                                            span{
                                                margin-right: 20px;
                                                color: #9ca3af;
                                                font-size: 12px;
                                                i{
                                                    color: #9ca3af;
                                                    font-size: 14px;
                                                }
                                                &:hover{
                                                    cursor: pointer;
                                                    color: #60a5fa;
                                                    i{
                                                        color: #60a5fa;
                                                    }
                                                }
                                            }
                                            .first{
                                                transition: all 0.3s ease;
                                                &:active{
                                                    transform: scale(1.04);
                                                }
                                                &.active{
                                                    color: #f87171;
                                                    i{
                                                        color: #f87171;
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                                .pinglun{
                                    display: flex;
                                    justify-content: space-between;
                                    img{
                                        width: 28px;
                                        height: 28px;
                                        border-radius: 50%;
                                        border: 2px solid #374151;
                                    }
                                    input{
                                        padding: 12px;
                                        width: 90%;
                                        height: 38px;
                                        color: #9ca3af;
                                        font-size: 16px;
                                        font-weight: 500;
                                        border-radius: 8px;
                                        background-color: #1f2937;
                                        border: 1px solid #4b5563;
                                        &:focus{
                                            box-shadow: 0 0 0 calc(1px + 1px) rgb(59 130 246 / 1);
                                            border: 0px;
                                            outline: transparent;
                                        }
                                        &::placeholder{
                                            color: #9ca3af;
                                            font-weight: 500;
                                            font-size: 16px;
                                        }
                                    }
                                    .button{
                                        padding: 0 12px;
                                        display: flex;
                                        justify-content: center;
                                        align-items: center;
                                        background-color: #374151;
                                        border-radius: 4px;
                                        cursor: pointer;
                                        &:hover{
                                            background-color: #4b5563;
                                        }
                                        &.active{
                                            color: #60a5fa;
                                            background-color: #1e3a8a4d;
                                        }
                                    }
                                }
                            }
                        }
                        .button3{
                            margin-top: 30px;
                            display: flex;
                            .anniu{
                                margin: 0 auto;
                                padding: 8px 16px;
                                background-color: #4b5563;
                                border-radius: 8px;
                                &:hover{
                                    background-color: #374151;
                                    cursor: pointer;
                                }
                            }
                        }
                    }
                    .database{
                        margin-top: 30px;
                        padding: 24px;
                        background-color: #1f2937;
                        border-radius: 12px;
                        h3{
                            margin-bottom: 18px;
                            display: flex;
                            justify-content: space-between;
                            font-size: 18px;
                            font-weight: 700;
                            color: #60a5fa;
                        }
                        .catogory1{
                            display: flex;
                            gap: 10px;
                            margin-top: 15px;
                            // margin-bottom: 15px;
                            // height: 36px;
                            // background-color: pink;
                            li{
                                margin-bottom: 10px;
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
                            }
                        }
                        .wenjian{
                            padding: 8px;
                            margin-top: 16px;
                            height: 70px;
                            background-color: #37415180;
                            border-radius: 8px;
                            &:hover{
                                cursor: pointer;
                                background-color: #374151;
                            }
                            li{
                                width: 100%;
                                height: 100%;
                                display: flex;
                                align-items: center;
                                .tubiao{
                                    display: flex;
                                    justify-content: center;
                                    align-items: center;
                                    margin-right: 10px;
                                    width: 40px;
                                    height: 40px;
                                    background-color: #1e3a8a4d;
                                    border-radius: 4px;
                                    i{
                                        color: #60a5fa;
                                        font-size: 18px;
                                    }
                                }
                                .wenzi{
                                    p{
                                        font-size: 16px;
                                    }
                                    span{
                                        margin-right: 10px;
                                        font-size: 12px;
                                        color: #9ca3af;
                                    }
                                }
                            }
                        }
                        .button4{
                            margin-top: 30px;
                            display: flex;
                            .anniu{
                                margin: 0 auto;
                                padding: 8px 16px;
                                background-color: #4b5563;
                                border-radius: 8px;
                                &:hover{
                                    background-color: #374151;
                                    cursor: pointer;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
</style>