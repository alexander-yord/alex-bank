from fastapi import FastAPI
from dependencies import database as db
from routers import myaccount, login, signup, account
from fastapi.middleware.cors import CORSMiddleware

# DB connection and cursor
cnx = db.cnx
cursor = db.cursor
db.verify_connection()

app = FastAPI(root_path="/api")

app.include_router(signup.router)
app.include_router(login.router)
app.include_router(myaccount.router)
app.include_router(account.router)

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

