# PDS Data API Deployment Guide

## Prerequisites
- Docker and Docker Compose installed
- Git installed
- Access to the application repository

## Deployment Steps

1. Clone the repository:
```bash
git clone <repository-url>
cd pds-data-api
```

2. Set up environment variables:
```bash
cp deployment/config/.env.example deployment/config/.env
# Edit .env with your secure values
```

3. Create secrets.json:
```bash
mkdir -p config
# Create config/secrets.json with your API keys
```

4. Make the deployment script executable:
```bash
chmod +x deployment/scripts/deploy.sh
```

5. Run the deployment:
```bash
./deployment/scripts/deploy.sh
```

## Configuration

### Environment Variables
- `DB_PASSWORD`: PostgreSQL database password
- `SECRET_KEY`: Application secret key
- `PDS_HOST`: Host address (default: 0.0.0.0)
- `PDS_PORT`: Port number (default: 8000)
- `WORKERS`: Number of worker processes (default: 4)
- `LOG_LEVEL`: Logging level (default: WARNING)

### Secrets
Create `config/secrets.json` with:
```json
{
    "openai_api_key": "your-openai-api-key"
}
```

## Monitoring

1. View application logs:
```bash
docker compose -f deployment/config/docker-compose.prod.yml logs -f pds_api
```

2. View database logs:
```bash
docker compose -f deployment/config/docker-compose.prod.yml logs -f db
```

## Backup and Restore

1. Database backup:
```bash
docker compose -f deployment/config/docker-compose.prod.yml exec db pg_dump -U pdsapi pds_data_api > backup.sql
```

2. Restore database:
```bash
docker compose -f deployment/config/docker-compose.prod.yml exec -T db psql -U pdsapi pds_data_api < backup.sql
```

## Troubleshooting

1. Check service status:
```bash
docker compose -f deployment/config/docker-compose.prod.yml ps
```

2. View logs:
```bash
docker compose -f deployment/config/docker-compose.prod.yml logs
```

3. Restart services:
```bash
docker compose -f deployment/config/docker-compose.prod.yml restart
```

## Security Notes

1. Keep your `.env` file secure and never commit it to version control
2. Regularly rotate database passwords and API keys
3. Monitor logs for suspicious activity
4. Keep Docker and all dependencies updated 