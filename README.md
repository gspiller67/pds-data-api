# PDS Data API

A FastAPI-based application for managing and syncing PDS (Product Data Service) tables with vector search capabilities.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- 2GB RAM minimum
- 1GB free disk space

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd pds-data-api
   ```

2. Create `secrets.json` with your API keys:
   ```json
   {
       "openai_api_key": "your-openai-api-key",
       "qdrant_api_key": "your-qdrant-api-key"
   }
   ```

3. Start the application:
   ```bash
   docker compose up --build
   ```

The application will be available at `http://localhost:8000`

## ⚙️ Configuration

### Environment Variables
Configure these in `docker-compose.yml`:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | - |
| `PDS_HOST` | Host address | 0.0.0.0 |
| `PDS_PORT` | Port number | 8000 |
| `SECRET_KEY` | Application secret key | - |
| `WORKERS` | Number of worker processes | 4 |
| `LOG_LEVEL` | Logging level | WARNING |
| `LOG_FILE` | Path to log file | - |

### Database Setup
- PostgreSQL runs in a separate container
- Data persists in a Docker volume
- Schema is automatically initialized

### Qdrant Vector Database
Configure in the UI:
```json
{
    "host": "host.docker.internal",
    "port": 6333,
    "api_key": "your-api-key",
    "batch_size": 100,
    "https": false
}
```

## 🔍 Monitoring & Maintenance

### Viewing Logs
```bash
# Application logs
docker compose logs -f pds_api

# Database logs
docker compose logs -f db
```

### Database Management
```bash
# Create backup
docker compose exec db pg_dump -U pdsapi pds_data_api > backup.sql

# Restore from backup
docker compose exec -T db psql -U pdsapi pds_data_api < backup.sql
```

## 🛠️ Troubleshooting

### Common Issues

1. **Container Issues**
   ```bash
   # View all logs
   docker compose logs

   # Restart services
   docker compose restart

   # Rebuild containers
   docker compose down
   docker compose up --build
   ```

2. **Database Issues**
   - Check database logs: `docker compose logs db`
   - Verify database connection in `docker-compose.yml`
   - Ensure database volume is properly mounted

3. **Application Issues**
   - Check application logs: `docker compose logs pds_api`
   - Verify environment variables
   - Check API key configuration in `secrets.json`

## 🔒 Security

- Sensitive data stored in Docker volumes
- API keys managed through `secrets.json`
- Production logging at WARNING level
- Database credentials via Docker environment variables
- HTTPS support for Qdrant connections

## 📚 Documentation

- API Documentation: Available at `/docs` when server is running
- Swagger UI: Available at `/redoc` when server is running

## 📞 Support

For production support:
- Email: support@example.com
- Documentation: `/docs` (when server is running)

## 📄 License

Copyright (c) 2024. All rights reserved. 