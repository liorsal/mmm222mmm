import torch
import concurrent.futures
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForTokenClassification, pipeline
import time
import asyncio

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

        self.current_progress = 0

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

    async def _update_progress(self, target_percent, duration):
        """Smoothly update progress in 0.1% increments"""
        start_percent = self.current_progress
        steps = int((target_percent - start_percent) * 10)  # 0.1% increments
        
        if steps > 0:
            for i in range(steps):
                self.current_progress = start_percent + (i + 1) * 0.1
                await asyncio.sleep(duration / steps)

    async def analyze(self, text):
        try:
            # Initialize progress
            self.current_progress = 0
            progress = {
                "status": "Starting analysis",
                "percent": self.current_progress
            }

            # Validate medical content (0-10%)
            await self._update_progress(5, 1)  # First 5%
            validation = self._validate_medical_content(text)
            await self._update_progress(10, 1)  # Up to 10%
            
            if not validation['is_medical']:
                return {
                    "error": "This document doesn't appear to be a medical report",
                    "confidence": validation['confidence'],
                    "is_medical_report": False,
                    "progress": {"status": "Not a medical report", "percent": self.current_progress}
                }

            # Process text (10-20%)
            max_length = 512
            truncated_text = ' '.join(text.split()[:max_length])
            await self._update_progress(20, 2)

            # Classification (20-40%)
            await self._update_progress(30, 2)
            classification = self.clinical_bert(truncated_text)[0]
            await self._update_progress(40, 2)

            # NER (40-60%)
            await self._update_progress(50, 2)
            entities = self.ner_model(truncated_text)
            await self._update_progress(60, 2)

            # Summary generation (60-90%)
            await self._update_progress(70, 2)
            summary = self.summarizer(
                truncated_text,
                max_length=150,
                min_length=50,
                do_sample=False
            )[0]['summary_text'] if len(text) > 200 else text
            
            await self._update_progress(90, 2)

            # Finalize results (90-100%)
            result = {
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
                ),
                "progress": {"status": "Complete", "percent": 100}
            }
            
            await self._update_progress(100, 1)
            return result

        except Exception as e:
            print(f"Error during analysis: {str(e)}")
            return {
                "error": "Error analyzing the document",
                "details": str(e),
                "is_medical_report": False,
                "progress": {"status": "Error", "percent": self.current_progress}
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