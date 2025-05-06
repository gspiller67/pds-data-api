# PDS Data API - Production Deployment

## Overview
PDS Data API is a FastAPI-based application for managing and syncing PDS (Product Data Service) tables. This document provides instructions for deploying the application in a production environment.

## System Requirements
- Python 3.9 or higher
- SQLite 3.x
- 2GB RAM minimum
- 1GB free disk space

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```env
DATABASE_URL=sqlite:///pds_data.db
PDS_HOST=127.0.0.1
PDS_PORT=8000
LOG_LEVEL=WARNING
SECRET_KEY=your-secure-secret-key
```

4. Initialize the database:
```bash
python init_db.py
```

## Running in Production

1. Start the application:
```bash
uvicorn pds_data_api.main:app --host 127.0.0.1 --port 8000 --workers 4
```

2. Access the application at `http://127.0.0.1:8000`

## Security Considerations

1. The application defaults to localhost-only access
2. All passwords and sensitive data are encrypted
3. Production logging is set to WARNING level
4. Database file permissions should be restricted

## Monitoring

1. Application logs are written to `pds_data_api.log`
2. Monitor disk space for database growth
3. Check log files for warnings and errors

## Backup and Maintenance

1. Regular database backup:
```bash
sqlite3 pds_data.db ".backup 'backup.db'"
```

2. Log rotation:
- Configure your system's logrotate or equivalent
- Keep 30 days of logs by default

## Troubleshooting

1. Check the log file at `pds_data_api.log`
2. Verify database connectivity
3. Ensure all required ports are accessible
4. Check file permissions

## Support

For production support, contact:
- Email: support@example.com
- Documentation: /docs (available when the server is running)

## Security Updates

- Subscribe to security notifications
- Regularly update dependencies
- Monitor for CVEs in dependencies

## License

Copyright (c) 2024. All rights reserved. 