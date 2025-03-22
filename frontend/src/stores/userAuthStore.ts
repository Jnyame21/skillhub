import { defineStore } from 'pinia'
import { defaultAxiosInstance } from '@/utils/axiosInstance'
import axiosInstance from '@/utils/axiosInstance'
import { useElementsStore } from '@/stores/elementsStore'
import { AxiosError } from 'axios'
import router from '@/router'


export interface WorkShopStudent {
  id: number;
  name: string;
  phone_number: string;
  school: string;
  gender: string;
  program: string;
  current_year: string;
  email: string;
}

export interface WorkShop {
  id: number;
  title: string;
  description: string;
  date: string;
  start_time: string;
  end_time: string;
  location: string;
  deadline: string;
  max_participants: number | null;
}

export interface StudentWorkShop extends WorkShop  {
  registered: boolean;
}

export interface SuperUserWorkShop extends WorkShop {
  students: WorkShopStudent[];
}

export interface states {
  userData: any
  accessToken: string
  lastLogin: string;
  resetPassword: boolean;
  message: string
  isAuthenticated: boolean
  fetchedDataLoaded: boolean;
  currentYearStartDate: string;
  currentDate: string;
  currentYearEndDate: string;
  superUserData: {
    workshops: SuperUserWorkShop[];
  };
  StudentData: {
    workshops: StudentWorkShop[];
  };
}

export const useUserAuthStore = defineStore('userAuthStore', {
  state: (): states => {
    return {
      userData: null,
      accessToken: '',
      lastLogin: '',
      resetPassword: false,
      message: '',
      isAuthenticated: false,
      fetchedDataLoaded: false,
      currentDate: '',
      currentYearStartDate: '',
      currentYearEndDate: '',
      superUserData: {
        workshops: [],
      },
      StudentData: {
        workshops: [],
      },
    }
  },

  actions: {

    async logoutUser() {
      const elementsStore = useElementsStore()
      try {
        elementsStore.ShowLoadingOverlay()
        await axiosInstance.post('logout')
        this.$reset()
        elementsStore.resetStore()
        this.message = 'You have been logged out!'
        localStorage.removeItem('activePage')
        setTimeout(()=>{
          this.message = ''
        }, 5000)
        await router.push('/')
        elementsStore.HideLoadingOverlay()
        return;
      }
      catch (e) {
        elementsStore.HideLoadingOverlay()
        elementsStore.ShowOverlay('An error occurred while logging out', 'error')
        return Promise.reject(e)
      }
    },

    async getSuperUserData() {
      try {
        const response = await axiosInstance.get('superuser/data')
        this.superUserData.workshops = response.data['workshops']
        this.fetchedDataLoaded = true
      }
      catch (e) {
        return Promise.reject(e)
      }
    },

    async getStudentData() {
      try {
        const response = await axiosInstance.get('student/data')
        this.StudentData.workshops = response.data['workshops']
        this.fetchedDataLoaded = true
      }
      catch (e) {
        return Promise.reject(e)
      }
    },

    async getUserData() {
      try {
        const response = await axiosInstance.get('user/data')
        this.userData = response.data
      }
      catch (e) {
        return Promise.reject(e)
      }
    },

    async userLogin(username: string, password: string) {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)
      try {
        const response = await defaultAxiosInstance.post('login', formData)
        this.accessToken = response.data['access']
        await this.getUserData()
        this.isAuthenticated = true
        this.message = 'Login successful'
      }
      catch (error) {
        if (error instanceof AxiosError) {
          const axiosError = error as AxiosError
          if (axiosError.response) {
            if (axiosError.response.status === 401 && axiosError.response.data) {
              this.message = 'Oops! your username or password is wrong'
            }
            else {
              this.message = 'Oops! something went wrong. Try again later'
            }
          }
          else if (!axiosError.response && (axiosError.code === 'ECONNABORTED' || !navigator.onLine)) {
            this.message = 'A network error occurred! Please check you internet connection'
          }
          else {
            this.message = 'An unexpected error occurred!'
          }
          return Promise.reject()
        }
      }
    },

    async UpdateToken() {
      try {
        const response = await defaultAxiosInstance.post('api/token/refresh/')
        this.accessToken = response.data.access
      }
      catch (error: any) {
        return Promise.reject(error)
      }
    },

    async getCurrentServerTime() {
      try {
        const response = await defaultAxiosInstance.get('server_time')
        return response.data
      }
      catch (error: any) {
        return Promise.reject(error)
      }
    },
  },
})


