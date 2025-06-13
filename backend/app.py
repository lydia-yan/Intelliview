from fastapi import FastAPI
from backend.api.routes import router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.include_router(router)

origins = [
    "http://localhost:3000",            # for local React dev
    "http://localhost:8080",            # for Flutter Web dev
    "http://localhost:5000",            # for Flutter Web dev
    "http://localhost",                 # for Flutter Web dev with any port
    "https://aiview-fa69f.web.app",    # for production
    "https://aiview-fa69f.firebaseapp.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],              # GET, POST, PUT, etc.
    allow_headers=["*"],              # Authorization, Content-Type, etc.
)