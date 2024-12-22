from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification,
    pipeline
)

class MedicalReportAnalyzer:
    def __init__(self):
        # Initialize models
        self.clinical_bert = self._setup_clinical_bert()
        self.ner_model = self._setup_ner_model()
        self.summarizer = self._setup_summarizer()

    def _setup_clinical_bert(self):
        model_name = "medicalai/ClinicalBERT"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        return pipeline("text-classification", model=model, tokenizer=tokenizer)

    def _setup_ner_model(self):
        model_name = "allenai/scibert_scivocab_uncased"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForTokenClassification.from_pretrained(model_name)
        return pipeline("ner", model=model, tokenizer=tokenizer)

    def _setup_summarizer(self):
        model_name = "facebook/bart-large-cnn"
        return pipeline("summarization", model=model_name)

    def _validate_medical_content(self, text):
        # List of common medical terms/indicators
        medical_indicators = [
            'diagnosis', 'patient', 'treatment', 'medical', 'health', 'doctor',
            'hospital', 'clinic', 'symptoms', 'examination', 'lab', 'test results'
        ]
        
        # Convert text to lowercase for checking
        text_lower = text.lower()
        
        # Count how many medical indicators are present
        matches = sum(1 for term in medical_indicators if term in text_lower)
        
        # If less than 2 medical terms are found, it's probably not a medical report
        return {
            'is_medical': matches >= 2,
            'confidence': matches / len(medical_indicators)
        }

    def analyze(self, text):
        # First validate if this looks like a medical report
        validation = self._validate_medical_content(text)
        if not validation['is_medical']:
            return {
                "error": "This document doesn't appear to be a medical report",
                "confidence": validation['confidence'],
                "is_medical_report": False
            }

        # Continue with existing analysis if it is a medical report
        try:
            classification = self.clinical_bert(text[:512])[0]
            entities = self.ner_model(text[:512])
            summary = self.summarizer(text[:1024], 
                                    max_length=150, 
                                    min_length=50, 
                                    do_sample=False)[0]['summary_text']

            return {
                "is_medical_report": True,
                "classification": {
                    "label": classification["label"],
                    "confidence": classification["score"]
                },
                "entities": self._process_entities(entities),
                "summary": summary,
                "recommendations": self._generate_recommendations(classification, entities)
            }
        except Exception as e:
            return {
                "error": "Error analyzing the document",
                "details": str(e),
                "is_medical_report": False
            }

    def _process_entities(self, entities):
        # Group similar entities and remove duplicates
        processed = []
        seen = set()
        
        for entity in entities:
            if entity['word'] not in seen:
                seen.add(entity['word'])
                processed.append({
                    "text": entity['word'],
                    "label": entity['entity'],
                    "confidence": entity['score']
                })
        
        return processed

    def _generate_recommendations(self, classification, entities):
        # This is a simplified version - you would want to expand this
        # based on your specific medical knowledge base
        recommendations = []
        
        if classification["label"] == "ABNORMAL":
            recommendations.append("Consult with your healthcare provider about these findings")
        
        # Add more specific recommendations based on entities found
        medical_terms = [e['word'] for e in entities if e['score'] > 0.8]
        if medical_terms:
            recommendations.append(f"Discuss these terms with your doctor: {', '.join(medical_terms[:3])}")
        
        return recommendations 