# url-shortner-01

A fast, async URL shortener built with **FastAPI**, **SQLAlchemy (async)**, **Alembic**, and **PostgreSQL**. Deployed on AWS EC2 with RDS Postgres and an Application Load Balancer.

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/shorten` | Shorten a URL |
| `GET` | `/{code}` | Redirect to original URL |
| `GET` | `/stats/{code}` | Hit-count and metadata for a short code |
| `GET` | `/health` | Health check |

### POST `/shorten`

**Request body:**
```json
{
  "url": "https://example.com/very/long/path",
  "custom_code": "mycode"   // optional
}
```

**Response (201):**
```json
{
  "code": "aB3kX7m",
  "short_url": "http://your-alb.amazonaws.com/aB3kX7m",
  "original_url": "https://example.com/very/long/path",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### GET `/{code}`

Redirects (302) to the original URL. Returns 404 if the code doesn't exist.

### GET `/stats/{code}`

```json
{
  "code": "aB3kX7m",
  "original_url": "https://example.com/very/long/path",
  "created_at": "2024-01-01T00:00:00Z",
  "hit_count": 42
}
```

---

## Local Development

### Prerequisites
- Python 3.12+
- Docker & Docker Compose
- PostgreSQL (or use Docker)

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/<your-org>/url-shortner-01.git
cd url-shortner-01

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements-dev.txt

# 4. Start Postgres via Docker
docker run -d \
  --name pg-local \
  -e POSTGRES_USER=dbadmin \
  -e POSTGRES_PASSWORD=localpass \
  -e POSTGRES_DB=urlshortener \
  -p 5432:5432 \
  postgres:15

# 5. Configure environment
cp .env.example .env
# Edit .env with your local DB credentials

# 6. Run migrations
DATABASE_URL=postgresql://dbadmin:localpass@localhost:5432/urlshortener \
  alembic upgrade head

# 7. Start the server
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Run Tests

```bash
pytest tests/ -v
```

Tests use SQLite in-memory (via aiosqlite) — no Postgres required for testing.

---

## Architecture

```
User → ALB (HTTP :80) → EC2 t3.micro (Docker / FastAPI :8000) → RDS Postgres 15 (db.t3.micro)
```

- **EC2**: Ubuntu 22.04, runs the FastAPI app in Docker
- **RDS**: PostgreSQL 15, private subnet, not publicly accessible
- **ALB**: Routes traffic, performs health checks at `/health`
- **Terraform**: Manages all AWS resources in `infra/`
- **Ansible**: Deploys Docker image and runs migrations on the EC2 instance

## Infrastructure

```bash
cd infra
terraform init
terraform plan -var="project_name=url-shortner-01" -var="db_password=..." -var="ssh_public_key=..."
terraform apply
```

## Optional Enhancements (Tier 2/3)

- HTTPS/ACM certificate on the ALB
- RDS Multi-AZ for high availability
- CloudWatch alarms and dashboards
- Auto Scaling Group
- ElastiCache Redis for hot-redirect caching
- CloudFront CDN + custom domain via Route 53
