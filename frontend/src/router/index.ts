import { createRouter, createWebHistory } from 'vue-router'
import Songs from '../components/Songs.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Songs',
      component: Songs,
    }
  ]
})
export default router
