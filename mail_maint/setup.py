from setuptools import setup, find_packages

setup(
    name="mail_maint",
    version="0.1.0",
    description="Gmail Maintenance Tool - Automatic inbox cleaning, organizing, and backup",
    author="Your Name",
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[
        "google-auth-oauthlib>=1.0.0",
        "google-auth-httplib2>=0.1.0",
        "google-api-python-client>=2.0.0",
        "schedule>=1.2.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "beautifulsoup4>=4.12.0",
    ],
    entry_points={
        "console_scripts": [
            "mail-maint=src.main:main",
        ],
    },
)
