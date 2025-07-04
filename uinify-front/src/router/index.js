import { route } from "quasar/wrappers";
import { createRouter, createWebHistory } from "vue-router";
import routes from "./routes";

import { useAuthStore } from "src/stores/auth";

export const isAuthenticated = () => {
  const auth = useAuthStore();
  return auth.isAuthenticated;
};

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default route(function (/* { store, ssrContext } */) {
  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createWebHistory(import.meta.env.VUE_ROUTER_BASE),
  });

  Router.beforeEach((to, from, next) => {
    const hasAuth = isAuthenticated();
    if (
      typeof to.name === "string" &&
      ["login", "unauthorized", "notfound"].includes(to.name)
    ) {
      hasAuth ? next("/dashboard") : next();
    } else {
      hasAuth ? next() : next("/unauthorized");
    }
  });
  return Router;
});
