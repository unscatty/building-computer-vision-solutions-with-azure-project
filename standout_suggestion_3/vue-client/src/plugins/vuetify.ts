import Vue from 'vue';
import Vuetify from 'vuetify/lib/framework';

Vue.use(Vuetify);

export default new Vuetify({
  theme: {
    themes: {
      light: {
        primary: '#2a83c5',
        secondary: '#316c98',
        accent: '#5484a8',
      },
    },
  },
});
