<script setup lang="ts">
import { useUserAuthStore } from '@/stores/userAuthStore';
import { useElementsStore } from '@/stores/elementsStore';

const userAuthStore = useUserAuthStore()
const elementsStore = useElementsStore()

const changePage = (page_name: string) => {
  elementsStore.activePage = page_name
  localStorage.setItem('activePage', page_name)
}


</script>
<template>
  <div class="nav-container">
    <v-list class="nav-list-container">
      <v-list-item class="nav-item nav-link" @click="changePage('SuperUserCreateWorkShop')" prepend-icon="mdi-clipboard-text">
        CREATE WORKSHOP
      </v-list-item>

      <v-list-group>
        <template v-slot:activator="{ props }">
          <v-list-item v-bind="props" prepend-icon="mdi-account-group-outline" class="nav-item">
            WORKSHOPS
          </v-list-item>
        </template>
        <v-list-item class="nav-title nav-link" v-for="[workshop_id, value] in Object.entries(userAuthStore.superUserData.workshops)"
          :key="workshop_id" @click="changePage(`SuperUserWorkShop,${workshop_id}`)">
          {{ value.title }}
        </v-list-item>
      </v-list-group>

    </v-list>
  </div>
</template>

<style scoped>
</style>
