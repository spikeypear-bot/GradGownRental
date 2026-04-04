# frontend

This template should help get you started developing with Vue 3 in Vite.

## Recommended IDE Setup

[VS Code](https://code.visualstudio.com/) + [Vue (Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Recommended Browser Setup

- Chromium-based browsers (Chrome, Edge, Brave, etc.):
  - [Vue.js devtools](https://chromewebstore.google.com/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd)
  - [Turn on Custom Object Formatter in Chrome DevTools](http://bit.ly/object-formatters)
- Firefox:
  - [Vue.js devtools](https://addons.mozilla.org/en-US/firefox/addon/vue-js-devtools/)
  - [Turn on Custom Object Formatter in Firefox DevTools](https://fxdx.dev/firefox-devtools-custom-object-formatters/)

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Demo Mode

To make the admin UI easier to demo without waiting for real rental and return dates, run:

```sh
VITE_DEMO_MODE=true npm run dev
```

When enabled, the frontend surfaces eligible orders immediately for walkthroughs while backend saga and service logic stays unchanged.

## Admin Workflow Updates

- Return processing now stores split maintenance details for clean versus damaged package subsets.
- Repair queue actions send the damaged subset into the return saga so repaired items move correctly into laundry.
- Laundry and maintenance views now work against the updated maintenance detail model and order subset stages.
- Stock overview reflects the backend inventory transition updates, including backup-buffered availability and damage-log-driven damaged counts.

### Compile and Minify for Production

```sh
npm run build
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```
