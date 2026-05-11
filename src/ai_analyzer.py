import os
import json
import glob
import requests

def analyze_with_ollama(caption):
    """Sends caption to local Ollama API for high-signal summary."""
    prompt = f"""
    Analyze the following technical Instagram caption from an AI expert.
    1. Identify the core 'Trend' or 'Concept'.
    2. Explain it like I'm 5 (ELI5).
    3. Provide a technical 'Deep Dive' for an engineer.
    4. Suggest how this impacts User Experience (UX).

    Caption: {caption}
    """
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
        )
        return response.json().get("response", "Analysis failed.")
    except Exception as e:
        return f"Error connecting to Ollama: {e}"

def run_analyzer():
    metadata_files = glob.glob("./data/raw_trends/metadata/*.json")
    insights = []

    print(f"🧠 Processing {len(metadata_files)} files with Ollama...")

    for file_path in metadata_files:
        with open(file_path, "r") as f:
            data = json.load(f)
            reel_id = data["reel_id"]
            
            print(f"🧪 Analyzing Reel: {reel_id}...")
            analysis = analyze_with_ollama(data["caption"])
            
            insights.append({
                "reel_id": reel_id,
                "url": data["url"],
                "ai_analysis": analysis
            })

    # Save the professional report
    os.makedirs("./data/insights", exist_ok=True)
    with open("./data/insights/ai_trend_report.json", "w") as f:
        json.dump(insights, f, indent=4)
    
    print("\n🏁 SUCCESS: Insights saved to ./data/insights/ai_trend_report.json")

if __name__ == "__main__":
    run_analyzer()