# 🚀 FastAPI Boilerplate
Boilerplate to start fastapi application

## 🧱 Project Structure

your-project-root/
│
├── app/
│ ├── main.py # FastAPI entry point
│ └── core/
│ └── logging_config.py # Central logging config
│
├── .devcontainer/ # DevContainer settings for VS Code
│ └── devcontainer.json
│
├── Dockerfile
├── requirements.txt
├── .env
├── .gitignore
└── README.md


---

## 🚀 Getting Started

### Update env file


### 🧪 Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run FastAPI app
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload


# Build Docker image
docker build -t fastapi-app .

# Run container
docker run -p 8000:8000 --env-file .env fastapi-app
Note: You can customize log paths, ports, and environment using .env.


💻 DevContainers (VS Code)
Install DevContainers extension

Open the folder in VS Code

Hit F1 → Remote-Containers: Reopen in Container

That’s it! All your tools, dependencies, and environment are ready.