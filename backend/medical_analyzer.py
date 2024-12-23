import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import asyncio
import re

class MedicalReportAnalyzer:
    def __init__(self):
        # Initialize LLaMA model
        print("Loading LLaMA model...")
        self.model_name = "meta-llama/Llama-2-7b-hf"  # or your preferred LLaMA version
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            low_cpu_mem_usage=True
        )
        print("LLaMA model loaded successfully")

        self.current_progress = 0
        self.blood_test_ranges = {
            "hemoglobin": {"min": 13.5, "max": 17.5, "unit": "g/dL"},
            "wbc": {"min": 4000, "max": 11000, "unit": "/µL"},
            "rbc": {"min": 4.5, "max": 5.9, "unit": "million/µL"},
            "platelets": {"min": 150000, "max": 450000, "unit": "/µL"},
        }

    async def _generate_llama_response(self, prompt):
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.7,
            do_sample=True
        )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    async def analyze(self, text):
        try:
            self.current_progress = 0
            
            # Validate medical content
            validation_prompt = f"""
            Analyze if this is a medical report. Text: {text[:500]}...
            Answer only 'YES' or 'NO'.
            """
            is_medical = await self._generate_llama_response(validation_prompt)
            await self._update_progress(20, 1)
            
            if "NO" in is_medical.upper():
                return {
                    "error": "This document doesn't appear to be a medical report",
                    "is_medical_report": False,
                    "progress": {"status": "Not a medical report", "percent": self.current_progress}
                }

            # Extract blood test values
            blood_test_values = self._extract_blood_test_values(text)
            blood_test_analysis = self._analyze_blood_tests(blood_test_values)
            await self._update_progress(40, 1)

            # Generate classification and analysis
            analysis_prompt = f"""
            Analyze this medical report and provide:
            1. Classification (NORMAL or ABNORMAL)
            2. Confidence score (0-1)
            3. Summary
            4. Key medical terms

            Report text: {text[:1000]}...
            
            Format your response as:
            Classification: [NORMAL/ABNORMAL]
            Confidence: [SCORE]
            Summary: [SUMMARY]
            Terms: [TERM1], [TERM2], [TERM3]
            """
            
            analysis_response = await self._generate_llama_response(analysis_prompt)
            await self._update_progress(70, 1)

            # Parse LLaMA's response
            classification = "ABNORMAL" if "ABNORMAL" in analysis_response else "NORMAL"
            confidence = 0.8  # Default confidence
            summary = ""
            terms = []

            for line in analysis_response.split('\n'):
                if line.startswith('Summary:'):
                    summary = line.replace('Summary:', '').strip()
                elif line.startswith('Terms:'):
                    terms = [term.strip() for term in line.replace('Terms:', '').split(',')]

            # Generate recommendations
            recommendations_prompt = f"""
            Based on this medical report analysis:
            - Classification: {classification}
            - Blood test results: {blood_test_analysis}
            - Key terms: {', '.join(terms)}

            Provide medical recommendations. Format each recommendation on a new line starting with '-'.
            """
            
            recommendations_text = await self._generate_llama_response(recommendations_prompt)
            recommendations = [
                rec.strip() for rec in recommendations_text.split('\n') 
                if rec.strip().startswith('-')
            ]
            
            await self._update_progress(90, 1)

            result = {
                "is_medical_report": True,
                "text": text,
                "classification": {
                    "label": classification,
                    "confidence": confidence
                },
                "entities": [{"text": term, "label": "MEDICAL", "confidence": 0.8} for term in terms],
                "summary": summary,
                "blood_test_results": blood_test_analysis,
                "recommendations": recommendations,
                "progress": {"status": "Complete", "percent": 100}
            }

            await self._update_progress(100, 1)
            return result

        except Exception as e:
            print(f"Analysis error: {str(e)}")
            return {
                "error": "Error analyzing the document",
                "details": str(e),
                "is_medical_report": False,
                "progress": {"status": "Error", "percent": self.current_progress}
            }

    def _extract_blood_test_values(self, text):
        """Extract blood test values from text using regex patterns"""
        blood_test_values = {}
        
        # Define patterns for common blood test formats
        patterns = {
            "hemoglobin": r"hemoglobin[:\s]+(\d+\.?\d*)",
            "wbc": r"wbc[:\s]+(\d+,?\d*)",
            "rbc": r"rbc[:\s]+(\d+\.?\d*)",
            "platelets": r"platelets[:\s]+(\d+,?\d*)",
            # Add more patterns as needed
        }
        
        # Extract values using patterns
        for test, pattern in patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                value = match.group(1).replace(',', '')
                blood_test_values[test] = float(value)
        
        return blood_test_values

    def _analyze_blood_tests(self, values):
        """Analyze blood test values against reference ranges"""
        analysis = []
        
        for test, value in values.items():
            if test in self.blood_test_ranges:
                ref_range = self.blood_test_ranges[test]
                status = "normal"
                if value < ref_range["min"]:
                    status = "low"
                elif value > ref_range["max"]:
                    status = "high"
                
                analysis.append({
                    "test": test,
                    "value": value,
                    "unit": ref_range["unit"],
                    "reference_range": f"{ref_range['min']} - {ref_range['max']}",
                    "status": status
                })
        
        return analysis

    async def _update_progress(self, target_percent, duration):
        """Smoothly update progress in 0.1% increments"""
        try:
            start_percent = self.current_progress
            steps = int((target_percent - start_percent) * 10)  # 0.1% increments
            
            if steps > 0:
                step_duration = duration / steps
                for i in range(steps):
                    self.current_progress = round(start_percent + (i + 1) * 0.1, 1)
                    await asyncio.sleep(0.1)  # Shorter sleep time to prevent timeout
                    
            return {
                "status": "Processing",
                "percent": self.current_progress
            }
        except Exception as e:
            print(f"Error updating progress: {str(e)}")
            return {
                "status": "Error",
                "percent": self.current_progress
            }