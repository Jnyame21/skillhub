<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useUserAuthStore } from '@/stores/userAuthStore';
import { useElementsStore } from '@/stores/elementsStore';
import TheLoader from '@/components/TheLoader.vue';
import { formatTime, formatDate, parseTime } from '@/utils/util';
import axiosInstance from '@/utils/axiosInstance';
import pusher from '@/utils/pusher';
import { AxiosError } from 'axios';
import type { WorkShopStudent, SuperUserWorkShop } from '@/stores/userAuthStore';
import NoData from '../NoData.vue';

const userAuthStore = useUserAuthStore()
const elementsStore = useElementsStore()
const workShopDescription = ref('')
const updateType = ref('')
const new_value = ref<string | number>('')

interface Props {
  workshopId: number;
}

const props = defineProps<Props>()
const workshopId = props.workshopId

const workShop = computed(() => {
  return userAuthStore.superUserData.workshops.find(item=> item.id === workshopId)
})
const workShopIndex = computed(() => {
  return userAuthStore.superUserData.workshops.findIndex(item=> item.id === workshopId)
})

onMounted(()=>{
  initializePusherChannels()
})

const initializePusherChannels = ()=>{
  if (workShop.value?.date && new Date(userAuthStore.currentDate) < new Date(workShop.value.date)){
    const channel_name = `workshop_${workshopId}_registration_channel`
    if (!pusher.allChannels().some(channel=> channel.name === channel_name)){
      const channel = pusher.subscribe(channel_name);
      channel.bind('new_registration', (data: WorkShopStudent)=>{
        const studentItemIndex = userAuthStore.superUserData.workshops[workShopIndex.value].students.findIndex(item=> item.id === data.id)
        if (studentItemIndex === -1){
          userAuthStore.superUserData.workshops[workShopIndex.value].students.unshift(data)
        }
      })
      channel.bind('cancel_registration', (data: number)=>{
        const studentItemIndex = userAuthStore.superUserData.workshops[workShopIndex.value].students.findIndex(item=> item.id === data)
        if (studentItemIndex !== -1){
          userAuthStore.superUserData.workshops[workShopIndex.value].students.splice(studentItemIndex, 1)
        }
      })
    }
  }
}

const get_missed_work_shops_registrations = async()=>{
  try{
    const formData = new FormData()
    formData.append('type', 'fetchMissedWorkShopRegistrations')
    const response = await axiosInstance.post('superuser/data', formData)
    const data:SuperUserWorkShop[] = response.data
    userAuthStore.superUserData.workshops = data
  }
  catch{
    return Promise.reject()
  }
}

pusher.connection.bind('connected', ()=>{
  if (userAuthStore.fetchedDataLoaded){
    get_missed_work_shops_registrations()
  }
})

