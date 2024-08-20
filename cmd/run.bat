set env=development
call venv\Scripts\activate
uvicorn app.main:app --reload
