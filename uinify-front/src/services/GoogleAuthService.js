import { Environment } from "src/environment/environment";

/**
 * Google Authentication Service
 * Handles Google OAuth2 login/logout functionality
 */
export class GoogleAuthService {
  constructor() {
    this.isInitialized = false;
  }

  /**
   * Initialize Google OAuth2
   * @returns {Promise<boolean>} Success status
   */
  async initialize() {
    if (this.isInitialized) {
      return true;
    }

    try {
      // Check if Google Client ID is configured
      if (!Environment.googleClientId) {
        console.error("Google Client ID not configured in environment");
        return false;
      }

      // Load Google Identity Services script if not already loaded
      if (!window.google) {
        await this.loadGoogleScript();
      }

      // Initialize Google OAuth2
      window.google.accounts.id.initialize({
        client_id: Environment.googleClientId,
        callback: this.handleCredentialResponse.bind(this),
        auto_select: false,
        cancel_on_tap_outside: true,
      });

      this.isInitialized = true;
      return true;
    } catch (error) {
      console.error("Failed to initialize Google Auth:", error);
      return false;
    }
  }

  /**
   * Load Google Identity Services script
   * @returns {Promise<void>}
   */
  loadGoogleScript() {
    return new Promise((resolve, reject) => {
      if (window.google) {
        resolve();
        return;
      }

      const script = document.createElement("script");
      script.src = "https://accounts.google.com/gsi/client";
      script.async = true;
      script.defer = true;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  /**
   * Handle Google credential response
   * @param {Object} response - Google credential response
   */
  handleCredentialResponse(response) {
    try {
      // Decode JWT token to get user info
      const userInfo = this.parseJwt(response.credential);
      
      // Trigger custom event with user data
      const event = new CustomEvent("google-login-success", {
        detail: {
          credential: response.credential,
          userInfo: userInfo,
        },
      });
      window.dispatchEvent(event);
    } catch (error) {
      console.error("Error handling Google credential response:", error);
      const event = new CustomEvent("google-login-error", {
        detail: { error },
      });
      window.dispatchEvent(event);
    }
  }

  /**
   * Parse JWT token to extract user information
   * @param {string} token - JWT token
   * @returns {Object} Parsed user information
   */
  parseJwt(token) {
    try {
      const base64Url = token.split(".")[1];
      const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split("")
          .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
          .join("")
      );
      return JSON.parse(jsonPayload);
    } catch (error) {
      console.error("Error parsing JWT token:", error);
      throw error;
    }
  }

  /**
   * Render Google Sign-In button
   * @param {string} elementId - ID of the element to render the button in
   * @param {Object} options - Button configuration options
   */
  renderButton(elementId, options = {}) {
    if (!this.isInitialized) {
      console.error("Google Auth not initialized");
      return;
    }

    const defaultOptions = {
      theme: "outline",
      size: "large",
      text: "signin_with",
      shape: "rectangular",
      logo_alignment: "left",
    };

    const buttonOptions = { ...defaultOptions, ...options };

    window.google.accounts.id.renderButton(
      document.getElementById(elementId),
      buttonOptions
    );
  }

  /**
   * Prompt Google One Tap sign-in
   */
  promptOneTap() {
    if (!this.isInitialized) {
      console.error("Google Auth not initialized");
      return;
    }

    window.google.accounts.id.prompt();
  }

  /**
   * Sign out from Google
   */
  signOut() {
    if (window.google && window.google.accounts) {
      window.google.accounts.id.disableAutoSelect();
    }
  }

  /**
   * Revoke Google access
   * @param {string} accessToken - Google access token
   */
  revokeAccess(accessToken) {
    if (window.google && window.google.accounts && accessToken) {
      window.google.accounts.oauth2.revoke(accessToken);
    }
  }
}

// Export singleton instance
export const googleAuthService = new GoogleAuthService();
