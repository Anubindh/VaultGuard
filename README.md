# VaultGuard – Intelligent Backup & Recovery System

VaultGuard is a Flask-based backup and recovery application designed to securely store files, maintain backup versions, verify file integrity, and restore files when needed.

The project demonstrates essential data protection concepts such as automated integrity verification, version tracking, backup monitoring, and recovery.

## Features

- **File Backup:** Upload and securely store files.
- **Version Tracking:** Maintain multiple backup versions of files.
- **SHA-256 Integrity Verification:** Verify whether stored backups have been modified or corrupted.
- **File Recovery:** Download verified backups when recovery is required.
- **Backup Health Monitoring:** Identify healthy, corrupted, and missing backups.
- **Activity Logs:** Track backup, verification, and recovery activities.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web application framework |
| SQLite | Database |
| HTML | Frontend structure |
| CSS | User interface styling |
| SHA-256 | File integrity verification |
| Git & GitHub | Version control |

## How It Works

1. Upload a file through the VaultGuard interface.
2. The application stores the backup and calculates its SHA-256 hash.
3. Backup versions are tracked in the database.
4. The application verifies file integrity using the stored hash.
5. The Backup Health page displays the status of stored backups.
6. Verified backups can be downloaded through the recovery feature.

## Project Structure

```text
VaultGuard/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── backups/
│
├── static/
│   └── style.css
│
└── templates/
    ├── index.html
    ├── recovery.html
    ├── health.html
    └── activity.html
```

*Note: The local database and backup files are excluded from the GitHub repository.*

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Anubindh/VaultGuard.git
```

### 2. Navigate to the project directory

```bash
cd VaultGuard
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
python app.py
```

Open the local URL displayed in your terminal (typically `http://127.0.0.1:5000/`).

<img width="1880" height="902" alt="Screenshot 2026-11-08 115604" src="https://github.com/user-attachments/assets/36bba87a-c2f3-4767-a121-d77e5d8803c4" />

<img width="1877" height="911" alt="Screenshot 2026-11-08 115623" src="https://github.com/user-attachments/assets/f36f8c54-2972-48af-a0ae-d7f7fc0e6cdf" />



## Learning Outcomes

- Understanding file backup and recovery workflows.
- Implementing SHA-256-based integrity verification.
- Working with Flask and SQLite.
- Managing file versions.
- Building a web-based monitoring dashboard.
- Using Git and GitHub for project management.

## Future Improvements

- Cloud storage integration.
- Scheduled automatic backups.
- User authentication and access control.
- Email notifications for backup failures.
- Advanced backup analytics.

## Disclaimer

VaultGuard is an educational project developed to demonstrate backup, file integrity, monitoring, and recovery concepts. It is not intended to replace an enterprise-grade backup and disaster recovery solution.

## Author

**Anubindh P**

GitHub: [@Anubindh](https://github.com/Anubindh)
