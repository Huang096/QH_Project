import { createApp } from 'vue';
import { createHead } from '@vueuse/head';
import VueMatomo from 'vue-matomo';
import { createMetaManager } from 'vue-meta';
import axios from 'axios';
import vueDebounce from 'vue-debounce';
import NProgress from 'nprogress';
import App from '@/App.vue';
import router from '@/router';
import { store } from './store';
import linkHandlerMixin from './mixins/linkHandler';

axios.defaults.baseURL = '/api/v2';
axios.defaults.onDownloadProgress = function onDownloadProgress(progressEvent) {
  const percentCompleted = Math.floor((progressEvent.loaded * 100.0) / progressEvent.total);
  NProgress.set(percentCompleted / 100.0);
};

// eslint-disable-next-line no-new
const app = createApp(App);
app.use(store);
app.use(router);

const head = createHead();
app.use(head);

const metaManager = createMetaManager();
app.use(metaManager);

app.use(vueDebounce, {
  listenTo: 'input',
});

if (navigator.doNotTrack !== '1') {
  app.use(VueMatomo, {
    host: 'https://csbi.chalmers.se/',
    siteId: import.meta.env.VUE_APP_MATOMOID,
    router,
  });
}

app.mixin(linkHandlerMixin);

app.mount('#app');

// new Vue({
//   el: '#app',
//   router,
//   store,
//   render: h => h(App),
// });
