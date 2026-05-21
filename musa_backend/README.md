# Musa Backend

Django REST backend for the `Hikarunnie/Musa` Next.js frontend.

The current frontend stores everything in local React state, so this backend replaces that state with real API endpoints for:

- auth: signup, login, me, refresh, logout
- products/listings: explore page, search, category filter, create listing
- studio: register seller studio and read current user's studio
- favourites: like/unlike products and list favourites
- cart: add products, update quantity, remove products
- orders: checkout with the same shipping/gift-wrap logic used by the frontend

## Setup

```bash
cd musa_backend
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Backend will run on:

```text
http://127.0.0.1:8000/api/
```

Demo login after seeding:

```text
email: demo@musa.com
password: password
```

## Frontend env

In the Next.js frontend folder, create `.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api
```

Then restart Next.js:

```bash
npm run dev
```

## Main endpoints

### Auth

```http
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/refresh/
GET  /api/auth/me/
POST /api/auth/logout/
```

Register body:

```json
{
  "name": "Nino",
  "username": "nino",
  "email": "nino@example.com",
  "password": "password123"
}
```

Login body:

```json
{
  "email": "demo@musa.com",
  "password": "password"
}
```

Auth response:

```json
{
  "user": {
    "id": 1,
    "name": "nn",
    "username": "user_nn",
    "email": "demo@musa.com",
    "isSeller": true,
    "memberSince": "2026",
    "earnings": "1240.00",
    "rating": "100.0"
  },
  "access": "jwt-access-token",
  "refresh": "jwt-refresh-token"
}
```

### Products

```http
GET    /api/products/
GET    /api/products/?category=Crochet&search=top
GET    /api/products/?mine=true
POST   /api/products/
GET    /api/products/{id}/
PATCH  /api/products/{id}/
DELETE /api/products/{id}/
POST   /api/products/{id}/favourite/
```

Create product body:

```json
{
  "title": "Handmade Ring",
  "category": "Jewelry",
  "price": "25.00",
  "description": "Silver handmade ring",
  "image": "https://example.com/ring.jpg",
  "active": true
}
```

### Studio

```http
GET  /api/studios/me/
POST /api/studios/me/
```

Create studio body:

```json
{
  "name": "Studio 138",
  "craft_type": "Crochet",
  "description": "Cozy handmade pieces."
}
```

### Cart

```http
GET    /api/cart/
POST   /api/cart/
PATCH  /api/cart/{item_id}/
DELETE /api/cart/{item_id}/
```

Add to cart body:

```json
{
  "product_id": 1,
  "qty": 1
}
```

Update quantity body:

```json
{
  "qty": 3
}
```

### Orders / Checkout

```http
GET  /api/orders/
POST /api/orders/
```

Checkout body:

```json
{
  "gift_wrap": true
}
```

The checkout logic matches the frontend:

- gift wrap costs `$2.50`
- shipping is `$5.00` when subtotal is below `$75.00`
- shipping is free at `$75.00+`
- cart is cleared after checkout

## Frontend integration helper

I included `frontend_api_example.ts`. You can copy it into the frontend, for example:

```text
musa/src/lib/api.ts
```

Then replace local functions like `login`, `addToCart`, `createProduct`, and `checkout` with API calls.
