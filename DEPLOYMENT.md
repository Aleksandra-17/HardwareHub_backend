# Deployment Guide

This guide covers different deployment methods for your FastAPI application.

## Table of Contents

- [Docker Deployment](#docker-deployment)
- [CI/CD Deployment](#cicd-deployment)
- [Production Checklist](#production-checklist)

## Docker Deployment

### Using Docker Compose (Recommended)

1. **Prepare configuration:** copy `.env.example` to `.env` and adjust values. Config is passed via docker-compose.
```bash
cp .env.example .env
cp alembic.ini.example alembic.ini
# Edit .env and alembic.ini with production values
```

2. **Build and start services:**
```bash
docker compose -f docker/docker-compose.yml up -d --build
```

3. **Check service status:**
```bash
docker compose -f docker/docker-compose.yml ps
docker compose -f docker/docker-compose.yml logs -f
```

4. **Run database migrations:**
```bash
docker compose -f docker/docker-compose.yml exec fastapi-app alembic upgrade head
```

### Using Docker only

1. **Build image:**
```bash
docker build -f docker/Dockerfile -t fastapi-app:latest .
```

2. **Run container:** use environment variables or mount config. See `docker-compose.yml` for env var names.
```bash
docker run -d \
  --name fastapi-app \
  -p 8000:8000 \
  -e POSTGRES_IP=host.docker.internal \
  -e POSTGRES_USERNAME=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DATABASE_NAME=fastapi_db \
  -e REDIS_HOST=host.docker.internal \
  -v $(pwd)/logs:/app/logs \
  fastapi-app:latest
```

## CI/CD Deployment

### GitHub Actions Setup

1. **Configure GitHub Secrets:**

Go to your repository → Settings → Secrets and variables → Actions, add:

- `SSH_PRIVATE_KEY`: Your SSH private key for server access
- `SSH_HOST`: Your server IP or domain
- `SSH_USER`: SSH username (e.g., `ubuntu`, `deployer`)
- `POSTGRES_USER`: PostgreSQL username
- `POSTGRES_PASSWORD`: PostgreSQL password
- `POSTGRES_DB`: PostgreSQL database name
- `ALEMBIC_INI`: Contents of your production `alembic.ini`
- `DOCKER_USERNAME`: (Optional) Docker Hub username
- `DOCKER_PASSWORD`: (Optional) Docker Hub password/token

2. **Prepare server:**

On your deployment server:
```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create deployment directory
sudo mkdir -p /opt/apps/fastapi-app
sudo chown $USER:$USER /opt/apps/fastapi-app
```

3. **Configure workflow:**

Edit `.github/workflows/develop.yaml` and update:
```yaml
env:
  APP_NAME: your-app-name  # Change this
  DEPLOY_PATH: /opt/apps   # Change if needed
```

4. **Deploy:**

Push to `main` branch:
```bash
git add .
git commit -m "Deploy application"
git push origin main
```

GitHub Actions will automatically:
- Run tests
- Build Docker image
- Deploy to your server
- Run health checks

## Production Checklist

Before deploying to production, ensure:

### Security

- [ ] Set strong PostgreSQL password in `.env`
- [ ] Updated database credentials
- [ ] Configured CORS origins properly
- [ ] Set up SSL/TLS certificates for HTTPS
- [ ] Configure firewall rules (only allow 80, 443, 22)
- [ ] Disable PostgreSQL remote access if not needed
- [ ] Set strong Redis password if exposed

### Configuration

- [ ] Configure proper database connection pooling
- [ ] Set appropriate log levels
- [ ] Configure Redis connection
- [ ] Update Nginx configuration if using custom domain
- [ ] Set proper CORS origins

### Infrastructure

- [ ] Database backups configured
- [ ] Log rotation configured
- [ ] Monitoring and alerting set up
- [ ] Health check endpoints working
- [ ] Nginx reverse proxy configured
- [ ] SSL certificates installed and renewed automatically
- [ ] Sufficient disk space allocated

### Performance

- [ ] Adjust uvicorn workers count based on CPU cores
- [ ] Configure database connection pool size
- [ ] Set up Redis for caching
- [ ] Enable gzip compression in Nginx
- [ ] Configure static file serving

### Testing

- [ ] All tests passing
- [ ] Load testing completed
- [ ] Health check endpoint responding
- [ ] Database migrations tested
- [ ] Rollback procedure tested

## Monitoring

### Health Check

Application exposes a health check endpoint:
```bash
curl http://localhost:8000/health
```

### Logs

#### Docker:
```bash
docker compose -f docker/docker-compose.yml logs -f fastapi-app
```

### Service Status

#### Docker:
```bash
docker compose -f docker/docker-compose.yml ps
```

## Rollback

### Docker Deployment

```bash
# Stop current version
docker compose -f docker/docker-compose.yml down

# Checkout previous version
git checkout <previous-commit>

# Rebuild and start
docker compose -f docker/docker-compose.yml up -d --build
```

## Scaling

### Horizontal Scaling

For load balancing multiple instances:

1. Run multiple containers on different ports
2. Configure Nginx upstream:

```nginx
upstream fastapi_cluster {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
}
```

### Vertical Scaling

Adjust worker processes in production:

```ini
# In your start script or service file
uvicorn app.main:app --workers 8
```

Rule of thumb: `workers = (2 x CPU cores) + 1`

## Troubleshooting

### Application won't start

1. Check logs: `docker compose logs -f fastapi-app`
2. Verify `.env` or env vars are set correctly
3. Check database connectivity
4. Ensure port 8000 is not in use

### Database connection errors

1. Verify database is running
2. Check database credentials in `.env` or docker-compose
3. Ensure database accepts connections
4. Test connection manually: `psql -h localhost -U postgres -d fastapi_db`

### High memory usage

1. Reduce number of workers
2. Adjust database connection pool size
3. Check for memory leaks in application code
4. Monitor with `docker stats` or `htop`

## Support

For issues or questions:
- Check application logs
- Review configuration files
- Consult FastAPI documentation: https://fastapi.tiangolo.com/
- Check Docker documentation: https://docs.docker.com/

