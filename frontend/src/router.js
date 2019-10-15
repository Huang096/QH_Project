import Vue from 'vue';
import $ from 'jquery';
import VueRouter from 'vue-router';
// import NProgress from 'nprogress';
import Home from './components/Home';
import Explorer from './components/Explorer';
import SearchTable from './components/SearchTable';
import Resources from './components/Resources';
import About from './components/About';
import Documentation from './components/Documentation';
import Repository from './components/Repository';
import CompareModels from './components/CompareModels';
import NotFound from './components/NotFound';


Vue.use(VueRouter);

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/explore', name: 'explorerRoot', component: Explorer, props: true },
  { path: '/search', name: 'search', component: SearchTable },
  { path: '/explore/gem-browser/:model', name: 'browserRoot', component: Explorer, props: true },
  { path: '/explore/gem-browser/:model/:type/:id', name: 'browser', component: Explorer, props: true },
  { path: '/explore/map-viewer/:model', name: 'viewer', component: Explorer, props: true },
  { path: '/explore/map-viewer/:model/compartment/:id', name: 'viewerCompartment', component: Explorer, props: true },
  { path: '/explore/map-viewer/:model/subsystem/:id', name: 'viewerSubsystem', component: Explorer, props: true },
  { path: '/explore/map-viewer/:model/compartment/:id/:rid', name: 'viewerCompartmentRea', component: Explorer, props: true },
  { path: '/explore/map-viewer/:model/subsystem/:id/:rid', name: 'viewerSubsystemRea', component: Explorer, props: true },
  { path: '/about', name: 'about', component: About },
  { path: '/gems/repository', name: 'gems', component: Repository },
  { path: '/gems/comparison', name: 'comparemodels', component: CompareModels },
  { path: '/resources', name: 'resources', component: Resources },
  { path: '/documentation', name: 'documentation', component: Documentation },
  { path: '/*', name: 'notFound', component: NotFound },
];

const router = new VueRouter({
  mode: 'history',
  routes,
  scrollBehavior(to) {
    if (to.hash) {
      $(window).scrollTop($(to.hash).offset().top);
    }
  },
});

// router.beforeResolve((to, from, next) => { // eslint-disable-line no-unused-vars
//   console.log('test1');
//   console.log(to);
//   NProgress.start();
//   next();
// });

// router.afterEach((to, from) => { // eslint-disable-line no-unused-vars
//   console.log('test2');
//   NProgress.done();
// });

export default router;
