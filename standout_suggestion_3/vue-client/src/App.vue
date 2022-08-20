<template>
  <div id="vue-app">
    <AppLayout>
      <router-view></router-view>
    </AppLayout>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import AppLayout from './layouts/AppLayout.vue';

@Component({
  components: {
    AppLayout,
  },
})
export default class App extends Vue {}
</script>

<style></style>
