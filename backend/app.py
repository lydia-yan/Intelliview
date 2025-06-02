from fastapi import FastAPI
from backend.api.routes import router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.include_router(router)

origins = [
    "http://localhost:3000",        # for local React dev
    "https://your-frontend-domain.com"  # for production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],              # GET, POST, PUT, etc.
    allow_headers=["*"],              # Authorization, Content-Type, etc.
)