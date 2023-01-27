# webgui

WebGUI for Restweet written in Vue3 + Typescript


## Project Setup

```sh
npm install
```

The vite config file has to be addapted to your local configuration

open
```
vite.config.ts
```
and set the proxy so that they redirect to your api servers

You have to launch the storage_server and the collector_server to make full use of the UI

```
cd Restweetution/restweetution/server/
SYSTEM_CONFIG="path/to/your/config.yaml" uvicorn app:collecor_server
SYSTEM_CONFIG="path/to/your/config.yaml" uvicorn app:storage_server
```


### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Type-Check, Compile and Minify for Production

```sh
npm run build
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```


