<template>
  <div class="flex items-center justify-center min-h-screen">
    <div class="p-8 rounded shadow-md w-full max-w-md">
      <h1 class="text-2xl font-bold mb-6 text-center">Login</h1>

      <!-- Google Login Section -->
      <div class="mb-6">
        <div
          id="google-signin-button"
          class="w-full flex justify-center mb-4"
        ></div>
        <div class="text-center text-gray-500 text-sm mb-4">
          <span class="bg-white px-2">ou</span>
        </div>
      </div>

      <!-- Traditional Login Form -->
      <q-input v-model="form.username" label="Username" filled class="mb-4" />
      <q-input
        v-model="form.password"
        label="Password"
        type="password"
        filled
        class="mb-6"
      />
      <q-btn
        label="Login"
        color="primary"
        class="w-full"
        @click="handleLogin"
        :loading="loading"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "stores/auth";
import { login, googleAuth } from "src/services/DefaultService";
import { useQuasar } from "quasar";
import { googleAuthService } from "src/services/GoogleAuthService";

const $q = useQuasar();
const router = useRouter();
const auth = useAuthStore();

const form = ref({
  username: "",
  password: "",
});

const loading = ref(false);

// Traditional login handler
const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    $q.notify({
      type: "negative",
      message: "Please enter username and password",
    });
    return;
  }

  loading.value = true;
  try {
    const { data } = await login(form.value);
    auth.storageAuthSave({
      user: data,
      authType: "traditional",
    });
    $q.notify({
      type: "positive",
      message: "Login successful!",
    });
    router.push("/dashboard");
  } catch (error) {
    console.error(error);
    $q.notify({
      type: "negative",
      message: "Login failed. Please check your credentials.",
    });
  } finally {
    loading.value = false;
  }
};

// Google login success handler
const handleGoogleLoginSuccess = async (event) => {
  const { userInfo, credential } = event.detail;

  try {
    // Call backend to create/find user
    const { data } = await googleAuth({
      email: userInfo.email,
      name: userInfo.name,
      google_id: userInfo.sub,
      picture: userInfo.picture,
      given_name: userInfo.given_name,
      family_name: userInfo.family_name,
    });

    // Save auth data with backend user ID
    auth.storageAuthSaveGoogle(userInfo, credential, data);

    $q.notify({
      type: "positive",
      message: `Welcome, ${userInfo.name}!`,
    });

    router.push("/dashboard");
  } catch (error) {
    console.error("Error during Google authentication:", error);
    $q.notify({
      type: "negative",
      message: "Failed to authenticate with Google. Please try again.",
    });
  }
};

// Google login error handler
const handleGoogleLoginError = (event) => {
  console.error("Google login error:", event.detail.error);
  $q.notify({
    type: "negative",
    message: "Google login failed. Please try again.",
  });
};

// Initialize Google Auth on component mount
onMounted(async () => {
  try {
    const initialized = await googleAuthService.initialize();
    if (initialized) {
      // Render Google Sign-In button
      googleAuthService.renderButton("google-signin-button", {
        theme: "outline",
        size: "large",
        text: "signin_with",
        shape: "rectangular",
        logo_alignment: "left",
      });
    }
  } catch (error) {
    console.error("Failed to initialize Google Auth:", error);
  }

  // Add event listeners for Google login
  window.addEventListener("google-login-success", handleGoogleLoginSuccess);
  window.addEventListener("google-login-error", handleGoogleLoginError);
});

// Cleanup event listeners on component unmount
onUnmounted(() => {
  window.removeEventListener("google-login-success", handleGoogleLoginSuccess);
  window.removeEventListener("google-login-error", handleGoogleLoginError);
});
</script>