const updateWorkShop = async () => {
  const formData = new FormData()
  formData.append('type', `update_${updateType.value}`)
  formData.append('newValue', new_value.value.toString())
  formData.append('workshopId', workshopId.toString())
  
  if (updateType.value === 'start_time' && parseTime(new_value.value?.toString()) > parseTime(workShop.value?.end_time || '')) {
    elementsStore.ShowOverlay('Start time must be before the end time.', 'red');
    return;
  } 

  if (updateType.value === 'end_time' && parseTime(new_value.value?.toString()) < parseTime(workShop.value?.start_time || '')) {
    elementsStore.ShowOverlay('End time must be after the start time.', 'red');
    return;
  }

  const newDate = Date.parse(new_value.value?.toString() || "");
  const workshopDate = Date.parse(workShop.value?.date || '');
  const deadlineDate = Date.parse(workShop.value?.deadline || '');

  if (updateType.value === 'date' && newDate < deadlineDate) {
    elementsStore.ShowOverlay('Workshop date must be on or after the registration deadline.', 'red');
    return;
  }

  if (updateType.value === 'deadline' && newDate > workshopDate) {
    elementsStore.ShowOverlay('Registration deadline must be on or before the workshop date.', 'red');
    return;
  }

  if (workShop.value && updateType.value === 'max_participants' && (new_value.value as number) < workShop.value.students.length) {
    elementsStore.ShowOverlay('The maximum number of participants must be at least equal to the current number of registered students.', 'red');
    return;
  }

  elementsStore.ShowLoadingOverlay()
  try {
    await axiosInstance.post('superuser/data', formData)
    if (updateType.value === 'title'){
      userAuthStore.superUserData.workshops[workShopIndex.value].title = new_value.value as string
    }
    else if (updateType.value === 'description'){
      userAuthStore.superUserData.workshops[workShopIndex.value].description = new_value.value as string
    }
    else if (updateType.value === 'start_time'){
      userAuthStore.superUserData.workshops[workShopIndex.value].start_time = new_value.value as string
    }
    else if (updateType.value === 'end_time'){
      userAuthStore.superUserData.workshops[workShopIndex.value].end_time = new_value.value as string
    }
    else if (updateType.value === 'date'){
      userAuthStore.superUserData.workshops[workShopIndex.value].date = new_value.value as string
      initializePusherChannels()
    }
    else if (updateType.value === 'deadline'){
      userAuthStore.superUserData.workshops[workShopIndex.value].deadline = new_value.value as string
    }
    else if (updateType.value === 'location'){
      userAuthStore.superUserData.workshops[workShopIndex.value].location = new_value.value as string
    }
    else if (updateType.value === 'max_participants'){
      userAuthStore.superUserData.workshops[workShopIndex.value].max_participants = new_value.value as number
    }
    
    updateType.value = ''
    new_value.value = ''
    closeOverlay(`SuperUserWorkShopUpdateOverlay${workshopId}`)
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

const deleteWorkShop = async () => {
  const formData = new FormData()
  formData.append('type', 'delete')
  formData.append('workshopId', workshopId.toString())

  elementsStore.ShowLoadingOverlay()
  try {
    await axiosInstance.post('superuser/data', formData)
    userAuthStore.superUserData.workshops.splice(workShopIndex.value, 1)
    const pageName = 'SuperUserCreateWorkShop'
    elementsStore.activePage = pageName
    localStorage.setItem('activePage', pageName)
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

const showOverlay = (element: string, description: string='', updade_type: string = '') => {
  workShopDescription.value = description
  updateType.value = updade_type
  const overlay = document.getElementById(element)
  if (overlay) {
    overlay.style.display = 'flex'
  }
}

const closeOverlay = (element: string) => {
  workShopDescription.value = ''
  const overlay = document.getElementById(element)
  if (overlay) {
    overlay.style.display = 'none'
  }
}


</script>

<template>
  <div class="content-wrapper" v-show="elementsStore.activePage === `SuperUserWorkShop,${workshopId}`" :class="{ 'is-active-page': elementsStore.activePage === `SuperUserWorkShop,${workshopId}`}">

    <!-- workshop properties overlay -->
    <div :id="`SuperUserWorkShopPropertiesViewOverlay${workshopId}`" class="overlay">
      <div class="overlay-card">
        <v-btn @click="closeOverlay(`SuperUserWorkShopPropertiesViewOverlay${workshopId}`)" color="red" size="small" class="close-btn" variant="flat">
          X
        </v-btn>
        <div class="overlay-card-content-container" style="margin-top: 3em;">
          <v-card-text>{{workShopDescription}}</v-card-text>
        </div> 
        <div class="overlay-card-action-btn-container"></div>
      </div>
    </div>

    <!-- workshop update overlay -->
    <div :id="`SuperUserWorkShopUpdateOverlay${workshopId}`" class="overlay">
      <div class="overlay-card">
        <v-btn @click="closeOverlay(`SuperUserWorkShopUpdateOverlay${workshopId}`)" color="red" size="small" class="close-btn" variant="flat">
          X
        </v-btn>
        <div class="overlay-card-content-container" style="margin-top: 3em;">
          <v-text-field v-if="updateType === 'title'" class="input-field" v-model="new_value" label="NEW TITLE" clearable variant="solo-filled"  prepend-icon="mdi-format-title"
            density="comfortable" placeholder="Eg. Mastering Web Development with Vue.js" hint="Enter a new title for the workshop" persistent-hint
          />
          <v-textarea class="mb-5" v-if="updateType === 'description'" v-model="new_value" label="NEW DESCRIPTION" clearable variant="solo-filled" no-resize  prepend-icon="mdi-text"
            density="comfortable" rows="10" hint="Include objectives and key topics" persistent-hint placeholder="Provide details about the workshop"
          />
          <v-text-field class="input-field" v-if="updateType === 'date'" v-model="new_value" label="NEW DATE" type="date" variant="solo-filled" density="comfortable"
            clearable persistent-hint hint="Select a new date for the workshop" prepend-icon="mdi-calendar"
          />
          <v-text-field class="input-field" v-if="updateType === 'deadline'" v-model="new_value" label="NEW REGISTRATION DEADLINE" type="date" variant="solo-filled" density="comfortable"
            clearable persistent-hint hint="Select a new registration deadline date for the workshop" prepend-icon="mdi-calendar"
          />
          <v-text-field class="input-field" v-if="updateType === 'start_time'" v-model="new_value" label="NEW START TIME" type="time" variant="solo-filled" density="comfortable"
            clearable persistent-hint hint="Select a new time the workshop will start" prepend-icon="mdi-clock-time-four-outline"
          />
          <v-text-field class="input-field" v-if="updateType === 'end_time'" v-model="new_value" label="NEW CLOSING TIME" type="time" variant="solo-filled" density="comfortable"
            clearable persistent-hint hint="Select a new time the workshop will end" prepend-icon="mdi-clock-end"
          />
          <v-text-field class="input-field" v-if="updateType === 'location'" v-model="new_value" label="NEW LOCATION" variant="solo-filled" density="comfortable"
            clearable persistent-hint hint="Enter a new location for the workshop" prepend-icon="mdi-map-marker"
          />
          <v-text-field class="input-field" v-if="updateType === 'max_participants'" v-model="new_value" label="NEW MAX PARTICIPANTS" type="number" variant="solo-filled" density="comfortable"
            clearable persistent-hint hint="Enter a new participant limit for the workshop" prepend-icon="mdi-account-group"
          />
        </div> 
        <div class="overlay-card-action-btn-container">
          <v-btn @click="updateWorkShop" :disabled="!new_value" size="small" variant="flat" color="black" class="mb-5" type="submit">
            SUBMIT
          </v-btn>
        </div>
      </div>
    </div>

    <div class="content-header" v-if="workShop && userAuthStore.fetchedDataLoaded">
      <h4 class="content-header-title">{{ workShop.title }}<v-icon size="small" color="black" icon="mdi-pencil" @click="showOverlay(`SuperUserWorkShopUpdateOverlay${workshopId}`, '', 'title')" /></h4>
    </div>
    <div class="content-header head-info" v-if="workShop && userAuthStore.fetchedDataLoaded">
      <p class="content-header-text">TIME: {{ formatTime(workShop.start_time) }}<v-icon size="small" color="black" icon="mdi-pencil" @click="showOverlay(`SuperUserWorkShopUpdateOverlay${workshopId}`, '', 'start_time')" /> - {{ formatTime(workShop.end_time) }}<v-icon size="small" color="black" icon="mdi-pencil" @click="showOverlay(`SuperUserWorkShopUpdateOverlay${workshopId}`, '', 'end_time')" /></p>
      <p class="content-header-text">LOCATION: {{ workShop.location }}<v-icon size="small" color="black" icon="mdi-pencil" @click="showOverlay(`SuperUserWorkShopUpdateOverlay${workshopId}`, '', 'location')" /></p>
      <p class="content-header-text">DATE: {{ formatDate(workShop.date, 'long') }}<v-icon size="small" color="black" icon="mdi-pencil" @click="showOverlay(`SuperUserWorkShopUpdateOverlay${workshopId}`, '', 'date')" /></p>
      <p class="content-header-text">DEADLINE: {{ formatDate(workShop.deadline, 'long') }}<v-icon size="small" color="black" icon="mdi-pencil" @click="showOverlay(`SuperUserWorkShopUpdateOverlay${workshopId}`, '', 'deadline')" /></p>
      <p class="content-header-text">MAX PARTICIPANTS: {{ workShop.max_participants }}<v-icon size="small" color="black" icon="mdi-pencil" @click="showOverlay(`SuperUserWorkShopUpdateOverlay${workshopId}`, '', 'max_participants')" /></p>
      <v-chip class="chip-link" @click="showOverlay(`SuperUserWorkShopPropertiesViewOverlay${workshopId}`, workShop.description)" color="blue" :size="elementsStore.btnSize1">See Details</v-chip><v-icon class="ml-2" size="small" color="blue" icon="mdi-pencil" @click="showOverlay(`SuperUserWorkShopUpdateOverlay${workshopId}`, '', 'description')" />
      <v-icon class="ml-5" size="small" color="red" icon="mdi-delete" @click="elementsStore.ShowDeletionOverlay(()=> deleteWorkShop(), 'Are you sure you want to delete this workshop? You will be redirected to the workshop creation page when the process is complete')" />
    </div>
    <TheLoader v-if="workShop && !userAuthStore.fetchedDataLoaded" :func="userAuthStore.getSuperUserData" />
    <NoData v-if="workShop && workShop.students.length === 0" message="No student has registered for this workshop yet." />
    <v-table fixed-header class="table" v-if="workShop && workShop.students.length > 0">
      <thead>
        <tr>
          <th class="table-head">STUDENT</th>
          <th class="table-head">GENDER</th>
          <th class="table-head">SCHOOL</th>
          <th class="table-head">PROGRAM</th>
          <th class="table-head">CURRENT YEAR</th>
          <th class="table-head">PHONE NUMBER</th>
          <th class="table-head">EMAIL</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="_student_ in workShop.students.sort((a, b)=> b.id - a.id)" :key="_student_.id">
          <td class="table-data">{{ _student_.name }}</td>
          <td class="table-data">{{ _student_.gender }}</td>
          <td class="table-data">{{ _student_.school }}</td>
          <td class="table-data">{{ _student_.program }}</td>
          <td class="table-data">
            <v-chip :size="elementsStore.btnSize1">{{ _student_.current_year }}</v-chip>
          </td>
          <td class="table-data">
            <v-chip :size="elementsStore.btnSize1">{{ _student_.phone_number }}</v-chip>
          </td>
          <td class="table-data">
            <v-chip :size="elementsStore.btnSize1">{{ _student_.email }}</v-chip>
          </td>
        </tr>
      </tbody>
    </v-table>
  </div>
</template>

<style scoped>

.content-header {
  min-height: 10% !important;
}
.head-info{
  min-height: 25% !important;
}
.overlay-card{
  max-width: 600px !important;
}


</style>
