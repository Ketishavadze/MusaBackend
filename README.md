# Musa Backend

Backend API for **Musa**, a handmade marketplace platform where creators can open studios, publish handmade products, manage carts, and receive orders.

This repository contains the Django REST Framework backend used by the Musa frontend.

---

## Tech Stack

* Python
* Django
* Django REST Framework
* JWT Authentication
* PostgreSQL / SQLite for local development
* Django CORS Headers

---

## Main Features

* User registration and login
* JWT-based authentication
* Current user profile endpoint
* Studio creation and management
* Product/listing CRUD
* Product search and category filtering
* Favourites
* Cart management
* Order checkout flow

---

## Project Structure

```text
MusaBackend/
├── musa_backend/
│   ├── api/
│   ├── musa_backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   └── frontend_api_example.ts
└── README.md
```

---

## Local Setup

Clone the repository:

```bash
git clone https://github.com/Ketishavadze/MusaBackend.git
cd MusaBackend/musa_backend
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create an environment file:

```powershell
copy .env.example .env
```

On macOS/Linux:

```bash
cp .env.example .env
```

Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

Optional: seed demo data:

```bash
python manage.py seed_demo
```

Start the development server:

```bash
python manage.py runserver
```

The API will run at:

```text
http://127.0.0.1:8000/api/
```

---

## Demo Account

After running the seed command, you can use the demo account:

```text
email: demo@musa.com
password: password
```

---

## API Endpoints

### Authentication

```text
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/refresh/
GET  /api/auth/me/
POST /api/auth/logout/
```

### Products

```text
GET    /api/products/
GET    /api/products/?category=Crochet&search=top
GET    /api/products/?mine=true
POST   /api/products/
GET    /api/products/{id}/
PATCH  /api/products/{id}/
DELETE /api/products/{id}/
POST   /api/products/{id}/favourite/
```

### Studios

```text
GET  /api/studios/me/
POST /api/studios/me/
```

### Cart

```text
GET    /api/cart/
POST   /api/cart/
PATCH  /api/cart/{item_id}/
DELETE /api/cart/{item_id}/
```

### Orders

```text
GET  /api/orders/
POST /api/orders/
```

---

## Frontend Integration

In the Musa frontend project, create a `.env.local` file:

```text
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api
```

Then restart the frontend:

```bash
npm run dev
```

---

## Related Repository

Frontend repository:

```text
https://github.com/Hikarunnie/Musa_front
```

---

## Notes

This backend was created for the Musa product capstone project. It replaces local frontend state with real API endpoints for authentication, studios, products, favourites, cart, and checkout.

The backend supports the main Musa user flow:

1. A creator registers or logs in.
2. The creator opens a studio.
3. The creator publishes handmade products.
4. Customers browse products, add items to favourites or cart, and place orders.
5. The frontend communicates with this backend through REST API endpoints.
