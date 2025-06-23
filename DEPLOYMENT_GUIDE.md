# Production Deployment Guide

## 🚀 Docker Hub Production Deployment

**Project:** Emotion-Responsive Food Ordering System
**Collaboration:** eyeAI.solutions
**Docker Hub:** sam2425/food_recomender-frontend, sam2425/food_recomender-backend

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Minimum 4GB RAM (8GB recommended)
- 10GB+ storage space
- Domain name (for production)

## 🔧 Quick Start Deployment

### 1. Download Production Files
```bash
# Clone the repository or download these files:
# - docker-compose.prod.yml
# - env.prod.example

# Or create a new directory for deployment
mkdir food-recommender-prod
cd food-recommender-prod

# Download the production compose file
curl -O https://raw.githubusercontent.com/yourusername/food_recomender/main/docker-compose.prod.yml
curl -O https://raw.githubusercontent.com/yourusername/food_recomender/main/env.prod.example
```

### 2. Configure Environment
```bash
# Copy environment template
cp env.prod.example .env.prod

# Edit with your production values
nano .env.prod
```

### 3. Create Required Directories
```bash
# Create volume directories
mkdir -p volumes/{postgres,redis,backend_logs,experiment_data,face_images,pgadmin,nginx_logs}

# Set permissions
chmod -R 755 volumes/
```

### 4. Deploy Application
```bash
# Pull latest images and start services
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Check service status
docker-compose -f docker-compose.prod.yml ps
```

## 🌐 Production Configurations

### Minimal Production Setup
```bash
# Start core services only
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d db redis backend frontend
```

### Full Production with Admin Tools
```bash
# Start all services including pgAdmin
docker-compose -f docker-compose.prod.yml --profile admin --env-file .env.prod up -d
```

### Production with Reverse Proxy
```bash
# Start with nginx reverse proxy
docker-compose -f docker-compose.prod.yml --profile proxy --env-file .env.prod up -d
```

## 🔒 Security Configuration

### Required Environment Variables
```bash
# Generate secure keys
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -hex 16)

# Update .env.prod with generated values
```

### SSL/TLS Setup (with nginx profile)
```bash
# Create SSL directory
mkdir -p nginx/ssl

# Place your SSL certificates
cp your-domain.crt nginx/ssl/
cp your-domain.key nginx/ssl/

# Create nginx config
cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:80;
    }

    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/your-domain.crt;
        ssl_certificate_key /etc/nginx/ssl/your-domain.key;

        location /api/ {
            proxy_pass http://backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location / {
            proxy_pass http://frontend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
EOF
```

## 📊 Monitoring & Health Checks

### Service Health Status
```bash
# Check all services
docker-compose -f docker-compose.prod.yml ps

# Check service logs
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend
docker-compose -f docker-compose.prod.yml logs db

# Monitor resource usage
docker stats
```

### Application Health Endpoints
- Backend Health: `http://localhost:8000/health`
- Frontend: `http://localhost:3000`
- Database: PostgreSQL on port 5432
- Redis: Redis on port 6379
- pgAdmin: `http://localhost:5050` (with admin profile)

## 🔄 Updates & Maintenance

### Update Application Images
```bash
# Pull latest images
docker-compose -f docker-compose.prod.yml pull

# Restart with new images
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --force-recreate
```

### Backup Data
```bash
# Backup database
docker exec food-recommender-db pg_dump -U postgres food_recommender_prod > backup_$(date +%Y%m%d).sql

# Backup experiment data
tar -czf experiment_data_backup_$(date +%Y%m%d).tar.gz volumes/experiment_data/

# Backup face images (if using)
tar -czf face_images_backup_$(date +%Y%m%d).tar.gz volumes/face_images/
```

### Restore Data
```bash
# Restore database
docker exec -i food-recommender-db psql -U postgres food_recommender_prod < backup_20240101.sql

# Restore experiment data
tar -xzf experiment_data_backup_20240101.tar.gz -C volumes/
```

## 🚨 Troubleshooting

### Common Issues

1. **Backend Not Starting**
   ```bash
   # Check logs
   docker-compose -f docker-compose.prod.yml logs backend

   # Common fixes:
   # - Verify DATABASE_URL format
   # - Ensure database is healthy
   # - Check volume permissions
   ```

2. **Database Connection Issues**
   ```bash
   # Test database connectivity
   docker exec food-recommender-db pg_isready -U postgres

   # Check database logs
   docker-compose -f docker-compose.prod.yml logs db
   ```

3. **Frontend Not Loading**
   ```bash
   # Check if backend is accessible
   curl http://localhost:8000/health

   # Verify environment variables
   docker exec food-recommender-frontend env | grep REACT_APP
   ```

4. **Out of Memory Issues**
   ```bash
   # Reduce backend workers
   export BACKEND_WORKERS=2

   # Monitor memory usage
   docker stats --no-stream
   ```

### Performance Optimization

1. **Resource Limits**
   ```bash
   # Adjust in docker-compose.prod.yml
   deploy:
     resources:
       limits:
         memory: 2G
         cpus: '1'
   ```

2. **Database Tuning**
   ```bash
   # Add to postgres environment
   POSTGRES_SHARED_PRELOAD_LIBRARIES=pg_stat_statements
   POSTGRES_MAX_CONNECTIONS=200
   POSTGRES_SHARED_BUFFERS=256MB
   ```

## 🌐 Production Deployment Examples

### AWS EC2 Deployment
```bash
# Launch EC2 instance (t3.large or larger)
# Install Docker and Docker Compose
# Configure security groups (ports 80, 443, 22)

# Deploy on EC2
git clone https://github.com/yourusername/food_recomender.git
cd food_recomender
cp env.prod.example .env.prod
# Update .env.prod with production values
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

### DigitalOcean Droplet
```bash
# Create droplet (4GB+ RAM)
# One-click Docker installation
# Configure domain DNS

# Deploy
curl -sSL https://raw.githubusercontent.com/yourusername/food_recomender/main/docker-compose.prod.yml -o docker-compose.prod.yml
# Configure and deploy
```

### Local Development with Production Images
```bash
# Use production images for local testing
export REACT_APP_API_URL=http://localhost:8000
export ALLOWED_ORIGINS=http://localhost:3000
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

## 🔧 Advanced Configuration

### Multi-Environment Setup
```bash
# staging.env
ENVIRONMENT=staging
POSTGRES_DB=food_recommender_staging

# production.env
ENVIRONMENT=production
POSTGRES_DB=food_recommender_prod

# Deploy to staging
docker-compose -f docker-compose.prod.yml --env-file staging.env up -d
```

### Load Balancing
```bash
# Scale backend instances
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# Use external load balancer (nginx, traefik, etc.)
```

## 📈 Research & Analytics

### Experiment Data Collection
- Experiment data: `volumes/experiment_data/`
- Face recognition data: `volumes/face_images/`
- Application logs: `volumes/backend_logs/`

### Data Export
```bash
# Export experiment data
docker exec food-recommender-backend python -c "
import pandas as pd
from app.db import get_db
# Export logic here
"

# CSV export
docker cp food-recommender-backend:/app/data/experiments.csv ./
```

## 🤝 Support & Collaboration

**Developed in collaboration with eyeAI.solutions**

For support:
- Check logs: `docker-compose logs service_name`
- Review health endpoints
- Verify environment configuration
- Contact: support@eyeai.solutions

---

**Status:** ✅ Production Ready
**Last Updated:** January 2025
**Version:** 1.0.0