import {createRouter,createWebHistory,type NavigationGuardNext} from 'vue-router'
import { useUserAuthStore } from '@/stores/userAuthStore'

const checkAuth = async () => {
  const userAuthStore = useUserAuthStore()
  if (!userAuthStore.isAuthenticated) {
    try {
      await userAuthStore.UpdateToken()
      await userAuthStore.getUserData()
      userAuthStore.isAuthenticated = true
    }
    catch (e) {
      return Promise.reject(e)
    }
  }
}

const checkStudent = async (to: any, from: any, next: NavigationGuardNext) => {
  const userAuthStore = useUserAuthStore()
  try {
    await checkAuth()
  }
  catch (e:any){
    if (e?.response?.status === 401) {
      return next('/')
    }
    next(false)
    return;
  }

  if (userAuthStore.userData?.['role'] === 'student' && !userAuthStore.fetchedDataLoaded){
    userAuthStore.getStudentData()
  }
  else if (userAuthStore.userData?.['role']?.toLowerCase() === 'superuser') {
    if (!userAuthStore.fetchedDataLoaded){
      userAuthStore.getSuperUserData()
    }

    return next('/admin')
  }

  next()
}

const checkSuperuser = async (to: any, from: any, next: NavigationGuardNext) => {
  const userAuthStore = useUserAuthStore()
  try {
    await checkAuth()
  }
  catch (e:any){
    if (e?.response?.status === 401) {
      return next('/')
    }
    next(false)
    return;
  }

  if (!userAuthStore.fetchedDataLoaded && userAuthStore.userData?.['role']?.toLowerCase() === 'superuser') {
    userAuthStore.getSuperUserData()
  }
  else if (userAuthStore.userData?.['role']?.toLowerCase() === 'student') {
    if (!userAuthStore.fetchedDataLoaded){
      userAuthStore.getStudentData()
    }

    return next('/student')
  }

  next()
}

const checkLogin = async (to: any, from: any, next: NavigationGuardNext) => {
  const userAuthStore = useUserAuthStore()
  try {
    await checkAuth()
  }
  catch {
    next()
    return;
  }

  if (userAuthStore.isAuthenticated){
    if (userAuthStore.userData?.['role']?.toLowerCase() === 'student') {
      if (!userAuthStore.fetchedDataLoaded){
        userAuthStore.getStudentData()
      }

      return next('/student')
    }
    else if (userAuthStore.userData?.['role']?.toLowerCase() === 'superuser') {
      if (!userAuthStore.fetchedDataLoaded){
        userAuthStore.getSuperUserData()
      }
  
      return next('/admin')
    }
  }

  next()
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: ()=> import('@/views/LoginView.vue'),
      beforeEnter: async (to, from, next) => {
        await checkLogin(to, from, next)
      },
    },
    {
      path: '/admin',
      name: 'admin',
      component: ()=> import('@/views/SuperUserView.vue'),
      beforeEnter: async (to, from, next) => {
        await checkSuperuser(to, from, next)
      },
    },
    {
      path: '/student',
      name: 'student',
      component: ()=> import('@/views/StudentView.vue'),
      beforeEnter: async (to, from, next) => {
        await checkStudent(to, from, next)
      },
    },
  ],
})

export default router
