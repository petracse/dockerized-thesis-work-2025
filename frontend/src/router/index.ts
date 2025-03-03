import { createRouter, createWebHistory } from 'vue-router'
import Ping from '../components/Ping.vue'
import Songs from '../components/Songs.vue'
import MusicProcessing from '../components/MusicProcessing.vue';  // Importáld a komponenst


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
    {
      path: '/music-processing',  // Új útvonal a MusicProcessing komponenshez
      name: 'music-processing',
      component: MusicProcessing,  // Az útvonalhoz rendeljük a komponenst
    }
  ]
})
export default router
