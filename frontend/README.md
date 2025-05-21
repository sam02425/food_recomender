# Emotion-Responsive Food Ordering & Recommendation System

This is a React-based web app for emotion-responsive food ordering and recommendation, designed for easy deployment on [Hugging Face Spaces](https://huggingface.co/spaces).

## Features
- User-facing food ordering flow (no experiment UI shown to users)
- Real-time mood tracking (admin-only, invisible to users)
- Admin-only experiment report with mood timeline, durations, and export (JSON/CSV)
- Simple password protection for admin report

## Deploying on Hugging Face Spaces

1. **Create a new Space**
   - Go to [Hugging Face Spaces](https://huggingface.co/spaces) and create a new Space.
   - Choose **"Static"** as the Space type.

2. **Upload your code**
   - Upload all files in the `frontend/` directory (including `public/`, `src/`, `package.json`, etc.) to the root of your Space repository.

3. **Configure build settings**
   - Hugging Face Spaces will automatically detect the React app and run `npm install` and `npm run build`.
   - The build output in `build/` will be served as a static site.

4. **(Optional) SPA Routing**
   - To support client-side routing (e.g., `/report`), add a file at `public/_redirects` with this content:
     ```
     /*    /index.html   200
     ```
   - This ensures all routes are handled by React Router.

5. **Admin Access**
   - The experiment report at `/report` is protected by a simple password prompt.
   - Default password: `admin123` (change in `src/components/ExperimentReport.jsx` for production).

6. **face-api.js Models**
   - Download the [face-api.js models](https://github.com/justadudewhohacks/face-api.js-models) and place them in `public/models/`.
   - The app expects models at `/models` (e.g., `/models/face_expression_model-weights_manifest.json`).

## Local Development

```bash
cd frontend
npm install
npm start
```

## Customization
- Change the admin password in `src/components/ExperimentReport.jsx`.
- Update branding, colors, or add more admin analytics as needed.

---

**For questions or support, open an issue or contact the project maintainer.**