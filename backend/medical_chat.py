from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline
import torch

class MedicalChatAnalyzer:
    def __init__(self):
        # Use a smaller, medical-focused model that can run locally
        self.model_name = "samwalton/biobert-base-cased-v1.2"
        
        try:
            # Initialize the model and tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForQuestionAnswering.from_pretrained(self.model_name)
            
            # Move to GPU if available
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
            
            # Create QA pipeline
            self.qa_pipeline = pipeline(
                "question-answering",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1
            )
            
            print(f"Model loaded successfully on {self.device}")
            
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            raise e

    def chat_with_report(self, text, question):
        try:
            # Prepare context by finding relevant section
            context = self._get_relevant_context(text, question)
            
            # Get answer using QA pipeline
            result = self.qa_pipeline(
                question=question,
                context=context,
            )

            return {
                "answer": result["answer"],
                "confidence": result["score"],
                "relevant_text": context
            }
        except Exception as e:
            print(f"Error in chat_with_report: {str(e)}")
            return {
                "error": "Could not process the question",
                "details": str(e)
            }

    def _get_relevant_context(self, text, question, max_length=512):
        # Simple context window extraction
        # In a production system, you'd want to use better text chunking and retrieval
        words = text.split()
        if len(words) > max_length:
            # Take first 512 words as context
            # You could implement more sophisticated context selection here
            context = ' '.join(words[:max_length])
        else:
            context = text
        return context

    def generate_medical_context(self, text):
        medical_terms = self._extract_medical_terms(text)
        return {
            "context": "Based on the medical report, here are key terms: " + 
                      ", ".join(medical_terms)
        }

    def _extract_medical_terms(self, text):
        # Basic medical term extraction
        # You could enhance this with a medical NER model
        common_medical_terms = [
            "diagnosis", "treatment", "symptoms", "medication",
            "lab results", "vitals", "patient history"
        ]
        return [term for term in common_medical_terms if term.lower() in text.lower()]