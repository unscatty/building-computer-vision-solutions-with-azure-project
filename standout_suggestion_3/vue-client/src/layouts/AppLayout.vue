<template>
  <component :is="layout">
    <slot />
  </component>
</template>

<script>
const defaultLayout = 'AppLayoutDefault';
export default {
  name: 'AppLayout',
  computed: {
    layout() {
      const layout = this.$route.meta.layout || defaultLayout;
      // console.log(layout);
      return () => import(`@/layouts/${layout}.vue`);
    },
  },
};
</script>
