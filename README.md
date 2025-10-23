# AI Image Text Editor (Fullstack)

This project lets users upload AI-generated images (DALL·E, Midjourney, Stable Diffusion, etc.). The backend analyzes the image with OCR to detect text elements and estimates font size and color. The frontend provides a Canva-like editor to edit text content, font, color, and position, and export the final image.

- Frontend: React + Vite + Tailwind CSS + Konva
- Backend: Django REST Framework
- OCR: Tesseract (via pytesseract)
- Font detection: lightweight serif vs sans-serif heuristic mapped to common fonts
- Color extraction: adaptive threshold + foreground pixel average
- Storage: Cloudinary (optional) or local media
- Database: PostgreSQL (optional via DATABASE_URL) or SQLite fallback

## Quick Start

Prerequisites:
- Python 3.10+
- Node.js 18+
- Tesseract OCR installed and available on PATH (`tesseract --version`)
- PostgreSQL (optional) if you want to use DATABASE_URL instead of sqlite
- Cloudinary account (optional) for image storage

### 1) Backend setup

```
cd backend
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` in backend folder:
```
DJANGO_SECRET_KEY=change-me
DEBUG=1
ALLOWED_HOSTS=*
# Optional: PostgreSQL
# DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/DBNAME
# Optional: Cloudinary (enables remote storage)
# CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
```

Run migrations and start the server:
```
python manage.py migrate
python manage.py runserver
```

API:
- POST /api/upload/ (multipart: image) → returns detected elements and image id
- GET /api/images/<id>/
- PUT /api/images/<id>/ (JSON: { elements: [...] }) → save edits

### 2) Frontend setup

```
cd frontend
npm install
npm run dev
```

The dev server proxies `/api` to `http://localhost:8000` (configure in `vite.config.js`).

### 3) Demo Flow

1. Start backend on port 8000.
2. Start frontend on port 5173.
3. Visit http://localhost:5173, upload an image with visible text.
4. Edit detected text layers: content, font, size, color, position.
5. Click "Download PNG" to export, or "Save" to persist layer data in the backend.

## Notes on Accuracy

- OCR uses Tesseract; image quality heavily impacts detection quality.
- Font family is estimated via a heuristic (serif vs sans-serif) and mapped to common fonts (Times New Roman or Arial). Users can adjust in the editor.
- Font size is approximated from bounding box height.
- Text color is computed from a foreground mask within the text bounding box.

## Production Considerations

- Set DEBUG=0 and provide proper ALLOWED_HOSTS.
- Use PostgreSQL via DATABASE_URL.
- Provide CLOUDINARY_URL to store images remotely.
- Put Django behind a production server (gunicorn/uvicorn + nginx).
- Serve the frontend as a static build (npm run build) or via a CDN.

## Troubleshooting

- Ensure Tesseract is installed and accessible by pytesseract.
- If Cloudinary is not configured, files are stored locally under `backend/media/`.
- If OCR returns few elements, adjust image contrast or try a higher-resolution input.

## Repository Structure

- /backend: Django REST API + image analysis
- /frontend: React editor