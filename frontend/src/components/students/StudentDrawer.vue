
<script setup lang="ts">
import { useUserAuthStore } from '@/stores/userAuthStore';
import { useElementsStore } from '@/stores/elementsStore';

const userAuthStore = useUserAuthStore()
const elementsStore = useElementsStore()

const drawer = document.getElementById('StudentDrawer')
document.addEventListener('click', (event: MouseEvent)=>{
  if (drawer?.style.display !== 'none'){
    if (!drawer?.contains(event?.target as Node)){
      elementsStore.drawer = false
    }
  }
})


</script>


<template>
    <div id="StudentDrawer" class="drawer-container" v-show="elementsStore.drawer">
      <v-list class="drawer-list">
        <v-card-title class="drawer-head">STUDENT INFORMATION</v-card-title>

        <v-list-item class="drawer-item" prepend-icon="mdi-account-outline">
          <v-list-item-title class="drawer-title">
            FIRST NAME
          </v-list-item-title>
          <v-list-item-subtitle class="drawer-subtitle">
            {{ userAuthStore.userData['first_name'] }}
          </v-list-item-subtitle>
        </v-list-item>

        <v-list-item class="drawer-item" prepend-icon="mdi-card-account-details-outline">
          <v-list-item-title class="drawer-title">
            LAST NAME
          </v-list-item-title>
          <v-list-item-subtitle class="drawer-subtitle">
            {{ userAuthStore.userData['last_name'] }}
          </v-list-item-subtitle>
        </v-list-item>

        <v-list-item class="drawer-item" v-if="userAuthStore.userData['gender'].toLowerCase() === 'male'" prepend-icon="mdi-gender-male">
          <v-list-item-title class="drawer-title">
            GENDER
          </v-list-item-title>
          <v-list-item-subtitle class="drawer-subtitle">
            {{ userAuthStore.userData['gender'] }}
          </v-list-item-subtitle>
        </v-list-item>
        <v-list-item class="drawer-item" v-if="userAuthStore.userData['gender'].toLowerCase() === 'female'" prepend-icon="mdi-gender-female">
          <v-list-item-title class="drawer-title">
            GENDER
          </v-list-item-title>
          <v-list-item-subtitle class="drawer-subtitle">
            {{ userAuthStore.userData['gender'] }}
          </v-list-item-subtitle>
        </v-list-item>
        <v-list-item class="drawer-item" v-if="['other', 'none'].includes(userAuthStore.userData['gender'].toLowerCase())" prepend-icon="mdi-gender-male-female">
          <v-list-item-title class="drawer-title">
            GENDER
          </v-list-item-title>
          <v-list-item-subtitle class="drawer-subtitle">
            {{ userAuthStore.userData['gender'] }}
          </v-list-item-subtitle>
        </v-list-item>

        <v-list-item class="drawer-item" prepend-icon="mdi-school-outline">
          <v-list-item-title class="drawer-title">
            SCHOOL
          </v-list-item-title>
          <v-list-item-subtitle class="drawer-subtitle">
            {{ userAuthStore.userData['school'] }}
          </v-list-item-subtitle>
        </v-list-item>

        <v-list-item class="drawer-item" prepend-icon="mdi-book-open-variant">
          <v-list-item-title class="drawer-title">
            PROGRAM OF STUDY
          </v-list-item-title>
          <v-list-item-subtitle class="drawer-subtitle">
            {{ userAuthStore.userData['program'] }}
          </v-list-item-subtitle>
        </v-list-item>

        <v-list-item class="drawer-item" prepend-icon="mdi-calendar-outline">
          <v-list-item-title class="drawer-title">
            CURRENT YEAR
          </v-list-item-title>
          <v-list-item-subtitle class="drawer-subtitle">
            {{ userAuthStore.userData['current_year'] }}
          </v-list-item-subtitle>
        </v-list-item>

        <v-list-item class="drawer-item" prepend-icon="mdi-phone-outline">
          <v-list-item-title class="drawer-title">
            PHONE NUMBER
          </v-list-item-title>
          <v-list-item-subtitle class="drawer-subtitle">
            {{ userAuthStore.userData['phone_number'] }}
          </v-list-item-subtitle>
        </v-list-item>
        
        <v-list-item class="drawer-item" prepend-icon="mdi-email-outline">
          <v-list-item-title class="drawer-title">
            EMAIL
          </v-list-item-title>
          <v-list-item-subtitle class="drawer-subtitle">
            {{ userAuthStore.userData['email'] }}
          </v-list-item-subtitle>
        </v-list-item>
      </v-list>
    </div>
</template>


<style scoped>

</style>
