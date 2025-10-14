# Soccer HUD Extension Architecture

## Overview
The Soccer HUD Chrome extension is built as a Manifest V3 (MV3) project that runs entirely on
-device within the browser. The MVP focuses on sampling frames from an HTML5 `<video>` element on
YouTube pages, rendering an overlay canvas, and preparing the scaffolding required for on-device
player detection and tracking.

## Extension Components
- **Background service worker (`src/background/index.ts`)** – Handles lifecycle events (installation
  logging today, and future model preloading or warm-up tasks).
- **Content script (`src/content/index.ts`)** – Injects an overlay canvas, listens to messages from
the page context, and renders the heads-up display (HUD) at ~10 FPS.
- **Page script (`src/page/index.ts`)** – Runs in the page context to access the YouTube `<video>`
  element, sample frames, and forward telemetry to the content script via `window.postMessage`.
- **Options page (`src/options`)** – Hosts the roster management UI stub where CSV rosters will be
  uploaded and persisted in future milestones.

## Build Pipeline
Vite bundles the extension with the `@crxjs/vite-plugin`, producing a `dist/` folder ready for
"Load unpacked" in Chrome. The same build pipeline will later package ONNX models and WASM assets
required for on-device inference.

## Video Sampling & HUD Rendering Flow
```mermaid
flowchart LR
    YT[YouTube <video>] -- frame --> Sampler
    subgraph Page Context
      Sampler[Page sampler script]\n(src/page/index.ts)
    end
    Sampler -- window.postMessage --> Content
    subgraph Extension Context
      Content[Content script renderer]\n(src/content/index.ts)
      Overlay[Canvas overlay]
    end
    Content --> Overlay --> Viewer[Viewer]
```

1. The page script locates the YouTube `<video>` element and samples frames via
   `requestVideoFrameCallback` (with a `setTimeout` fallback) at roughly 10–15 FPS.
2. Each sample updates a hidden canvas for future ML processing and posts a `FRAME_SAMPLED` message
   to the content script.
3. The content script updates internal state, keeps the overlay sized to the video bounds, and draws
   the current HUD text using a high z-index, pointer-events-disabled canvas.
4. Future milestones will replace the static "Unknown" label with live inference results sourced
   from on-device player detection, tracking, and OCR modules.

## Data Flow & Future Integration Points
- **Roster storage** – The options page will parse CSV uploads and persist structured rosters via
  `chrome.storage.sync/local`, allowing HUD personalization per team.
- **On-device inference** – ONNX Runtime Web (WebGPU/WebGL/CPU) will be loaded inside the page
  script, leveraging the sampled frames and tracked bounding boxes to classify the ball carrier.
- **Tracking** – OC-SORT/ByteTrack will run in the page context, publishing player IDs to the content
  script to keep the HUD synchronized with visual overlays.

The architecture ensures that all computation remains within the browser tab, avoiding any network
calls or data exfiltration, and keeping permissions limited to `activeTab` and `scripting`.
