from ingestion.ingestion import run_ingestion
from ai.ai_scoring import run_ai
from dashboard.dashboard import run_dashboard

if __name__ == "__main__":
    data = run_ingestion()
    results = run_ai(data)
    run_dashboard(results)
