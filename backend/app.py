from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from backend.api.routes import router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = [
    "http://localhost:3000",            # for local React dev
    "http://localhost:8080",            # for Flutter Web dev
    "http://localhost:5000",            # for Flutter Web dev
    "http://localhost",                 # for Flutter Web dev with any port
    "https://aiview-fa69f.web.app",    # for production
    "https://aiview-fa69f.firebaseapp.com"
]

# Add CORS middleware BEFORE router (important!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],              # GET, POST, PUT, etc.
    allow_headers=["*"],              # Authorization, Content-Type, etc.
)

# Add global exception handler to ensure CORS headers on errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
            "Access-Control-Allow-Credentials": "true",
        }
    )

app.include_router(router)