# Digital Products eCommerce (MVP)

Stack:
- Backend: Django 4, DRF, Postgres, Jazzmin, SimpleJWT, Cloudinary
- Frontend: React (Vite), Tailwind, Axios, React Router
- Dev: Docker + docker-compose

Ports:
- Backend: 8000
- Frontend: 5173

## Setup

1. Copy `.env.example` to `.env` and update values.
2. Run:
   ```
   docker-compose up --build
   ```
3. Access:
   - Backend: http://localhost:8000
   - Frontend: http://localhost:5173

## Features

- Signup with email OTP (6-digit, 5 min expiry, 3 attempts, 30s resend cooldown)
- Login via JWT
- Products list and detail
- Orders: Buy -> Pending -> Admin Approve -> Email link -> Dashboard shows link
- Secure Cloudinary signed URL (7-day expiry, 3 downloads)
- Admin via Jazzmin: manage products, orders, logs
- Forgot password via email link and token confirmation

## Environment

See `.env.example` for all keys.

## Testing

Run Django tests (to be extended):
```
docker-compose exec backend python manage.py test
```