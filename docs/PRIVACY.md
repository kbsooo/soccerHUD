# Privacy & Security Commitments

The Soccer HUD extension is designed to operate entirely within the user's browser tab. The MVP
(and future milestones) adheres to the following principles:

1. **On-device inference only** – All computer vision models (player detection, tracking, jersey
   OCR) will execute locally using ONNX Runtime Web with WebGPU/WebGL/CPU backends. No frames,
   telemetry, or derived metadata leave the browser.
2. **No network exfiltration** – The extension does not transmit captured frames, roster data, or
   telemetry to remote services. Network access is limited to assets already present on the page
   (e.g., YouTube streams).
3. **Minimal permissions** – Manifest permissions are restricted to `activeTab` and `scripting`,
   enabling content script injection without broad host access. Additional permissions require a
   deliberate review.
4. **User-controlled data** – Roster CSV files are handled entirely in-browser. Future persistence
   will use `chrome.storage` with clear UI affordances for deletion/reset.
5. **Transparent processing** – Documentation (ARCHITECTURE.md, UX.md) clarifies what data is
   processed and how overlays are generated. Future releases will provide an in-extension privacy
   notice surfaced in the options page.

These guardrails ensure that Soccer HUD remains privacy-first and compliant with MV3 best practices.
