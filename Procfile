worker: python sender.py --loop
api: uvicorn web_manager:app --host 0.0.0.0 --port ${PORT:-8000}
