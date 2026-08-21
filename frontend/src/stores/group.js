import { defineStore } from 'pinia';
import { ref } from 'vue';
import { getGroupDetailAPI, getGroupMembersAPI,joinGroupAPI,leaveGroupAPI,myGroupsAPI,myLikedGroupsAPI,unlikeGroupAPI,getCommunityActiveAPI,createActiveAPI,activeLikeAPI,createCommentAPI,getDatabase,uploadAttachmentAPI} from '../apis/groups'

export const useGroupStore = defineStore('group', () =>{
    //先定义相关state数据
    const detailGroup = ref({});
    const membersList = ref({});
    const myGroups = ref({});
    const communityActive = ref({});
    const Comment = ref({});
    const database = ref({});
    const members = ref({})


    // 定义相关action方法
    const getGroupDetail = async (group_id) => {
        const res = await getGroupDetailAPI(group_id);
        detailGroup.value = res.data;
    }

    const getGroupMembers = async (group_id) => {
        const res = await getGroupMembersAPI(group_id);
        membersList.value = res.data;
    }

    const joinGroup = async (group_id) => {
        const res = await joinGroupAPI(group_id);
        members.value = res.data;
    }

    const leaveGroup = async (group_id) => {
        const res = await leaveGroupAPI(group_id);
        members.value = res.data;
    }

    const getMyGroups = async () => {
        const res = await myGroupsAPI();
        myGroups.value = res.data;
    }

    const getMyLikedGroups = async (group_id) => {
        const res = await myLikedGroupsAPI(group_id);
    }

    const unlikeGroup = async (group_id) => {
        const res = await unlikeGroupAPI(group_id);
    }

    const getCommunityActive = async () => {
        const res = await getCommunityActiveAPI();
        communityActive.value = res.data;
    }

    const createActive = async (data) => {
        const res = await createActiveAPI(data);
        communityActive.value = res.data;
    }

    const activeLike = async (post_id) => {
        const res = await activeLikeAPI(post_id);
        communityActive.value = res.data;
    }

    const createComment = async (post_id, data) => {
        const res = await createCommentAPI(post_id, data);
        Comment.value = res.data;
    }

    const getDatabaseData = async () => {
        const res = await getDatabase();
        database.value = res.data;
    }

    return {
        detailGroup,
        membersList,
        myGroups,
        communityActive,
        Comment,
        database,
        members,

        getGroupDetail,
        getGroupMembers,
        joinGroup,
        leaveGroup,
        getMyGroups,
        getMyLikedGroups,
        unlikeGroup,
        getCommunityActive,
        createActive,
        activeLike,
        createComment,
        getDatabaseData,
    }


},{
    persist: true,
});
