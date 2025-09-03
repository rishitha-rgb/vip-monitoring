def run_dashboard(results):
    print("Dashboard:")
    for post, status in results.items():
        print(f"{post} -> {status}")
