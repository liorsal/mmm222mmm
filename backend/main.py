from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import re
from difflib import get_close_matches
import pdfplumber
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
import io

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize model at startup
print("Loading biomedical NER model...")
model_name = "d4data/biomedical-ner-all"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)
ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
print("Model loaded successfully")

def load_reference_ranges():
    return {
        "Alanine aminotransferase (ALT)": {"range": (10, 40), "unit": "U/L"},
        "Albumin": {"range": (3.5, 5), "unit": "g/dL"},
        "Potassium": {"range": (3.5, 5.0), "unit": "mEq/L"},
        "Sodium": {"range": (136, 142), "unit": "mEq/L"},
        "Hemoglobin": {"range": (12, 18), "unit": "g/dL"},
        "Glucose": {"range": (70, 110), "unit": "mg/dL"},
        "White Blood Cell (WBC)": {"range": (4.5, 11.0), "unit": "K/µL"},
        "Red Blood Cell (RBC)": {"range": (4.5, 5.9), "unit": "M/µL"},
        "Platelet Count": {"range": (150, 450), "unit": "K/µL"},
        "Total Cholesterol": {"range": (125, 200), "unit": "mg/dL"},
        "HDL Cholesterol": {"range": (40, 60), "unit": "mg/dL"},
        "LDL Cholesterol": {"range": (0, 100), "unit": "mg/dL"},
        "Triglycerides": {"range": (0, 150), "unit": "mg/dL"},
        "Creatinine": {"range": (0.6, 1.2), "unit": "mg/dL"},
        "BUN (Blood Urea Nitrogen)": {"range": (7, 20), "unit": "mg/dL"},
        "AST (Aspartate Aminotransferase)": {"range": (10, 40), "unit": "U/L"},
        "Alkaline Phosphatase": {"range": (44, 147), "unit": "U/L"},
        "Total Bilirubin": {"range": (0.3, 1.2), "unit": "mg/dL"},
        "TSH (Thyroid Stimulating Hormone)": {"range": (0.4, 4.0), "unit": "mIU/L"},
        "T4 (Thyroxine)": {"range": (4.5, 11.2), "unit": "µg/dL"},
        "HbA1c (Hemoglobin A1c)": {"range": (4.0, 5.6), "unit": "%"},
        "Fasting Blood Sugar": {"range": (70, 100), "unit": "mg/dL"},
        "Calcium": {"range": (8.5, 10.5), "unit": "mg/dL"},
        "Magnesium": {"range": (1.7, 2.2), "unit": "mg/dL"},
        "Chloride": {"range": (96, 106), "unit": "mEq/L"},
    }

def load_test_metadata():
    return {
        "categories": {
            "blood_count": ["WBC", "RBC", "Hemoglobin", "Platelet Count"],
            "lipids": ["Total Cholesterol", "HDL", "LDL", "Triglycerides"],
            "liver": ["ALT", "AST", "Alkaline Phosphatase", "Bilirubin"],
            "kidney": ["Creatinine", "BUN"],
            "thyroid": ["TSH", "T4"],
            "diabetes": ["HbA1c", "Glucose"],
            "electrolytes": ["Sodium", "Potassium", "Chloride", "Calcium"]
        },
        "importance": {
            "critical": ["Glucose", "Potassium", "Sodium"],
            "major": ["Hemoglobin", "WBC", "Creatinine"],
            "standard": ["Cholesterol", "Albumin"]
        }
    }

def extract_text_from_pdf(file_content):
    with pdfplumber.open(io.BytesIO(file_content)) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages)

def analyze_text(text, batch_size=512):
    chunks = [text[i:i + batch_size] for i in range(0, len(text), batch_size)]
    return [entity for chunk in chunks for entity in ner_pipeline(chunk)]

def simplify_results(ner_results):
    tests = []
    test = {}

    for entity in ner_results:
        if entity["entity_group"] == "Diagnostic_procedure":
            if test:
                tests.append(test)
            test = {"Test Name": entity["word"]}
        elif entity["entity_group"] == "Lab_value":
            test["Value"] = entity["word"]
        elif entity["entity_group"] == "Unit":
            test["Unit"] = entity["word"]
    if test:
        tests.append(test)
    return tests

def find_closest_match(name, reference_ranges):
    # Convert to lowercase and remove common words/characters for better matching
    def clean_name(n):
        return n.lower().replace('(', '').replace(')', '').replace(',', '').strip()
    
    name = clean_name(name)
    matches = {}
    
    for ref_name in reference_ranges.keys():
        ref_clean = clean_name(ref_name)
        # Check for exact match
        if name == ref_clean:
            return ref_name
        # Check if name is contained in reference name
        if name in ref_clean or ref_clean in name:
            matches[ref_name] = len(ref_clean)
    
    # Return the closest match if any found
    if matches:
        return max(matches.items(), key=lambda x: x[1])[0]
    
    # Try fuzzy matching if no direct match found
    close_matches = get_close_matches(name, 
                                    [clean_name(k) for k in reference_ranges.keys()], 
                                    n=1, 
                                    cutoff=0.6)
    
    # Return the first match if found, otherwise return None
    return reference_ranges.keys()[0] if close_matches else None

def evaluate_tests(tests, reference_ranges):
    status = "Good"
    abnormal_tests = []
    normal_tests = []

    for test in tests:
        name = test.get("Test Name", "").strip()
        value = test.get("Value", "").strip()
        unit = test.get("Unit", "").strip()
        
        matched_name = find_closest_match(name, reference_ranges)
        if matched_name and matched_name in reference_ranges:
            ref_range = reference_ranges[matched_name]["range"]
            ref_unit = reference_ranges[matched_name]["unit"]

            try:
                values = list(map(float, re.findall(r"[-+]?\d*\.\d+|\d+", value)))
                if values:
                    if len(values) == 1 and not (ref_range[0] <= values[0] <= ref_range[1]):
                        status = "Bad"
                        abnormal_tests.append({
                            "test": name,
                            "value": value,
                            "unit": unit,
                            "range": f"{ref_range[0]}-{ref_range[1]} {ref_unit}"
                        })
                    elif len(values) == 2 and not (ref_range[0] <= values[0] <= ref_range[1] and ref_range[0] <= values[1] <= ref_range[1]):
                        status = "Bad"
                        abnormal_tests.append({
                            "test": name,
                            "value": f"{values[0]}-{values[1]}",
                            "unit": unit,
                            "range": f"{ref_range[0]}-{ref_range[1]} {ref_unit}"
                        })
                    else:
                        normal_tests.append({
                            "test": name,
                            "value": value,
                            "unit": unit,
                            "range": f"{ref_range[0]}-{ref_range[1]} {ref_unit}"
                        })
            except ValueError:
                print(f"Error parsing value for {name}: {value}")
        else:
            print(f"No reference range found for test: {name}")

    return {
        "status": status,
        "abnormal_tests": abnormal_tests,
        "normal_tests": normal_tests
    }

@app.post("/api/analyze-report")
async def analyze_report(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        
        # Extract text from PDF
        text = extract_text_from_pdf(contents)
        
        # Analyze with NER
        ner_results = analyze_text(text)
        
        # Simplify results
        tests = simplify_results(ner_results)
        
        # Load reference ranges
        reference_ranges = load_reference_ranges()
        
        # Evaluate test results
        evaluation = evaluate_tests(tests, reference_ranges)
        
        return {
            "success": True,
            "text": text,
            "results": tests,
            "evaluation": evaluation
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