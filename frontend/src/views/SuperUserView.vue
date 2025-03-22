<script setup lang="ts">
import { useUserAuthStore } from '@/stores/userAuthStore'
import { useElementsStore } from '@/stores/elementsStore'
import { useHead } from '@vueuse/head';
import TheHeader from '@/components/TheHeader.vue';
import TheFooter from '@/components/TheFooter.vue';
import SuperUserNavContainerDesk from '@/components/superuser/SuperUserNavContainerDesk.vue';
import SuperUserNavContainerMob from '@/components/superuser/SuperUserNavContainerMob.vue';
import { onBeforeMount } from 'vue';
import SuperUserWorkShops from '@/components/superuser/SuperUserWorkShops.vue';
import SuperUserCreateWorkShop from '@/components/superuser/SuperUserCreateWorkShop.vue';

useHead({
  meta: [
    { name: "robots", content: "no-index" }
  ],
})

const userAuthStore = useUserAuthStore()
const elementsStore = useElementsStore()

onBeforeMount(() => {
  const previousActivePage = localStorage.getItem('activePage')
  if (previousActivePage) {
    elementsStore.activePage = previousActivePage
  }
  else {
    elementsStore.activePage = 'SuperUserCreateWorkShop'
    localStorage.setItem('activePage', elementsStore.activePage)
  }
})



</script>


<template>
  <TheHeader v-if="userAuthStore.userData" />
  <main class="main" v-if="userAuthStore.userData">
    <SuperUserNavContainerDesk v-if="elementsStore.onDesk" />
    <SuperUserNavContainerMob v-if="!elementsStore.onDesk" />
    <div class="pages-container">
      <div class="component-wrapper" :class="{ 'is-active-component': elementsStore.activePage === 'SuperUserCreateWorkShop' }">
        <SuperUserCreateWorkShop />
      </div>
      <div class="component-wrapper" v-for="(workshop, index) in userAuthStore.superUserData.workshops" :key="workshop.id" :class="{ 'is-active-component': elementsStore.activePage === `SuperUserWorkShop,${workshop.id}` }" >
        <SuperUserWorkShops :workshopId="workshop.id" />
      </div>
    </div>
  </main>
  <TheFooter v-if="userAuthStore.userData" />
</template>

<style scoped></style>
