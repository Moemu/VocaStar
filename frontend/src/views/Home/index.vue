<script setup>
import HomeNav from './HomeNav/index.vue'
import HomeCondition from './HomeCondition/index.vue'
import HomeCategory from './HomeCategory/index.vue'
import HomeRecommend from './HomeRecommend/index.vue'
import HomeExplore from './HomeExplore/index.vue'
import HomeFooter from './HomeFooter/index.vue'

</script>

<template>
        <div class="home">
            <HomeNav/>
            <HomeCondition/>
            <HomeCategory/>
            <HomeRecommend/>
            <HomeExplore/>
            <HomeFooter/>
        </div>
</template>

<style lang="scss">
    .home{
        background-image: linear-gradient(to bottom, #0f1a2b , #020617);
    }
</style>