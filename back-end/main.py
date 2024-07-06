from fastapi import FastAPI
from dependencies import database as db
from routers import signup, account, frontend, products, authorization
from fastapi.middleware.cors import CORSMiddleware

# DB connection and cursor
cnx = db.cnx
cursor = db.cursor
db.verify_connection()

app = FastAPI(root_path="/api")

app.include_router(authorization.router)
app.include_router(signup.router)
app.include_router(account.router)
app.include_router(products.router)
app.include_router(frontend.router)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def home():
    return {"message": "Welcome to the Alex Bank Back End API!"}

