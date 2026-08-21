import { ref } from 'vue'
import { defineStore } from 'pinia'
import { getGroupsCategoryAPI, getGroupsAPI, getGroupDetailAPI} from '../apis/groups'
import { getSearchPartnerAPI,getPartnerSkillAPI,getRecommendPartnerAPI,getchoosePartnerAPI,getDeletePartnerAPI,getMyPartnerAPI} from '../apis/partner'
import { getTeacherCategoryAPI,getTeacherListAPI,createTeacherAPI,myTeacherListAPI} from '../apis/teacher'

export const useCommunityStore = defineStore('community', () =>{
    //定义相关state数据
    // groups相关数据
    const isSun = ref(false);
    const groupsCategory = ref({});
    const groups = ref({});
    const groupDetail = ref({});

    // partner相关数据
    const myPartner = ref({});
    const skillList = ref([]);
    const recommendPartner = ref({});
    const choosePartner = ref({});
    const deletePartner = ref({});

    //teachers相关数据
    const teacherCategory = ref({});
    const teacherList = ref({});
    const myteacherList = ref({});

    //定义相关action方法
    const getGroupsCategory = async () => {
        const res = await getGroupsCategoryAPI();
        groupsCategory.value = res.data;
    }

    const getGroups = async (querry) => {
        const res = await getGroupsAPI({q : querry});
        groups.value = res.data;
    }

    const getGroupDetail = async (id) => {
        const res = await getGroupDetailAPI(id);
        groupDetail.value = res.data;
    }


    // 定义partner相关方法
    const getRecommendPartner = async () => {
        const res = await getRecommendPartnerAPI();
        recommendPartner.value = res.data;
    }

    const getPartnerSkill = async () => {
        const res = await getPartnerSkillAPI();
        skillList.value = res.data;
    }

    const getchoosePartner = async (id) => {
        const res = await getchoosePartnerAPI(id);
        choosePartner.value = res.data;
    }

    const getDeletePartner = async (id) => {
        const res = await getDeletePartnerAPI(id);
        deletePartner.value = res.data;
    }

    const getMyPartner = async () => {
        const res = await getMyPartnerAPI();
        myPartner.value = res.data;
    }


    // 定义teachers相关方法
    const getTeacherCategory = async () => {
        const res = await getTeacherCategoryAPI();
        teacherCategory.value = res.data;
    }

    const getTeacherList = async () => {
        const res = await getTeacherListAPI();
        teacherList.value = res.data;
    }

    const createTeacher = async (mentor_id) => {
        const res = await createTeacherAPI(mentor_id);
        myTeacherList.value = res.data;
    }

    const myTeacherList = async () => {
        const res = await myTeacherListAPI();
        myteacherList.value = res.data;
    }





    return {
        isSun,
        groupsCategory,
        groups,
        groupDetail,

        myPartner,
        skillList,
        recommendPartner,
        choosePartner,
        deletePartner,

        teacherCategory,
        teacherList,
        myteacherList,


        getGroupsCategory,
        getGroups,
        getGroupDetail,
        getRecommendPartner,
        getPartnerSkill,
        getchoosePartner,
        getDeletePartner,
        getMyPartner,
        getTeacherCategory,
        getTeacherList,
        createTeacher,
        myTeacherList
    }
})