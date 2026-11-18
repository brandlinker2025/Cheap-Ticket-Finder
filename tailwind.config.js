/** Built Tailwind CSS (replaces cdn.tailwindcss.com). Rebuild: npm run build:css */
module.exports = {
  content: ["./**/*.html", "./js/**/*.js", "!./node_modules/**"],
  theme: {
    extend: {
      colors: {
        "ctf-grayblue": "#B5C2D1",  // backgrounds / neutral sections
        "ctf-slate": "#41677B",     // headings, brand name, important text
        "ctf-plum": "#473D5B",      // footer, borders, dark accents
        "ctf-lavender": "#8C7392",  // cards / secondary containers
        "ctf-peach": "#D98C8B"      // call-to-action / booking buttons
      }
    }
  },
  plugins: []
};
