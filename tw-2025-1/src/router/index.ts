import { createRouter, createWebHistory } from 'vue-router'
import Ping from '../components/Ping.vue'
import Songs from '../components/Songs.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Songs',
      component: Songs,
    },
    {
      path: '/ping',
      name: 'ping',
      component: Ping
    },
  ]
})
export default router
