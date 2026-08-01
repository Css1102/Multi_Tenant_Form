# Multi-Tenant Dynamic Form Engine

An enterprise-grade, headless backend architecture featuring schema-less JSONB validation, strict multi-tenant data isolation, and asynchronous chunked file streaming. Built with FastAPI and PostgreSQL.

## 🚀 Quick Start (One-Click Deploy)

This project is fully containerized. You do not need Python or PostgreSQL installed on your local machine to run it—only Docker.

**1. Clone the repository:**
`git clone https://github.com/yourusername/multi-tenant-form-engine.git`
`cd multi-tenant-form-engine`

**2. Spin up the cluster:**
`docker compose up --build -d`

**3. Explore the API:**
Open your browser and navigate to the auto-generated Swagger UI:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

*The FastAPI server will automatically connect to the PostgreSQL container, execute the schema migrations, and prepare the endpoints for testing.*