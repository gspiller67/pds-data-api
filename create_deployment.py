#!/usr/bin/env python3
"""Create a deployment package for PDS Data API."""

import os
import shutil
import subprocess
from pathlib import Path
import sys

def create_deployment_package():
    """Create a deployment package."""
    # Define paths
    current_dir = Path(__file__).parent
    dist_dir = current_dir / 'dist'
    deployment_dir = dist_dir / 'pds_data_api'
    
    try:
        # Clean previous builds
        if dist_dir.exists():
            shutil.rmtree(dist_dir)
        
        # Create deployment directory
        deployment_dir.mkdir(parents=True)
        
        # Copy required files
        files_to_copy = [
            'requirements.txt',
            'README.md',
            'start_prod.py',
            '.env.example',
            'src/pds_data_api'
        ]
        
        for file in files_to_copy:
            src = current_dir / file
            dst = deployment_dir / file
            
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
        
        # Create empty log file
        (deployment_dir / 'pds_data_api.log').touch()
        
        # Create example environment file
        with open(deployment_dir / '.env.example', 'w') as f:
            f.write("""DATABASE_URL=sqlite:///pds_data.db
PDS_HOST=127.0.0.1
PDS_PORT=8000
LOG_LEVEL=WARNING
SECRET_KEY=generate-a-secure-key-here
WORKERS=4""")
        
        # Create deployment archive
        shutil.make_archive(
            str(dist_dir / 'pds_data_api_deployment'),
            'zip',
            deployment_dir
        )
        
        print(f"Deployment package created at: {dist_dir}/pds_data_api_deployment.zip")
        
    except Exception as e:
        print(f"Error creating deployment package: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    create_deployment_package() 