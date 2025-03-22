<script setup lang="ts">
import { AxiosError } from 'axios';
import { useUserAuthStore } from '@/stores/userAuthStore'
import { useElementsStore } from '@/stores/elementsStore'
import TheLoader from '@/components/TheLoader.vue';
import { computed, ref, onMounted } from 'vue'
import NoData from '@/components/NoData.vue'
import axiosInstance from '@/utils/axiosInstance';
import { formatDate, formatTime} from '@/utils/util';
import pusher from '@/utils/pusher';
import type { StudentWorkShop, WorkShop } from '@/stores/userAuthStore';

const userAuthStore = useUserAuthStore()
const elementsStore = useElementsStore()
const registrationDescription = ref('')
const currentDate = new Date(userAuthStore.currentDate)

const workshops = computed(()=>{
  return userAuthStore.StudentData.workshops
})

onMounted(()=>{
  const channel = pusher.subscribe('workshop_update_channel');
  const channel2 = pusher.subscribe('workshop_creation_channel');
  channel2.bind('new_workshop', (data: WorkShop)=>{
    const workshopIndex = userAuthStore.StudentData.workshops.findIndex(item=> item.id === data.id)
    if (workshopIndex === -1){
      userAuthStore.StudentData.workshops.push({...data, registered: false})
    }
  })

  channel.bind('update', (data: {'id': number, 'update_type': string; 'new_value': string | number})=>{
    const workshopIndex = userAuthStore.StudentData.workshops.findIndex(item=> item.id === data.id)
    if (workshopIndex !== -1 && data.update_type === 'title'){
      userAuthStore.StudentData.workshops[workshopIndex].title = data.new_value as string
    }
    else if (workshopIndex !== -1 && data.update_type === 'description'){
      userAuthStore.StudentData.workshops[workshopIndex].description = data.new_value as string
    }
    else if (workshopIndex !== -1 && data.update_type === 'start_time'){
      userAuthStore.StudentData.workshops[workshopIndex].start_time = data.new_value as string
    }
    else if (workshopIndex !== -1 && data.update_type === 'end_time'){
      userAuthStore.StudentData.workshops[workshopIndex].end_time = data.new_value as string
    }
    else if (workshopIndex !== -1 && data.update_type === 'location'){
      userAuthStore.StudentData.workshops[workshopIndex].location = data.new_value as string
    }
    else if (workshopIndex !== -1 && data.update_type === 'deadline'){
      userAuthStore.StudentData.workshops[workshopIndex].deadline = data.new_value as string
    }
    else if (workshopIndex !== -1 && data.update_type === 'date'){
      userAuthStore.StudentData.workshops[workshopIndex].date = data.new_value as string
    }
    else if (workshopIndex !== -1 && data.update_type === 'max_participants'){
      userAuthStore.StudentData.workshops[workshopIndex].max_participants = data.new_value as number
    }
    else if (workshopIndex !== -1 && data.update_type === 'delete'){
      userAuthStore.StudentData.workshops.splice(workshopIndex, 1)
    }
  })
})

const get_missed_work_shops_updates = async()=>{
  try{
    const formData = new FormData()
    formData.append('type', 'fetchMissedWorkShopUpdates')
    const response = await axiosInstance.post('student/data', formData)
    const data:StudentWorkShop[] = response.data
    data.forEach(item=>{
      const existingWorkshopIndex = userAuthStore.StudentData.workshops.findIndex(subItem=> subItem.id === item.id)
      if (existingWorkshopIndex !== -1){
        userAuthStore.StudentData.workshops[existingWorkshopIndex] = item
      }
    })
  }
  catch{
    return Promise.reject()
  }
}

pusher.connection.bind('connected', ()=>{
  if (userAuthStore.StudentData.workshops.length > 0){
    get_missed_work_shops_updates()
  }
})

const cancelRegistration = async (id:number, index:number) => {
  const formData = new FormData()
  formData.append('type', 'cancel')
  formData.append('workshopId', id.toString())

  elementsStore.ShowLoadingOverlay()
  try {
    await axiosInstance.post('student/data', formData)
    userAuthStore.StudentData.workshops[index].registered = false
    elementsStore.HideLoadingOverlay()
  }
  catch (error) {
    elementsStore.HideLoadingOverlay()
    if (error instanceof AxiosError) {
      if (error.response) {
        if (error.response.status === 400 && error.response.data.message) {
          elementsStore.ShowOverlay(error.response.data.message, 'red')
        } else {
          elementsStore.ShowOverlay('Oops! something went wrong. Try again later', 'red')
        }
      }
      else if (!error.response && (error.code === 'ECONNABORTED' || !navigator.onLine)) {
        elementsStore.ShowOverlay('A network error occurred! Please check you internet connection', 'red')
      }
      else {
        elementsStore.ShowOverlay('An unexpected error occurred!', 'red')
      }
    }
  }
}


