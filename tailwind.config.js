/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./accounts/templates/**/*.html",
    "./admin_portal/templates/**/*.html",
    "./dashboard/templates/**/*.html",
    "./tickets/templates/**/*.html",
    "./accounts/**/*.py",
    "./admin_portal/**/*.py",
    "./dashboard/**/*.py",
    "./tickets/**/*.py",
  ],
  theme: {
    extend: {
      colors: {
        premierBlue: "#233893",
        premierBlueDeep: "#18296e",
        premierYellow: "#ffbd11",
      },
      boxShadow: {
        shell: "0 28px 70px rgba(24, 38, 89, 0.16)",
        card: "0 16px 36px rgba(24, 38, 89, 0.10)",
        soft: "0 10px 24px rgba(24, 38, 89, 0.08)",
      },
    },
  },
  plugins: [],
}
