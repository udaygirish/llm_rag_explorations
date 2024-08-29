from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials  
from jose import JWTError, jwt
from fastapi import HTTPException, status
import json 
import dotenv
from datetime import datetime, timedelta   
import os  

dotenv.load_dotenv()


class Security_Helpers:
    def __init__(self):
        self.description = "Utility Class for Security Helpers "
        with open("src/data/security_db/users.json") as f:
            self.users = json.load(f)['users']
        self.secret_key = os.getenv("BACKEND_SECRET_KEY")
        self.algorithm = os.getenv("BACKEND_ALGORITHM")
        self.access_token_expire_minutes = int(os.getenv("BACKEND_ACCESS_TOKEN_EXPIRE_MINUTES"))
        
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
        self.token_auth_scheme = HTTPBearer()
    
    # Verify User    
    def verify_user(self, username: str, password: str):
        print("Users:", self.users)
        print("Username:", username)
        print("Password:",password)
        for user in self.users:
            print("User:", user)
            if user['name'] == username and user['password'] == password:
                return True
        return False
    
    # Create JWT Token
    def create_jwt_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    # Verify JWT Token
    def verify_jwt_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
        