# Inkflow

A complete Flask blogging platform with accounts, rich-text posts, categories, tags, comments, search, and pagination.

## Features

- Registration and login with password hashing
- Create, edit, and delete published posts or drafts
- Rich-text editor
- Categories and comma-separated tags
- Comments for signed-in readers
- Search and pagination
- Responsive editorial interface

## Run locally

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Open http://127.0.0.1:5000

Set `SECRET_KEY` and `DATABASE_URL` environment variables for production use.