const registerWorkshop = async (id:number, index:number) => {
  const formData = new FormData()
  formData.append('type', 'register')
  formData.append('workshopId', id.toString())

  elementsStore.ShowLoadingOverlay()
  try {
    await axiosInstance.post('student/data', formData)
    userAuthStore.StudentData.workshops[index].registered = true
    elementsStore.HideLoadingOverlay()
  }
  catch (error) {
    elementsStore.HideLoadingOverlay()
    if (error instanceof AxiosError) {
      if (error.response) {
        if (error.response.status === 400 && error.response.data.message) {
          elementsStore.ShowOverlay(error.response.data.message, 'red')
        } else {
          elementsStore.ShowOverlay('Oops! something went wrong. Try again later', 'red')
        }
      }
      else if (!error.response && (error.code === 'ECONNABORTED' || !navigator.onLine)) {
        elementsStore.ShowOverlay('A network error occurred! Please check you internet connection', 'red')
      }
      else {
        elementsStore.ShowOverlay('An unexpected error occurred!', 'red')
      }
    }
  }
}

const showOverlay = (element: string, description:string='') => {
  registrationDescription.value = description
  const overlay = document.getElementById(element)
  if (overlay) {
    overlay.style.display = 'flex'
  }
}

const hidOverlay = (element: string) => {
  registrationDescription.value = ''
  const overlay = document.getElementById(element)
  if (overlay) {
    overlay.style.display = "none"
  }
}


</script>

<template>
  <div class="content-wrapper" v-show="elementsStore.activePage ==='StudentWorkShops' " :class="{ 'is-active-page': elementsStore.activePage === 'StudentWorkShops' }">
    
    <!-- workshop properties overlay -->
    <div id="StudentWorkShopPropertiesViewOverlay" class="overlay">
      <div class="overlay-card">
        <v-btn @click="hidOverlay('StudentWorkShopPropertiesViewOverlay')" color="red" size="small" class="close-btn" variant="flat">
          X
        </v-btn>
        <div class="overlay-card-content-container" style="margin-top: 3em;">
          <v-card-text>{{registrationDescription}}</v-card-text>
        </div> 
        <div class="overlay-card-action-btn-container"></div>
      </div>
    </div>
    
    <NoData v-if="userAuthStore.fetchedDataLoaded && workshops.length === 0" message="There are no workshops available" />
    <TheLoader v-if="!userAuthStore.fetchedDataLoaded" :func="userAuthStore.getStudentData" />
    <v-table class="table" fixed-header v-if="userAuthStore.fetchedDataLoaded && workshops.length > 0">
      <thead>
        <tr>
          <th class="table-head">TITLE</th>
          <th class="table-head">DATE</th>
          <th class="table-head">START TIME</th>
          <th class="table-head">END TIME</th>
          <th class="table-head">LOCATION</th>
          <th class="table-head">STATUS</th>
          <th class="table-head">ACTION</th>
          <th class="table-head">DESCRIPTION</th>
          <th class="table-head">MAX PARTICIPANTS</th>
          <th class="table-head">DEADLINE</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(_workshop_, index) in workshops.sort((a, b)=> b.id - a.id)" :key="index">
          <td class="table-data">{{ _workshop_.title  }}</td>
          <td class="table-data">
            <v-chip :size="elementsStore.btnSize1">{{ formatDate(_workshop_.date, 'long') }}</v-chip>
          </td>
          <td class="table-data">
            <v-chip :size="elementsStore.btnSize1">{{ formatTime(_workshop_.start_time) }}</v-chip>
          </td>
          <td class="table-data">
            <v-chip :size="elementsStore.btnSize1">{{ formatTime(_workshop_.end_time) }}</v-chip>
          </td>
          <td class="table-data">
            <v-chip :size="elementsStore.btnSize1">{{ _workshop_.location }}</v-chip>
          </td>
          <td class="table-data flex-all">
            <v-icon v-if="_workshop_.registered" size="small" color="green" icon="mdi-circle" />
            <v-icon v-if="!_workshop_.registered" size="small" color="yellow" icon="mdi-circle" />
            <v-chip v-if="_workshop_.registered" class="ml-2" size="x-small">registered</v-chip>
            <v-chip v-if="!_workshop_.registered" class="ml-2" size="x-small">not registered</v-chip>
          </td>
          <td class="table-data">
            <v-chip v-if="!_workshop_.registered && currentDate < new Date(_workshop_.deadline)" class="chip-link mb-1" @click="elementsStore.ShowDeletionOverlay(() => registerWorkshop(_workshop_.id, index), 'Are you sure you want to register for this workshop?.')" color="green" size="x-small">REGISTER</v-chip>
            <v-chip v-if="_workshop_.registered && currentDate < new Date(_workshop_.deadline)" class="chip-link mt-1" @click="elementsStore.ShowDeletionOverlay(() => cancelRegistration(_workshop_.id, index), 'Are you sure you want to cancel registration for this workshop?.')" color="red" size="x-small">CANCEL REGISTRATION</v-chip>
          </td>
          <td class="table-data">
            <v-chip class="chip-link" @click="showOverlay('StudentWorkShopPropertiesViewOverlay', _workshop_.description)" color="blue" :size="elementsStore.btnSize1">See Details</v-chip>
          </td>
          <td class="table-data">
            <v-chip :size="elementsStore.btnSize1">{{ _workshop_.max_participants }}</v-chip>
          </td>
          <td class="table-data">
            <v-chip :size="elementsStore.btnSize1">{{ formatDate(_workshop_.deadline, 'long') }}</v-chip>
          </td>
        </tr>
      </tbody>
    </v-table>
  </div>
</template>

<style scoped>

.overlay-card {
  max-width: 600px !important;
}

.table{
  height: 100% !important;
}

</style>

