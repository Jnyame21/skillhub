<script setup lang="ts">
import { computed, reactive } from "vue";
import { useRouter } from "vue-router";
import { useHead } from '@vueuse/head'
import { useUserAuthStore } from '@/stores/userAuthStore'
import { onMounted, ref } from "vue";
import { defaultAxiosInstance } from "@/utils/axiosInstance";
import { AxiosError } from "axios";
import { useElementsStore } from "@/stores/elementsStore";
const userAuthStore = useUserAuthStore()
const elementsStore = useElementsStore()

useHead({
  meta: [
    { name: "description", content: "SkillHub - A seamless platform for students to explore, register, and participate in skill-training workshops. Learn, grow, and enhance your skills today!" },
    { name: "robots", content: "index, follow" }
  ],
})

const router = useRouter()
const signUp = ref(false)
const data = reactive({
  form: false,
  username: '',
  password: '',
  loading: false,
  visible: false,
  lockField: false,
  firstName: '',
  lastName: '',
  email: '',
  signupPassword: '',
  school: '',
  program: '',
  currentYear: '',
  phoneNumber: '',
  gender: '',
})

const isFormValid = computed(() => {
  return !(data.username && data.password)
})

onMounted(()=>{
  localStorage.removeItem('activePage')
})

const authenticate = async () => {
  data.loading = true;
  data.lockField = true;
  try {
    await userAuthStore.userLogin(data.username, data.password);
    if (userAuthStore.isAuthenticated && userAuthStore.userData['role'].toLowerCase() === 'student') {
      data.password = '';
      data.loading = false;
      setTimeout(() => {
        router.push('/student');
      }, 2000);
    }
    else if (userAuthStore.isAuthenticated && userAuthStore.userData['role'].toLowerCase() === 'superuser') {
      data.password = '';
      data.loading = false;
      setTimeout(() => {
        router.push('/admin');
      }, 2000);
    }
    else{
      userAuthStore.message = "Ooop! Something went wrong. Contact your IT administrator"
      data.loading = false;
      data.lockField = false;
      setTimeout(() => {
        userAuthStore.message = '';
      }, 10000);
    }
  }
  catch {
    data.loading = false;
    data.lockField = false;
    setTimeout(() => {
      userAuthStore.message = '';
    }, 10000);
  }
}

