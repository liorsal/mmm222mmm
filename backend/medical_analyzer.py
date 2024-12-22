import torch
import concurrent.futures
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForTokenClassification, pipeline

class MedicalReportAnalyzer:
    def __init__(self):
        # Check for MPS (Metal Performance Shaders) availability
        self.device = (
            "mps" if torch.backends.mps.is_available() 
            else "cuda" if torch.cuda.is_available() 
            else "cpu"
        )
        print(f"Using device: {self.device}")

        # Load models with lower precision (faster and uses less memory)
        self.model_config = {
            "torch_dtype": torch.float16,  # Use half precision
            "load_in_8bit": True,         # 8-bit quantization
            "device_map": self.device
        }

        # Initialize models with optimizations
        self.clinical_bert = self._setup_clinical_bert()
        self.ner_model = self._setup_ner_model()
        
        # Only initialize summarizer if needed (it's the heaviest model)
        self._lazy_summarizer = None

    def _setup_clinical_bert(self):
        model_name = "medicalai/ClinicalBERT"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(
            model_name, 
            **self.model_config
        )
        return pipeline("text-classification", model=model, tokenizer=tokenizer)

    def _setup_ner_model(self):
        model_name = "allenai/scibert_scivocab_uncased"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForTokenClassification.from_pretrained(
            model_name,
            **self.model_config
        )
        return pipeline("ner", model=model, tokenizer=tokenizer)

    @property
    def summarizer(self):
        # Lazy loading of summarizer only when needed
        if self._lazy_summarizer is None:
            model_name = "facebook/bart-large-cnn"
            self._lazy_summarizer = pipeline(
                "summarization", 
                model=model_name,
                **self.model_config
            )
        return self._lazy_summarizer

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
        # First validate if this looks like a medical report (fast check)
        validation = self._validate_medical_content(text)
        if not validation['is_medical']:
            return {
                "error": "This document doesn't appear to be a medical report",
                "confidence": validation['confidence'],
                "is_medical_report": False
            }

        try:
            # Limit text length for faster processing
            max_length = 512
            truncated_text = ' '.join(text.split()[:max_length])

            # Run classification and NER in parallel
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_classification = executor.submit(
                    self.clinical_bert, truncated_text
                )
                future_entities = executor.submit(
                    self.ner_model, truncated_text
                )

                classification = future_classification.result()[0]
                entities = future_entities.result()

            # Only generate summary if needed (it's the slowest part)
            summary = self.summarizer(
                truncated_text,
                max_length=150,
                min_length=50,
                do_sample=False
            )[0]['summary_text'] if len(text) > 200 else text

            return {
                "is_medical_report": True,
                "classification": {
                    "label": classification["label"],
                    "confidence": classification["score"]
                },
                "entities": self._process_entities(entities),
                "summary": summary,
                "recommendations": self._generate_recommendations(
                    classification, 
                    entities
                )
            }
        except Exception as e:
            print(f"Error during analysis: {str(e)}")
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