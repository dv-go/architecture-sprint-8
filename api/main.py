from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from keycloak import KeycloakOpenID
import random
import jwt
import requests
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

keycloak_url = "http://keycloak:8080"
realm_name = "reports-realm"
client_id = "reports-api"
client_secret = "oNwoLQdvJAvRcL89SydqCWCe5ry1jMgq"

keycloak_client = KeycloakOpenID(
    server_url=keycloak_url,
    realm_name=realm_name,
    client_id=client_id,
    client_secret_key=client_secret,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_public_key():
    try:
        key = keycloak_client.public_key()
        public_key = f"-----BEGIN PUBLIC KEY-----\n{key}\n-----END PUBLIC KEY-----"
        return public_key
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to retrieve public key from Keycloak: {str(e)}")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        public_key = get_public_key()
        payload = jwt.decode(token, public_key, algorithms=["RS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/reports")
def get_reports(user=Depends(get_current_user)):
    if "prothetic_user" not in user.get("realm_access", {}).get("roles", []):
        raise HTTPException(status_code=401, detail="Invalid or missing role")

    reports = [{"id": i, "name": f"Report {i}", "status": random.choice(["Completed", "In Progress", "Pending"])} for i in range(1, 6)]
    return reports
