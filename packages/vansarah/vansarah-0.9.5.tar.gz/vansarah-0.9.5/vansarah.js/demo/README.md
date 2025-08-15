---
title: vansarah Text-to-Speech
emoji: 🗣️
colorFrom: indigo
colorTo: purple
sdk: static
pinned: false
license: apache-2.0
short_description: High-quality speech synthesis powered by vansarah TTS
header: mini
models:
  - onnx-community/vansarah-82M-ONNX
custom_headers:
  cross-origin-embedder-policy: require-corp
  cross-origin-opener-policy: same-origin
  cross-origin-resource-policy: cross-origin
---

# vansarah Text-to-Speech

A simple React + Vite application for running [vansarah](https://github.com/mr-don88/vansarah), a frontier text-to-speech model for its size. The model runs 100% locally in the browser using [vansarah-js](https://www.npmjs.com/package/vansarah-js) and [🤗 Transformers.js](https://www.npmjs.com/package/@huggingface/transformers)!

## Getting Started

Follow the steps below to set up and run the application.

### 1. Clone the Repository

```sh
git clone https://github.com/mr-don88/vansarah.git
```

### 2. Build the Dependencies

```sh
cd vansarah/vansarah.js
npm i
npm run build
```

### 3. Setup the Demo Project

Note this depends on build output from the previous step.

```sh
cd demo
npm i
```

### 4. Start the Development Server

```sh
npm run dev
```

The application should now be running locally. Open your browser and go to [http://localhost:5173](http://localhost:5173) to see it in action.
