from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "VIP Threat & Misinformation Monitoring System is running 🚀"}
