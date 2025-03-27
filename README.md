# 🐍 The Python Script (Backend)

```
cd backend
pip install -r requirements.txt
python main.py
```

# 💻 The Client (Frontend)


## 📦 Install the dependencies
```bash
cd frontend
npm install
```

### 🚀 Start the app in development mode (hot-code reloading, error reporting, etc.)
```bash
quasar dev -m electron
```


### 🏗️ Build the app for production
```bash
quasar build -m electron
```

### ⚙️ Customize the configuration
See [Configuring quasar.config.js](https://v2.quasar.dev/quasar-cli-vite/quasar-config-js).

## 🤔 How does this work?

> Same... I am learning along the way too

```
my-app/
├── src/               <-- Quasar/Vue frontend (your app UI lives here)
├── src-electron/      <-- Electron main process (desktop window setup)
├── public/            <-- Static files
├── quasar.conf.js     <-- Central config file
├── package.json       <-- Project dependencies & scripts
```

## 📁 Project Structure Overview

This project uses [Quasar Framework](https://quasar.dev) with [Vue 3](https://vuejs.org) for the frontend and [Electron](https://www.electronjs.org/) for desktop functionality.

---

### 📦 Root Level

- `package.json`
  Project metadata and dependencies.

- `quasar.conf.js`
  Central configuration for Quasar, including modes, plugins, boot files, build settings, and Electron options.

- `public/`
  Static assets copied directly to the final build (e.g. `favicon.ico`, icons, etc).

---

### 🎨 `/src` — Quasar + Vue Frontend

This is the main source folder for your frontend app.

- `layouts/`
  App-wide layouts that wrap your pages.
  Example: `MainLayout.vue` defines headers, footers, sidebars, etc.

- `pages/`
  Individual screens or views of your app.
  Example: `IndexPage.vue` is shown at route `/`.

- `components/`
  Reusable Vue components used across layouts or pages.
  Example: Custom buttons, cards, widgets, etc.

- `router/`
  Vue Router setup and route definitions.
  Example: `routes.js` maps paths to layouts and pages.

- `boot/` (optional)
  JS files that run at app boot time (e.g. for setting up libraries, APIs, globals).

- `assets/`
  Local images, fonts, and styles for use in components.

---

### ⚡ `/src-electron` — Electron Main Process

Handles native desktop behavior and integration with OS.

- `electron-main.js`
  Main process script for Electron.
  Responsible for creating the window, loading the Vue app, and configuring Electron APIs.
  Modify this file to:
  - Set window size/title
  - Interact with the OS
  - Spawn Python scripts or background processes

- `electron-preload.js`
  (Optional) Preload script that runs before your frontend loads.
  Used to safely expose selected Node.js APIs to the renderer when using `contextIsolation`.

