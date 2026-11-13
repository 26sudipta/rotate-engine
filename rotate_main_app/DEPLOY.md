# Free demo deployment

The judge demo can run as a **single free Vercel frontend**. The client includes local demonstration data and falls back to it when the optional Express API is unavailable, so no paid backend service is needed.

## Vercel

1. Push the repository to GitHub.
2. Open [vercel.com](https://vercel.com) and sign in with GitHub.
3. Import `26sudipta/rotate-engine`.
4. Set **Root Directory** to:

   ```text
   rotate_main_app/client
   ```

5. Keep the framework as **Vite** and deploy.

No environment variable is required for the free demo. The `vercel.json` rewrite keeps React Router routes working on direct navigation and refresh.

The client build copies the committed engine outputs from `fixtures/cards_ctg.json` and
`fixtures/cards_barind.json` into the deployed static assets. The Strategies and Results pages
load those outputs and render the Python engine's cards, evidence text, scoring breakdown, and
engine provenance label. This keeps the demo free and serverless; it is a build-time snapshot,
not a live Python process.

The deployed demo uses the current illustrative/mock dataset. The Express API remains available for local development, but is not required for the public demo. The frontend is not yet wired to the Python engine contract.
