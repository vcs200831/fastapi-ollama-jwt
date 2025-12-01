from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
import sqlite3
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import List
import ollama

# -----------------------------
# JWT CONFIG
# -----------------------------
SECRET_KEY = "mysecretjwtkey123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

DB = "users.db"

# -----------------------------
# DB INIT
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT,
        password TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# -----------------------------
# Helper Functions
# -----------------------------
def get_user(username: str):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return row

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire_time})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# -----------------------------
# Pydantic Models
# -----------------------------
class RegisterModel(BaseModel):
    username: str
    email: str
    password: str

class Student(BaseModel):
    name: str
    age: int
    marks: List[int]

# -----------------------------
# AUTH ROUTES
# -----------------------------
@app.post("/register")
def register(data: RegisterModel):
    if get_user(data.username):
        raise HTTPException(400, "Username already exists")

    hashed = hash_password(data.password)

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO users(username, email, password) VALUES (?,?,?)",
              (data.username, data.email, hashed))
    conn.commit()
    conn.close()

    return {"message": "User registered successfully"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if not user:
        raise HTTPException(400, "Invalid username")

    if not verify_password(form_data.password, user[3]):
        raise HTTPException(400, "Invalid password")

    token = create_access_token({"sub": user[1]})
    return {"access_token": token, "token_type": "bearer"}

# -----------------------------
# PROTECTED ROUTE
# -----------------------------
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        return username
    except JWTError:
        raise HTTPException(401, "Invalid or expired token")

@app.get("/protected")
def protected_route(current_user: str = Depends(get_current_user)):
    return {"message": f"Hello {current_user}, you accessed a protected route!"}

# -----------------------------
# AI SUMMARY ENDPOINT (PROTECTED)
# -----------------------------
@app.post("/students/summary")
def generate_student_summary(student: Student, current_user: str = Depends(get_current_user)):
    try:
        prompt = f"""
        Create a short summary for this student:

        Name: {student.name}
        Age: {student.age}
        Marks: {student.marks}
        """

        response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}]
        )

        summary = response["message"]["content"]

        return {"summary": summary}

    except Exception as e:
        raise HTTPException(500, str(e))

# -----------------------------
# Run Locally
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=True)
