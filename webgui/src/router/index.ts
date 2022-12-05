import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import UsersView from "../views/UserView.vue"
import RulesView from "@/views/RulesView.vue"
import MenuVue from "@/components/Menu.vue"
import StreamerView from "@/views/StreamerView.vue"


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
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
    }
  ],
});

export default router;
