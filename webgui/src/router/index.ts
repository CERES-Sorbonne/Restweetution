import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import UsersView from "../views/UserView.vue"
import RulesView from "@/views/RulesView.vue"
import MenuVue from "@/components/Menu.vue"
import StreamerView from "@/views/StreamerView.vue"
import SearcherView from "@/views/SearcherView.vue";
import DashboardView from "@/views/DashboardView.vue";
import MediaDownloaderView from "@/views/MediaDownloaderView.vue";
import ErrorView from '@/views/ErrorView.vue'
import StorageView from "@/views/StorageView.vue";


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: StorageView,
    },
    {
      path: '/rules',
      name: 'rules',
      component: RulesView
    },
    {
      path: '/users',
      name: 'users',
      component: UsersView
    },
    {
      path: '/menu',
      name: 'menu',
      component: MenuVue
    },
    {
      path: '/streamer',
      name: 'streamer',
      component: StreamerView
    },
    {
      path: '/searcher',
      name: 'searcher',
      component: SearcherView
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView
    },
    {
      path: '/errors',
      name: 'erorrs',
      component: ErrorView
    },
    {
      path: '/media',
      name: 'media',
      component: MediaDownloaderView
    },
    {
      path: '/storage',
      name: 'storage',
      component: StorageView
    }
  ],
});

export default router;
