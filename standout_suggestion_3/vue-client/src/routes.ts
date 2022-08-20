import Vue from 'vue';
import VueRouter, { RouteConfig } from 'vue-router';

// Vue.use(VueRouter);

const routes: Array<RouteConfig> = [
  {
    path: '/',
    component: () => import('./pages/Home.vue'),
    name: 'home',
    meta: {
      layout: 'LayoutVuetifyDefault',
    },
  },
];

const router = new VueRouter({
  mode: 'history',
  routes,
});

const DEFAULT_TITLE = 'Boarding Kiosk Validator';
router.afterEach((to) => {
  // Use next tick to handle router history correctly
  // see: https://github.com/vuejs/vue-router/issues/914#issuecomment-384477609
  Vue.nextTick(() => {
    document.title =
      to.meta && to.meta.title ? `${DEFAULT_TITLE} - ${to.meta.title}` : DEFAULT_TITLE;
  });
});
export default router;
