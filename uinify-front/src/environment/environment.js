export const Environment = {
  baseUrl:
    import.meta.env.VITE_URL_API ||
    "https://eduardomsilveira.pythonanywhere.com",
  googleClientId: import.meta.env.VITE_GOOGLE_CLIENT_ID || "",
};
