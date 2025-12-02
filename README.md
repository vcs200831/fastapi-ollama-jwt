📌 Student API with FastAPI + JWT + Ollama AI

A backend project demonstrating real-world API development with:

✔ Student CRUD APIs
✔ Secure authentication using JWT
✔ AI-powered student summary generation using Ollama (Llama3 model)

🚀 Features

Create / Read / Update / Delete Students

Login + JWT Authorization

Protected endpoints

AI summary generation using Ollama model

🛠️ Tech Stack

FastAPI

Python

JWT Authentication

Ollama (Llama3 AI Model)

Uvicorn

🔧 How to Run Locally
1️⃣ Install dependencies
pip install -r requirements.txt

2️⃣ Start Ollama Model
ollama run llama3

3️⃣ Start the API
uvicorn main:app --reload

📌 API Testing

Once running, open Swagger UI:

👉 http://127.0.0.1:8000/docs

Login using valid credentials, then access protected endpoints.

📌 Purpose of the Project

This project is built for:

Learning and interview preparation

Demonstrating skills in authentication + AI API integration

📎 Future Enhancements

✔ Docker support
✔ Database storage instead of in-memory
✔ Deployment on Render / Railway
