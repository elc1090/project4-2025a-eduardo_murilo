import { defineStore } from "pinia";

const defaultData = {
  user: null,
  authType: null, // 'traditional' or 'google'
  googleCredential: null,
};

export const getAuthStorage = () => {
  const authString = localStorage.getItem("UInify-auth");

  if (!authString) {
    return defaultData;
  }

  try {
    return JSON.parse(authString);
  } catch (error) {
    console.error("Erro ao parsear UInify-auth do localStorage:", error);
    return defaultData;
  }
};

export const useAuthStore = defineStore("UInify-auth", {
  state: () => ({ authData: getAuthStorage() }),
  getters: {
    storeAuthDataGetter(state) {
      return state.authData;
    },
    isAuthenticated(state) {
      return !!state.authData?.user;
    },
    authType(state) {
      return state.authData?.authType;
    },
    isGoogleAuth(state) {
      return state.authData?.authType === 'google';
    },
    userInfo(state) {
      return state.authData?.user;
    },
  },
  actions: {
    storageAuthSave(auth) {
      this.authData = auth;
      localStorage.setItem("UInify-auth", JSON.stringify(this.authData));
    },
    storageAuthSaveGoogle(googleUserInfo, credential, backendUserData = null) {
      const authData = {
        user: {
          id: backendUserData?.id || googleUserInfo.sub, // Use backend ID if available
          username: googleUserInfo.email,
          email: googleUserInfo.email,
          name: googleUserInfo.name,
          picture: googleUserInfo.picture,
          given_name: googleUserInfo.given_name,
          family_name: googleUserInfo.family_name,
          // Include backend user data if available
          ...(backendUserData && { backendId: backendUserData.id }),
        },
        authType: 'google',
        googleCredential: credential,
      };
      this.authData = authData;
      localStorage.setItem("UInify-auth", JSON.stringify(this.authData));
    },
    storageAuthRemove() {
      this.authData = defaultData;
      localStorage.removeItem("UInify-auth");
    },
  },
});
