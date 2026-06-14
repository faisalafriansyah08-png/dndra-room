# Hotel Booking System - Backend API

Sistema booking hotel dengan fitur pembayaran digital, manajemen kamar, dan customer support.

## 🚀 Features

- ✅ Autentikasi User (JWT)
- ✅ Manajemen Kamar (CRUD)
- ✅ Sistem Booking dengan cek ketersediaan
- ✅ Integrasi Payment Gateway (Xendit/Midtrans)
- ✅ Sistem Promo/Diskon
- ✅ Customer Support Ticketing
- ✅ Email Notifications
- ✅ Role-based Access Control
- ✅ API Documentation (Swagger)

## 📋 Requirements

- Python 3.11+
- PostgreSQL 13+
- Redis (optional, untuk caching)

## 🔧 Installation

### 1. Clone & Setup

```bash
# Clone repository
git clone <repo-url>
cd hotel-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env dengan konfigurasi Anda
nano .env
```

### 3. Setup Database

```bash
# Create PostgreSQL database
createdb hotel_db

# Run migrations
alembic upgrade head
```

### 4. Run Development Server

```bash
# Using Make
make dev

# Or directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server akan berjalan di: http://localhost:8000

## 🐳 Docker Setup

```bash
# Build containers
make docker-build

# Start containers
make docker-up

# Stop containers
make docker-down
```

## 📖 API Documentation

Setelah server berjalan, akses dokumentasi API di:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

## 🔑 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register user baru
- `POST /api/v1/auth/login` - Login dan dapatkan token
- `GET /api/v1/auth/me` - Get user info

### Rooms
- `GET /api/v1/rooms` - List semua kamar
- `GET /api/v1/rooms/{id}` - Detail kamar
- `POST /api/v1/rooms/check-availability` - Cek ketersediaan
- `POST /api/v1/rooms` - Buat kamar baru (Admin)
- `PUT /api/v1/rooms/{id}` - Update kamar (Admin)

### Bookings
- `POST /api/v1/bookings` - Buat booking
- `GET /api/v1/bookings` - List bookings
- `GET /api/v1/bookings/{code}` - Detail booking
- `PUT /api/v1/bookings/{id}` - Update status (Admin)
- `DELETE /api/v1/bookings/{id}` - Cancel booking

### Payments
- `POST /api/v1/payments/create` - Buat payment
- `POST /api/v1/payments/webhook` - Webhook dari gateway
- `GET /api/v1/payments/{booking_id}` - Status payment

### Promos
- `GET /api/v1/promos` - List promo aktif
- `POST /api/v1/promos/validate` - Validasi kode promo
- `POST /api/v1/promos` - Buat promo (Admin)

### Support
- `POST /api/v1/support` - Buat tiket support
- `GET /api/v1/support` - List tiket
- `PUT /api/v1/support/{id}` - Update tiket (Admin)

## 🗄️ Database Schema

Database menggunakan PostgreSQL dengan tabel:
- `users` - Data pengguna
- `rooms` - Data kamar hotel
- `bookings` - Data pemesanan
- `payments` - Data pembayaran
- `promos` - Data promo/diskon
- `support_messages` - Tiket customer support

## 🛠️ Development

### Create Migration

```bash
# Auto-generate migration
make create-migration

# Or manually
alembic revision --autogenerate -m "description"

# Apply migration
make upgrade
```

### Run Tests

```bash
make test
```

## 📦 Project Structure

```
hotel-backend/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   ├── utils/           # Helper functions
│   ├── config.py        # Configuration
│   ├── database.py      # Database setup
│   ├── dependencies.py  # FastAPI dependencies
│   └── main.py          # Main application
├── alembic/             # Database migrations
├── tests/               # Unit tests
├── .env                 # Environment variables
├── requirements.txt     # Python dependencies
├── Dockerfile
├── docker-compose.yml
└── Makefile
```

## 🔐 Security

- Password hashing menggunakan bcrypt
- JWT untuk autentikasi
- HTTPS/TLS untuk production
- Input validation dengan Pydantic
- SQL injection protection dengan SQLAlchemy ORM
- CORS configuration
- Rate limiting (implementasi tambahan dengan slowapi)

## 📝 License

MIT License

## 👥 Contributors

Your Team Name

---

Untuk pertanyaan dan support, hubungi: support@yourhotel.com



📋 Penjelasan Tiap Kolom
Nama Kolom	Tipe Data	Penjelasan
id	Integer	Primary key, penanda unik setiap promo.
title	String	Nama promo. Misalnya: "Promo Akhir Tahun" atau "Diskon Spesial Kopi".
code	String(50)	Kode unik promo yang dimasukkan pengguna saat checkout. Contoh: "COFFEE20".
discount_percent	Integer	Persentase potongan harga. Misalnya 20 berarti diskon 20% dari total belanja.
discount_amount	Numeric(12,2)	Potongan harga dalam nominal tetap (bukan persen). Misalnya 20000 berarti diskon Rp20.000.
min_transaction	Numeric(12,2)	Nilai transaksi minimum agar promo bisa digunakan. Misalnya 50000 berarti promo hanya berlaku jika total belanja ≥ Rp50.000.
max_discount	Numeric(12,2)	Batas maksimum diskon yang bisa diberikan. Misalnya jika max_discount=30000, maka walau 20% dari total belanja lebih besar dari Rp30.000, diskonnya tetap dibatasi Rp30.000.
start_date	Date	Tanggal mulai promo berlaku.
end_date	Date	Tanggal berakhirnya promo.
usage_limit	Integer	Jumlah maksimum promo bisa digunakan secara total (oleh semua pengguna). Misalnya 100 berarti promo hanya bisa dipakai 100 kali.
usage_count	Integer	Jumlah promo yang sudah digunakan sejauh ini. Biasanya sistem akan menambah nilai ini tiap kali promo digunakan.
active	Boolean	Status promo aktif atau tidak (True = aktif, False = nonaktif).