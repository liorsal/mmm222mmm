from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from medical_analyzer import MedicalReportAnalyzer
from medical_chat import MedicalChatAnalyzer
import pdfplumber
import io
import asyncio

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzers
report_analyzer = MedicalReportAnalyzer()
chat_analyzer = MedicalChatAnalyzer()

@app.post("/api/analyze-report")
async def analyze_report(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        
        text = ""
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

        # Analyze the medical report (now async)
        analysis_results = await report_analyzer.analyze(text)
        
        return {
            "success": True,
            "analysis": analysis_results
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/chat-with-report")
async def chat_with_report(request: dict):
    try:
        text = request.get("text", "")
        question = request.get("question", "")
        
        # First validate if this is a medical report
        validation = report_analyzer._validate_medical_content(text)
        if not validation['is_medical']:
            return {
                "error": "This document doesn't appear to be a medical report",
                "confidence": validation['confidence']
            }

        # Get chat response
        chat_response = chat_analyzer.chat_with_report(text, question)
        
        return {
            "success": True,
            "response": chat_response
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 