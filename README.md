# PDS Data API - Docker Deployment

## Overview
PDS Data API is a FastAPI-based application for managing and syncing PDS (Product Data Service) tables. This application is designed to be deployed using Docker containers.

## System Requirements
- Docker and Docker Compose
- 2GB RAM minimum
- 1GB free disk space

## Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd pds-data-api
```

2. Create a `secrets.json` file with your API keys:
```json
{
    "openai_api_key": "your-openai-api-key"
}
```

3. Start the application:
```bash
docker compose up --build
```

The application will be available at `http://localhost:8000`

## Configuration

### Environment Variables
The application uses the following environment variables (configured in docker-compose.yml):
- `DATABASE_URL`: PostgreSQL connection string
- `PDS_HOST`: Host address (default: 0.0.0.0)
- `PDS_PORT`: Port number (default: 8000)
- `SECRET_KEY`: Application secret key
- `WORKERS`: Number of worker processes (default: 4)
- `LOG_LEVEL`: Logging level (default: WARNING)
- `LOG_FILE`: Path to log file

### Database
- PostgreSQL database runs in a separate container
- Data is persisted in a Docker volume
- Initial schema is applied automatically

### Qdrant Vector Database
- Qdrant runs as a separate service
- Configure connection in the UI:
  ```json
  {
    "host": "host.docker.internal",
    "port": 6333,
    "api_key": "your-api-key",
    "batch_size": 100,
    "https": false
  }
  ```

## Monitoring

1. View application logs:
```bash
docker compose logs -f pds_api
```

2. View database logs:
```bash
docker compose logs -f db
```

## Backup and Maintenance

1. Database backup:
```bash
docker compose exec db pg_dump -U pdsapi pds_data_api > backup.sql
```

2. Restore database:
```bash
docker compose exec -T db psql -U pdsapi pds_data_api < backup.sql
```

## Troubleshooting

1. Check container logs:
```bash
docker compose logs
```

2. Restart services:
```bash
docker compose restart
```

3. Rebuild containers:
```bash
docker compose down
docker compose up --build
```

## Security Considerations

1. All sensitive data is stored in Docker volumes
2. API keys are stored in `secrets.json`
3. Production logging is set to WARNING level
4. Database credentials are managed through Docker environment variables

## Support

For production support, contact:
- Email: support@example.com
- Documentation: /docs (available when the server is running)

## License

Copyright (c) 2024. All rights reserved. 