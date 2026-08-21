import { getCosplayProfile,getCosPlayList,getCreateCosplay,getCurrentCosplay,getCosplayChioce,getFinalReport} from '../apis/cosplay'
import { ref } from 'vue';
import { defineStore } from 'pinia';

export const useCosplayStore = defineStore('cosplay', () => {
    //定义相关state数据
    const cosplayFile = ref({});//cosplay数据梗概
    const cosplayList = ref({});//剧本详情
    const cosplaySession = ref({});//会话状态返回体
    const currentSession = ref({});//当前会话
    const cosplayChoice = ref({});//选择结果
    const finalReport = ref({});//最终报告
    const component = ref('first'); // 组件实例
    const lastTitle = ref('');
    const session_id = ref('');

    //定义相关action函数
    const CosplayProfile = async () => {
        const res = await getCosplayProfile();
        cosplayFile.value = res.data;
    }

    const CosPlayList = async (script_id) => {
        const res = await getCosPlayList(script_id);
        cosplayList.value = res.data;
    }

    const CreateCosplay = async (script_id) => {
        const res = await getCreateCosplay(script_id);
        cosplaySession.value = res.data;
    }

    const CurrentCosplay = async (session_id) => {
        const res = await getCurrentCosplay(session_id);
        currentSession.value = res.data;
    }

    const CosplayChoice = async ({session_id, option_id}) => {
        const res = await getCosplayChioce({session_id, option_id});
        cosplayChoice.value = res.data;
    }

    const FinalReport = async (session_id) => {
        const res = await getFinalReport(session_id);
        finalReport.value = res.data;
    }

    return {
        cosplayFile,
        cosplayList,
        cosplaySession,
        currentSession,
        cosplayChoice,
        finalReport,
        component,
        lastTitle,
        session_id,

        CosplayProfile,
        CosPlayList,
        CreateCosplay,
        CurrentCosplay,
        CosplayChoice,
        FinalReport,
    }
})