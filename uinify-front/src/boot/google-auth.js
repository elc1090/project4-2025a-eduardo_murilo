import { boot } from "quasar/wrappers";
import { googleAuthService } from "src/services/GoogleAuthService";

// "async" is optional;
// more info on params: https://v2.quasar.dev/quasar-cli/boot-files
export default boot(async ({ app, router, store }) => {
  // Initialize Google Auth Service globally
  try {
    await googleAuthService.initialize();
    console.log("Google Auth Service initialized successfully");
  } catch (error) {
    console.error("Failed to initialize Google Auth Service:", error);
  }

  // Make Google Auth Service available globally
  app.config.globalProperties.$googleAuth = googleAuthService;
  app.provide("googleAuth", googleAuthService);
});
