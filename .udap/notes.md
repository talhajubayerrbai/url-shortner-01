# url-shortner-01 — Working Notes

## Status
- Phase: GENERATION complete → running validate_project

## Stack
- Python 3.12 / FastAPI / SQLAlchemy async / Alembic
- RDS Postgres 15 (db.t3.micro), private, not publicly accessible
- EC2 t3.micro Ubuntu 22.04 running Docker
- ALB for HTTP ingress + health checks
- Ansible deploys Docker image + runs Alembic migrations

## Key Decisions
- `asyncpg` driver for async Postgres; tests use `aiosqlite` (no Postgres needed in CI test stage)
- Code generation: 7-char alphanumeric, collision-retry up to 10 attempts
- Alembic migration runs inside Docker on the EC2 before app container starts
- ALB health check path: /health
- RDS username: dbadmin, db name: urlshortener
- No HTTPS in Tier 1 (listed as optional enhancement)

## Secrets needed
- DB_PASSWORD (set before deploy)
- SSH_PUBLIC_KEY, SSH_PRIVATE_KEY (platform-provided)
- TF_STATE_BUCKET, PROJECT_NAME (platform-provided)

## What's Done
- [x] architecture.d2
- [x] pipeline.yaml
- [x] FastAPI app (main, config, database, models, schemas, crud, router)
- [x] Alembic migrations
- [x] Dockerfile
- [x] Terraform (infra/main.tf, variables.tf, outputs.tf)
- [x] Ansible playbook
- [x] Tests (conftest, test_urls)
- [x] README, .gitignore, .env.example, requirements*.txt
- [ ] validate_project
- [ ] DB_PASSWORD secret
- [ ] create_repo_and_push
- [ ] deploy

## Gotchas
- Default VPC has 6 subnets in us-east-1 — used for RDS subnet group (needs >=2)
- RDS db subnet group requires subnets in >=2 AZs — default VPC subnets cover all AZs, fine
- pipeline.yaml build stage builds Docker image locally (no registry) — Ansible rebuilds on EC2
