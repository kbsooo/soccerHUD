# Soccer HUD User Experience

## HUD Layout
- **Primary badge** – A semi-transparent pill anchored to the top-left of the video canvas displays
  "Ball Carrier: Unknown" in the MVP. The badge size scales with the video resolution, maintaining
  readable typography on 720p–4K streams.
- **Status line** – A secondary line provides debug-friendly timing (e.g., last frame sampled). This
  will evolve into confidence metrics or assistive hints once detection is integrated.
- **Non-invasive overlay** – The canvas respects pointer events (disabled) and uses a very high
  `z-index` to stay above the player but below native YouTube controls.

## Density & Controls (Roadmap)
- **Compact vs. Detailed modes** – Future releases will allow toggling between a lightweight badge
  and a richer panel with player statistics. Density control will likely reside in the options page
  and sync per user.
- **Positioning** – Users will be able to drag or choose predefined quadrants to avoid obstructing
  important gameplay. The MVP keeps a fixed top-left alignment for simplicity.
- **Roster awareness** – Once roster CSV ingestion is wired up, the HUD will display player names,
  jersey numbers, and team colors derived from uploaded metadata.
- **Debug mode** – A developer toggle will expose bounding boxes, tracking IDs, and performance
  metrics to aid future ML iteration.

## Interaction Model
- The HUD remains purely informational in the MVP; no in-video interactions are required.
- Options and future toggles are surfaced through the extension options page to keep the content
  script lightweight and minimize runtime overhead.
