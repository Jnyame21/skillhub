<script setup lang="ts">
import { useElementsStore } from '@/stores/elementsStore';

const elementsStore = useElementsStore()

const changePage = (page_name: any) => {
  elementsStore.activePage = page_name
  localStorage.setItem('activePage', page_name)
}

const showOverlay = () => {
  const overlay = document.getElementById('LogoutOverlay')
  if (overlay) {
    overlay.style.display = 'flex'
  }
}


</script>


<template>
  <div class="nav-container-drawer" v-show="elementsStore.navDrawer">
    <v-list class="nav-list-container">
      <v-list-item @click="changePage('StudentWorkShops')" class="nav-item nav-link" prepend-icon="mdi-account-group">
        WORKSHOPS
      </v-list-item>
      <div class="flex-all mt-15">
        <v-btn @click="showOverlay()" size="small" color="red" variant="flat" prepend-icon="mdi-logout">LOGOUT</v-btn>
      </div>
    </v-list>
  </div>
</template>


<style scoped>

</style>
