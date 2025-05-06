from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pds_data_api",
    version="0.1.0",
    author="Glenn Spiller II",
    description="A PDS Data API with Qdrant integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",  # Add your repository URL here
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "sqlalchemy==2.0.23",
        "alembic==1.12.1",
        "jinja2==3.1.2",
        "python-multipart==0.0.6",
        "requests==2.31.0",
        "qdrant-client==1.6.4",
        "openpyxl==3.1.2",
        "python-dotenv==1.0.0",
        "aiosqlite==0.19.0",
        "bcrypt==4.0.1",
        "cryptography==41.0.5",
        "pydantic==2.4.2",
        "starlette==0.27.0",
        "typing-extensions==4.8.0",
        "openai==1.12.0"
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "pds-data-api=pds_data_api.main:run_app",
        ],
    },
) 