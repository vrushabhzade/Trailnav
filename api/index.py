"""
Vercel Serverless Entrypoint.
Vercel looks for `api/index.py` natively so we don't need customized `vercel.json` rewrites
for the backend, which often break HTTP POST methods.
"""
from main import app

# Vercel needs the exact variable 'app' available in this file.
