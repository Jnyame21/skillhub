<script setup lang="ts">
import { useElementsStore } from '@/stores/elementsStore';

const elementsStore = useElementsStore()

const changePage = (page_name: any) => {
  elementsStore.activePage = page_name
  localStorage.setItem('activePage', page_name)
}

</script>


<template>
  <div class="nav-container">

    <v-list class="nav-list-container">
      <v-list-item @click="changePage('StudentWorkShops')" class="nav-item nav-link" prepend-icon="mdi-account-group">
        WORKSHOPS
      </v-list-item>
    </v-list>
  </div>
</template>


<style scoped>

</style>
