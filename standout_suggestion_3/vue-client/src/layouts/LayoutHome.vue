<template>
  <v-app>
    <v-main>
      <slot />
    </v-main>

    <!-- Snackbar -->
    <v-snackbar v-model="show" :timeout="toast.time" top right :color="toast.color">
      {{ toast.text }}
      <template v-slot:action="{ attrs }">
        <v-btn dark text v-bind="attrs" @click="show = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';

import { namespace } from 'vuex-class';
const ui = namespace('Ui');
@Component
export default class LayoutVuetifyDefault extends Vue {
  // Store
  @ui.State
  public toast!: any;

  @ui.Mutation
  public setToastVisibility!: (visible: boolean) => void;

  get show() {
    return this.toast.show;
  }

  set show(value) {
    this.setToastVisibility(value);
  }
}
</script>
