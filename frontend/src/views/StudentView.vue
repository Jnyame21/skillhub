<script setup lang="ts">
import { useUserAuthStore } from '@/stores/userAuthStore'
import { useElementsStore } from '@/stores/elementsStore'
import { ref, watch } from 'vue'
import { useHead } from '@vueuse/head';
import TheHeader from '@/components/TheHeader.vue';
import TheFooter from '@/components/TheFooter.vue';
import StudentNavContainerMob from '@/components/students/StudentNavContainerMob.vue';
import StudentNavContainerDesk from '@/components/students/StudentNavContainerDesk.vue';
import StudentWorkShops from '@/components/students/StudentWorkShops.vue';


useHead({
  meta: [
    { name: "robots", content: "no-index" }
  ],
})

const userAuthStore = useUserAuthStore()
const elementsStore = useElementsStore()

watch(() => userAuthStore.userData, () => {
  const previousActivePage = localStorage.getItem('activePage')
  if (previousActivePage) {
    elementsStore.activePage = previousActivePage
  }
  else {
    const activePage = ref('')
    activePage.value = 'StudentWorkShops'
    elementsStore.activePage = activePage.value
    localStorage.setItem('activePage', activePage.value)
  }
}, { 'once': true, 'immediate': true })

const hidOverlay = (element:string) => {
  const overlay = document.getElementById(element)
  if (overlay) {
    overlay.style.display = 'none'
  }
}

</script>

<template>

  <!-- Welcome Overlay-->
  <div id="StudentWelcomeOverlay" class="overlay" v-if="userAuthStore.userData">
    <div class="overlay-card" v-if="userAuthStore.userData['last_login']">
      <v-btn @click="hidOverlay('StudentWelcomeOverlay')" color="red" size="small" class="close-btn" variant="flat">
        X
      </v-btn>
      <div class="overlay-card-content-container" style="margin-top: 3em">
        <v-card class="welcome-card">
          <v-card-title class="text-h5 font-weight-bold">Welcome!</v-card-title>
          <v-card-text class="welcome-text"> Hello {{ userAuthStore.userData['first_name'] }} {{ userAuthStore.userData['last_name'] }}, 🎉
            Thank you for registering for our workshop! We're thrilled to have you join us. Your account has been created, and you are now logged in.
            You can log in anytime to explore new workshops and register for more. Stay tuned for updates—we look forward to seeing you soon!
          </v-card-text>
        </v-card>
      </div>
    </div>
  </div>

  <TheHeader v-if="userAuthStore.userData" />
  <main class="main" v-if="userAuthStore.userData">
    <StudentNavContainerMob v-if="!elementsStore.onDesk" />
    <StudentNavContainerDesk v-if="elementsStore.onDesk" />

    <div class="pages-container">
      <div class="component-wrapper" :class="{ 'is-active-component': elementsStore.activePage === 'StudentWorkShops' }">
        <StudentWorkShops />
      </div>
    </div>
  </main>
  <TheFooter v-if="userAuthStore.userData" />
</template>

<style scoped>
.overlay-card {
  max-width: 600px !important;
}

.welcome-card {
  max-width: 400px;
  margin: auto;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  background-color: #f5f5f5;
}

.welcome-text {
  font-size: 16px;
  color: #333;
  text-align: center;
  line-height: 1.5;
}

</style>
