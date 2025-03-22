<script setup lang="ts">
import { ref } from 'vue';
import { AxiosError } from 'axios';
import { useUserAuthStore } from '@/stores/userAuthStore';
import { useElementsStore } from '@/stores/elementsStore';
import TheLoader from '@/components/TheLoader.vue';
import axiosInstance from '@/utils/axiosInstance';
import type { SuperUserWorkShop } from '@/stores/userAuthStore';
import { parseTime } from '@/utils/util';

const userAuthStore = useUserAuthStore()
const elementsStore = useElementsStore()
const workShopDescription = ref('')
const workShopTitle = ref('')
const workShopDate = ref('')
const workShopDeadline = ref('')
const workShopStartTime = ref('')
const workShopEndTime = ref('')
const workShopLocation = ref('')
const workShopMaxParticipant = ref('')

const createWorkShop = async () => {
  const formData = new FormData()
  formData.append('type', 'create')
  formData.append('title', workShopTitle.value)
  formData.append('description', workShopDescription.value)
  formData.append('date', workShopDate.value)
  formData.append('startTime', workShopStartTime.value)
  formData.append('endTime', workShopEndTime.value)
  formData.append('location', workShopLocation.value)
  formData.append('maxParticipant', workShopMaxParticipant.value)
  formData.append('deadline', workShopDeadline.value)

  if (parseTime(workShopStartTime.value) > parseTime(workShopEndTime.value)) {
    elementsStore.ShowOverlay('Start time must be before the end time.', 'red');
    return;
  } 
  const workshopDate = Date.parse(workShopDate.value);
  const deadlineDate = Date.parse(workShopDeadline.value);
  if (deadlineDate > workshopDate) {
    elementsStore.ShowOverlay('Registration deadline must be on or before the workshop date.', 'red');
    return;
  }
  if (Number(workShopMaxParticipant.value) < 0) {
    elementsStore.ShowOverlay('The maximum number of participants must be greater than zero(0).', 'red');
    return;
  }

  elementsStore.ShowLoadingOverlay()
  try {
    const response = await axiosInstance.post('superuser/data', formData)
    const data: SuperUserWorkShop = response.data
    userAuthStore.superUserData.workshops.unshift(data)
    workShopDate.value = ''
    workShopDescription.value = ''
    workShopEndTime.value = ''
    workShopLocation.value = ''
    workShopMaxParticipant.value = ''
    workShopStartTime.value = ''
    workShopTitle.value = ''
    workShopDeadline.value = ''
    elementsStore.HideLoadingOverlay()
    elementsStore.ShowOverlay("Workshop created successfully!", "green")
  }
  catch (error) {
    elementsStore.HideLoadingOverlay()
    if (error instanceof AxiosError) {
      if (error.response) {
        if (error.response.status === 400 && error.response.data.message) {
          elementsStore.ShowOverlay(error.response.data.message, 'red')
        } 
        else {
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


</script>

<template>
  <div class="content-wrapper" v-show="elementsStore.activePage === 'SuperUserCreateWorkShop'" :class="{ 'is-active-page': elementsStore.activePage === 'SuperUserCreateWorkShop'}">
    <TheLoader v-if="!userAuthStore.fetchedDataLoaded" :func="userAuthStore.getSuperUserData" />
    <v-container v-if="userAuthStore.fetchedDataLoaded" class="form-container">
      <v-card class="pa-6 rounded-xl elevation-3">
        <v-card-title class="text-h5 font-weight-bold">Create Workshop</v-card-title>

        <v-card-text>
          <v-text-field
            v-model="workShopTitle"
            label="Title"
            placeholder="Enter the workshop title"
            hint="Keep it short and descriptive"
            persistent-hint
            prepend-icon="mdi-format-title"
          />

          <v-textarea
            v-model="workShopDescription"
            label="Description"
            placeholder="Provide details about the workshop"
            hint="Include objectives and key topics"
            persistent-hint
            prepend-icon="mdi-text"
            rows="3"
          />

          <v-text-field
            v-model="workShopDate"
            label="Date"
            type="date"
            hint="Select the workshop date"
            persistent-hint
            prepend-icon="mdi-calendar"
          />

          <v-text-field
            v-model="workShopStartTime"
            label="Start Time"
            type="time"
            hint="Specify when the workshop begins"
            persistent-hint
            prepend-icon="mdi-clock-time-four-outline"
          />

          <v-text-field
            v-model="workShopEndTime"
            label="End Time"
            type="time"
            hint="Specify when the workshop ends"
            persistent-hint
            prepend-icon="mdi-clock-end"
          />

          <v-text-field
            v-model="workShopLocation"
            label="Location"
            placeholder="Enter the venue or online link"
            hint="Provide a clear location for attendees"
            persistent-hint
            prepend-icon="mdi-map-marker"
          />

          <v-text-field
            v-model="workShopMaxParticipant"
            label="Max Participants"
            type="number"
            placeholder="Enter the maximum number of participants"
            hint="Set a limit to manage capacity"
            persistent-hint
            prepend-icon="mdi-account-group"
          />

          <v-text-field
            v-model="workShopDeadline"
            label="Deadline"
            type="date"
            hint="Select the workshop registration deadline date"
            persistent-hint
            prepend-icon="mdi-calendar"
          />
          
          <v-btn
            @click="createWorkShop"
            :disabled="!(workShopTitle && workShopDescription && workShopDate && workShopStartTime && workShopEndTime && workShopLocation && workShopMaxParticipant)"
            color="primary"
            block
            class="mt-4"
          >
            Submit
          </v-btn>
        </v-card-text>
      </v-card>
    </v-container>
    
  </div>
</template>

<style scoped>

.content-wrapper{
  justify-content: flex-start !important;
}
.form-container {
  max-width: 1200px;
  margin: auto;
}

.v-card {
  border-radius: 12px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
}

.v-btn {
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
}

.v-text-field,
.v-textarea {
  margin-bottom: 2em;
  background: #f9f9f9;
  border-radius: 8px;
}

</style>
