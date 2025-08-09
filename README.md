# Virtual Notice Board - FastAPI Backend

## Features
- Firebase Authentication Integration
- Role-based Access Control (admin/student/faculty)
- Advanced Filtering, Pagination, Search
- PostgreSQL with Railway support
- Automatic Timestamps, Notice Expiration, Priority System
- CORS Configuration for frontend integration
- Comprehensive Error Handling

## Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── notice.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── notice.py
│   │   └── user.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── notices.py
│   │   └── users.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py
│   │   └── firebase.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── requirements.txt
├── .env.example
└── README.md
```

## Getting Started

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up PostgreSQL database (locally or on Railway)
4. Configure environment variables
5. Set up Firebase project and download credentials
6. Run migrations: `alembic upgrade head` (optional, tables auto-create)
7. Start development server: `uvicorn app.main:app --reload`

## Railway Deployment
- Add PostgreSQL service in Railway dashboard
- Set environment variables (see `.env.example`)
- Deploy with Railway

## API Endpoints
See code for detailed endpoints and usage.