const studentSignUp = async () => {
  const formData = new FormData()
  formData.append('type', 'signup')
  formData.append('firstName', data.firstName)
  formData.append('lastName', data.lastName)
  formData.append('gender', data.gender)
  formData.append('school', data.school)
  formData.append('program', data.program)
  formData.append('currentYear', data.currentYear)
  formData.append('phoneNumber', data.phoneNumber)
  formData.append('email', data.email)
  formData.append('password', data.signupPassword)
  elementsStore.ShowLoadingOverlay()
  try {
    await defaultAxiosInstance.post('student/signup', formData)
    data.password = '';
    data.gender = ''
    data.currentYear = ''
    data.firstName = ''
    data.lastName = ''
    data.email = ''
    data.school = ''
    data.program = ''
    data.phoneNumber = ''
    data.signupPassword = ''
    closeOverlay('SignUpOverlay')
    elementsStore.HideLoadingOverlay()
    elementsStore.ShowOverlay("Your student account has been created successfully. Your username has been sent to your email. Please log in with it.", 'green')
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

const showOverlay = (element: string) => {
  const overlay = document.getElementById(element)
  if (overlay) {
    overlay.style.display = 'flex'
  }
}

const closeOverlay = (element: string) => {
  const overlay = document.getElementById(element)
  if (overlay) {
    overlay.style.display = 'none'
  }
}


</script>

<template>
  <div class="container flex-c flex-column">
    
    <!-- signup overlay -->
    <div id="SignUpOverlay" class="overlay">
      <div class="overlay-card">
        <v-btn @click="closeOverlay('SignUpOverlay')" color="red" size="small" class="close-btn" variant="flat">
          X
        </v-btn>
        <div class="overlay-card-content-container" style="margin-top: 3em;">
          <v-text-field class="input-field" :disabled="data.lockField" v-model="data.firstName"
            label="FIRST NAME" hint="Enter your first name" density="compact" type="text" clearable prepend-inner-icon="mdi-account-outline">
          </v-text-field>
          <v-text-field class="input-field" :disabled="data.lockField" v-model="data.lastName"
            label="LAST NAME" hint="Enter your last name (middle name + surname)" density="compact" type="text" clearable prepend-inner-icon="mdi-account-outline">
          </v-text-field>
          <v-select class="select" :items="['Male', 'Female', 'Other']" label="GENDER" v-model="data.gender" variant="solo-filled"
            density="comfortable" clearable persistent-hint hint="Select your gender" prepend-inner-icon="mdi-gender-transgender"
          />
          <v-text-field class="input-field" :disabled="data.lockField" v-model="data.email"
            label="EMAIL" hint="Enter your email" density="compact" type="email" clearable prepend-inner-icon="mdi-email">
          </v-text-field>
          <v-text-field class="input-field" :disabled="data.lockField" v-model="data.school"
            label="SCHOOL" hint="Enter the name of your school" density="compact" clearable prepend-inner-icon="mdi-school">
          </v-text-field>
          <v-text-field class="input-field" :disabled="data.lockField" v-model="data.program"
            label="PROGRAM" hint="Enter your program of study" density="compact" clearable prepend-inner-icon="mdi-book-open">
          </v-text-field>
          <v-text-field class="input-field" :disabled="data.lockField" v-model="data.currentYear"
            label="CURRENT YEAR" hint="Which year are you currently in?" type="number" density="compact" clearable prepend-inner-icon="mdi-timeline-clock">
          </v-text-field>
          <v-text-field class="input-field" :disabled="data.lockField" v-model="data.phoneNumber" placeholder="Eg. +233596021383"
            label="PHONE NUMBER" hint="Enter your mobile number" density="compact" type="text" clearable prepend-inner-icon="mdi-phone">
          </v-text-field>
          <v-text-field class="input-field password" :append-inner-icon="data.visible ? 'mdi-eye-off-outline' : 'mdi-eye-outline'"
            @click:append-inner="data.visible = !data.visible" :disabled="data.lockField"
            :type="data.visible ? 'text' : 'password'" clearable density="compact"
            hint="Set a password" v-model="data.signupPassword" label="PASSWORD"
            prepend-inner-icon="mdi-lock-outline">
          </v-text-field>
          <p class="mb-5" style="color: black;">Already have a student account? <a @click="closeOverlay('SignUpOverlay')" class="signup-link">Sign in</a></p>
        </div>
        <div class="overlay-btn-action-container">
          <v-btn @click="studentSignUp" class="mb-3" type="submit" prepend-icon="mdi-lock-open-outline" :loading="data.loading" color="black"
            :disabled="!(data.firstName && data.lastName && data.gender && data.school && data.program && data.currentYear && data.phoneNumber && data.email && data.signupPassword)">SIGN UP
          </v-btn>
        </div>
      </div>
    </div>
    
    <!-- login form -->
    <div class="img-container flex-c align-center justify-center">
      <section class="flex-all-c form-container">
        <h1 class="portal-name">SKILLHUB</h1>
        <img class="logo" src="/app_logo.png" alt="app logo">
        <div class="flex-c align-center w-100" style="background-color: transparent">
          <v-form class="login-form-input-container" @submit.prevent="authenticate">
            <div class="form-error-message-container">
              <h6 class="form-error-message login-success-message" v-if="userAuthStore.message && userAuthStore.isAuthenticated">
                {{ userAuthStore.message }}
              </h6>
              <h6 class="login-form-error-message" style="color: red"
                v-if="userAuthStore.message && !userAuthStore.isAuthenticated">{{ userAuthStore.message }}
              </h6>
            </div>
            <v-text-field v-if="!signUp" :disabled="data.lockField" class="form-text-field username" v-model="data.username"
              label="USERNAME" hint="Enter your username" density="compact" type="text" clearable prepend-inner-icon="mdi-account-outline">
            </v-text-field>
            <v-text-field v-if="!signUp" :append-inner-icon="data.visible ? 'mdi-eye-off-outline' : 'mdi-eye-outline'"
              @click:append-inner="data.visible = !data.visible" :disabled="data.lockField"
              :type="data.visible ? 'text' : 'password'" clearable density="compact"
              class="form-text-field password" hint="Enter your password" v-model="data.password" label="PASSWORD"
              prepend-inner-icon="mdi-lock-outline">
            </v-text-field>
            <v-text-field v-if="signUp" :disabled="data.lockField" class="form-text-field username" v-model="data.firstName"
              label="FIRST NAME" hint="Enter your first name" density="compact" type="text" clearable prepend-inner-icon="mdi-account-outline">
            </v-text-field>
            <v-text-field v-if="signUp" :disabled="data.lockField" class="form-text-field username" v-model="data.lastName"
              label="LAST NAME" hint="Enter your last name (middle name + surname)" density="compact" type="text" clearable prepend-inner-icon="mdi-account-outline">
            </v-text-field>
            <v-text-field v-if="signUp" :disabled="data.lockField" class="form-text-field username" v-model="data.email"
              label="EMAIL" hint="Enter your email" density="compact" type="email" clearable prepend-inner-icon="mdi-account-outline">
            </v-text-field>
            <v-text-field v-if="signUp" :append-inner-icon="data.visible ? 'mdi-eye-off-outline' : 'mdi-eye-outline'"
              @click:append-inner="data.visible = !data.visible" :disabled="data.lockField"
              :type="data.visible ? 'text' : 'password'" clearable density="compact"
              class="form-text-field password" hint="Set a password" v-model="data.password" label="PASSWORD"
              prepend-inner-icon="mdi-lock-outline">
            </v-text-field>
            <p v-if="!signUp" class="signup-text">Don't have a student account yet? <a @click="showOverlay('SignUpOverlay')" class="signup-link">Sign up</a></p>
            <v-btn v-if="!signUp" class="submit-btn" type="submit" prepend-icon="mdi-lock-open-outline" :loading="data.loading"
              :disabled="isFormValid">LOGIN
            </v-btn>
            <v-btn v-if="signUp" class="submit-btn" type="submit" prepend-icon="mdi-lock-open-outline" :loading="data.loading"
              :disabled="!(data.firstName && data.lastName && data.email && data.password)">SIGN UP
            </v-btn>
          </v-form>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>

.container {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
}
.img-container {
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
  background-size: cover !important;
  background-image: url('app_background_img.jpg') !important;
  background-position: center !important;
  flex-grow: 1 !important;
}
.form-container {
  border-radius: 1em !important;
  background-color: #333333 !important;
  padding: 1em !important;
  width: 90% !important;
  height: 95% !important;
  min-height: 500px;
  max-height: 900;
  max-width: 600px !important;
  overflow: auto !important;
}
.portal-name {
  color: yellow;
  font-size: 2rem;
  font-weight: 700;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
  font-family: 'Roboto', sans-serif;
  text-align: center;
}
.logo {
  width: 80px;
  height: 80px;
  margin-top: 1em;
}
.login-form-input-container{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 300px;
  max-width: 550px;
  width: 95%;
}

.form-error-message-container {
  display: flex !important;
  align-items: center !important;
  flex-direction: column;
  height: 100px !important;
  justify-content: center !important;
  width: 100% !important;
}
.login-form-error-message {
  font-size: .9rem !important;
  padding: .1em !important;
  text-align: center !important;
  width: 100% !important;
  height: max-content;
}
.form-error-message{
  margin-top: .5em !important;
  margin-bottom: .5em !important;
}
.form-text-field {
  width: 250px;
  font-weight: bold;
  margin-top: .5em;
  color: yellow !important;
}
.login-success-message{
  color: yellow !important;
  text-transform: uppercase !important;
}
.submit-btn {
  margin-top: 2em;
  font-weight: bold;
}

.forgot-password {
  color: white;
  font-size: 1rem;
}

.forgot-password:hover {
  color: yellow;
  cursor: pointer;
}

.footer {
  background-color: black;
  color: yellow;
  text-align: center;
  padding: 1em;
}

.signup-text {
  font-size: 14px;
  color: white;
  text-align: center;
  margin-top: 1em;
}

.signup-link {
  color: #007bff;
  font-weight: bold;
  text-decoration: none;
}

.signup-link:hover {
  text-decoration: underline;
}
.overlay-card{
  max-width: 700px !important;
}


</style>
