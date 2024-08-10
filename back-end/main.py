from fastapi import FastAPI
from dependencies import database as db
from routers import signup, account, frontend, products, authorization, portal
from fastapi.middleware.cors import CORSMiddleware
import requests


def get_latest_release(repo_owner, repo_name):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    response = requests.get(url)
    if response.status_code == 200:
        latest_release = response.json()
        return latest_release['tag_name']
    else:
        raise Exception(f"Failed to fetch latest release: {response.status_code}")


try:
    repo_owner = "alexander-yord"
    repo_name = "alex-bank"
    api_version = get_latest_release(repo_owner, repo_name)
except Exception as e:
    print(f"Error: {e}")
    api_version = "v1.2.0"  # Fallback version if fetching fails

# DB connection and cursor
cnx = db.cnx
cursor = db.cursor
db.verify_connection()

app = FastAPI(root_path="/api",
              title="Alex Bank API",
              description=f"""
This API powers the Alex Bank front-end application and can be utilized independently as well. 
It provides a comprehensive set of endpoints to interact with various banking services and functionalities.

Key Points:
- Authentication: To access certain endpoints, users must authenticate by clicking the "Authorize" button. Use your Account ID as the username and enter your password.
- Authorization: Some endpoints require specific user privileges (e.g., admin, manager) which may restrict access based on your user role.
- Security: All data transmissions are encrypted to ensure the highest level of security.
- Error Handling: The API uses standard HTTP status codes to indicate the success or failure of an API request. Detailed error messages and codes are provided in the response body for troubleshooting.
- Versioning: The API follows a versioning strategy to manage updates and changes. The latest version is {api_version}. Future versions will be introduced with backward-compatible changes whenever possible.
- Documentation: Comprehensive API documentation, including endpoint details, request/response examples, and error codes, is available below.
- Source Code: The Alex Bank source code is available on <a href="https://github.com/alexander-yord/alex-bank">GitHub</a>.

Note: Unauthorized access attempts or misuse of the API may result in account suspension or termination. Please adhere to our usage guidelines and terms of service.

For support and queries, please contact our technical support team.
              """,
              version=api_version
              )

app.include_router(authorization.router)
app.include_router(signup.router)
app.include_router(account.router)
app.include_router(products.router)
app.include_router(frontend.router)
app.include_router(portal.router)

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

