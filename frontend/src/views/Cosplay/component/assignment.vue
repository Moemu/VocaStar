<script setup>
import { ref } from 'vue'
import { useCosplayStore } from '../../../stores/cosplay';
const CosplayStore = useCosplayStore();
const session_id = ref();
session_id.value = CosplayStore.cosplaySession?.state?.session_id;
const options = ref([]);
// options.value = CosplayStore.cosplaySession?.state?.current_scene?.options;
console.log(options.value);
const option_id = ref('');
const isSubmit = ref(false);
const handle = (id) => {
    option_id.value = id;
    isSubmit.value = true;
}

const submit = async () => {
    console.log(CosplayStore.cosplaySession?.state?.history)
    if(CosplayStore.cosplaySession?.state?.current_scene_index == 3){
        console.log('end');
        await CosplayStore.CosplayChoice({session_id: session_id.value, option_id: option_id.value});
        CosplayStore.component = 'third';
        CosplayStore.session_id = session_id.value;
    }else{
        if(isSubmit.value){
            CosplayStore.lastTitle = CosplayStore.cosplaySession?.state?.current_scene?.title;
            console.log(CosplayStore.lastTitle);
            await CosplayStore.CosplayChoice({session_id: session_id.value, option_id: option_id.value});
            await CosplayStore.CreateCosplay(1);
            console.log(CosplayStore.cosplaySession);
            console.log(CosplayStore.cosplayChoice);
            CosplayStore.component = 'second';
        }
    }
}

</script>

<template>
    <div class="assignment">
        <h2>{{CosplayStore.cosplaySession?.state?.current_scene?.title}}</h2>
        <div class="tiao">
        </div>
        <div class="question">
            {{CosplayStore.cosplaySession?.state?.current_scene?.text}}
        </div>
        <div class="options">
            <div class="option" v-for="i in CosplayStore.cosplaySession?.state?.current_scene?.options" :key="i.id" @click="handle(i.id)" :class="{active: i.id == option_id}">
                {{ i.text }}
            </div>
        </div>
        <div class="submit" @click="submit()" :class="{disabled:!isSubmit}" v-if="CosplayStore.cosplaySession?.state?.current_scene_index < 3">
            提交选择
            <i class="iconfont icon-check"></i>
        </div>
        <div class="submit" @click="submit()" :class="{disabled:!isSubmit}" v-else>
            查看结果
            <i class="iconfont icon-check"></i>
        </div>
    </div>

</template>

<style lang="scss">
    .assignment {
        // text-align: center;
        padding: 32px 16px;
        height: 628px;
        width: 100%;
        h2{
            text-align: center;
            font-size: 24px;
            font-weight: 32px;
        }
        .tiao{
            margin: 5px auto 0;
            // margin-top: 5px;
            width: 80px;
            height: 4px;
            background-image: linear-gradient(to right,#a855f7 , #3b82f6);
            border-radius: 999px;
        }
        .question{
            margin: 30px auto;
            display: flex;
            align-items: center;
            padding: 32px;
            width: 45%;
            // height: 145px;
            font-size: 18px;
            color: #e2e8f0;
            line-height: 30px;
            border-radius: 12px;
            background-color: #1e293b80;
        }
        .options{
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            gap: 20px;
            margin: 0 auto;
            // height: 342px;
            width: 45%;
            .option{
                transition: all 0.3s ease;
                padding: 24px;
                height: 74px;
                background-color: #1e293b4d;
                color: #e2e8f0;
                font-size: 17px;
                border-radius: 12px;
                border: 1px solid #334155;
                &:hover{
                    cursor: pointer;
                    transform: scale(1.02);
                }
                &:active{
                    transform: scale(0.98);
                }
                &.active{
                    border-color: #a855f7;
                    background-color: #9333ea1a;
                }
            }
        }
        .submit{
            transition: all 0.3s ease;
            padding: 12px 32px;
            margin: 35px auto 0;
            width: 10%;
            height: 48px;
            border-radius: 12px;
            font-weight: 700;
            background-image: linear-gradient(to right, #9333ea , #2563eb);
            cursor: not-allowed;
            &:hover{
                background-image: linear-gradient(to right, #7e22ce , #1d4ed8);
                transform: scale(1.04);
                cursor: pointer;
            }
            &:active{
                transform: scale(0.98);
            }
            &.disabled{
                color: #94a3b8;
                background-color: #334155;
                background-image: none;
                cursor: pointer;
                .iconfont{
                    color: #94a3b8;
                }
            }
        }
    }

</style>

