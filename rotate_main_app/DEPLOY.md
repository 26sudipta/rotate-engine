# Demo deployment

The demo is deployed as two services:

1. **API:** Render Web Service from the repository root, using `render.yaml`.
2. **Frontend:** Vercel project rooted at `rotate_main_app/client`.

## Render API

Connect the GitHub repository in Render and apply the `render.yaml` blueprint. The service uses:

- Build command: `npm ci`
- Start command: `npm start`
- Health check: `/api/health`

After the service is created, copy its public URL, for example:

```text
https://rotate-api.onrender.com
```

## Vercel frontend

Create a Vercel project from the same repository with **Root Directory** set to `rotate_main_app/client`.

Set this production environment variable before deploying:

```text
VITE_API_URL=https://rotate-api.onrender.com/api
```

The `vercel.json` rewrite keeps React Router routes working on direct navigation and refresh.

This deployment uses the current demonstration dataset from the Express API. The frontend is not yet wired to the Python engine contract.
