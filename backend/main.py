from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import json

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat")
async def chat(request: dict):
    try:
        message = request.get("message", "")
        
        # Create prompt with medical context
        prompt = f"""You are a helpful medical AI assistant. You can provide general health information but always remind users to consult healthcare professionals for medical advice.

User: {message}
Assistant: """

        # Call Ollama
        process = subprocess.Popen(
            ["ollama", "run", "llama2", prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Get the response
        output, error = process.communicate()

        if error:
            print(f"Ollama error: {error}")
            return {"error": "Failed to generate response"}

        return {"response": output.strip()}

    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 