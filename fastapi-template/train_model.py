import google.generativeai as genai
import json
import os
from pathlib import Path
import numpy as np
from PIL import Image
import time
from datetime import datetime

class DataPreparationContainer:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.vision_model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_image_description(self, image_array):
        """Generate detailed image description using Gemini Vision"""
        try:
            # Convert numpy array to PIL Image
            if isinstance(image_array, np.ndarray):
                pil_image = Image.fromarray(image_array)
            else:
                pil_image = image_array
            
            prompt = """Describe this crochet pattern image in detail. Focus on:
            1. The type of crochet item (hat, scarf, blanket, etc.)
            2. Colors and yarn textures visible
            3. Stitch patterns and techniques shown
            4. Size and proportions
            5. Any decorative elements or details
            
            Be specific and technical for crochet pattern generation."""
            
            response = self.vision_model.generate_content([prompt, pil_image])
            return response.text
        except Exception as e:
            print(f"Error generating image description: {e}")
            return "Unable to generate description"
    
    def structure_pattern_text(self, raw_text):
        """Convert raw text into structured crochet pattern format"""
        try:
            prompt = f"""Convert this raw crochet pattern text into a structured JSON format:

Raw text: {raw_text[:2000]}...

Return a JSON with these fields:
- title: Pattern name
- skill_level: BEGINNER/EASY/INTERMEDIATE/ADVANCED
- materials: List of yarns and tools needed
- gauge: Stitch and row gauge information
- measurements: Final dimensions
- instructions: Step-by-step instructions broken into sections
- abbreviations: List of crochet abbreviations used

Make it clean and well-structured for training data."""

            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error structuring text: {e}")
            return raw_text
    
    def prepare_training_data(self, processed_pdfs_dir, output_dir):
        """Prepare training data from processed PDFs"""
        processed_dir = Path(processed_pdfs_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / "training_data.jsonl"
        
        # Load existing processed files
        processed_files = set()
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line)
                    processed_files.add(data['source_file'])
        
        count = 0
        start_time = time.time()
        total_files = len(list(processed_dir.glob("*_processed.txt")))
        
        for txt_file in processed_dir.glob("*_processed.txt"):
            if txt_file.name in processed_files:
                continue
                
            current_total = count + len(processed_files) + 1
            elapsed = time.time() - start_time
            if count > 0:
                avg_time = elapsed / count
                remaining = (total_files - current_total) * avg_time
                eta = datetime.now().timestamp() + remaining
                eta_str = datetime.fromtimestamp(eta).strftime('%H:%M:%S')
            else:
                eta_str = "calculating..."
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing {txt_file.name}... ({current_total}/{total_files}) ETA: {eta_str}")
            
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "Text Content:" in content:
                    text_start = content.find("Text Content:") + len("Text Content:")
                    text_end = content.find("Image Descriptions:")
                    raw_text = content[text_start:text_end].strip()
                else:
                    raw_text = content
                
                if len(raw_text.strip()) < 50:
                    print(f"  Skipped - insufficient content")
                    continue
                
                structured_text = self.structure_pattern_text(raw_text)
                
                training_example = {
                    "input": f"Generate a crochet pattern for: {txt_file.stem.replace('_processed', '')}",
                    "output": structured_text,
                    "source_file": txt_file.name
                }
                
                # Append to file immediately
                with open(output_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(training_example) + '\n')
                
                count += 1
                print(f"  ✅ Completed ({count} new examples generated)")
                
                # Progress checkpoint every 10 files
                if count % 10 == 0:
                    print(f"\n📊 CHECKPOINT: {count} new examples processed, {current_total}/{total_files} total\n")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        total_time = time.time() - start_time
        print(f"\n🎉 COMPLETED: Generated {count} new training examples")
        print(f"📈 Total examples: {count + len(processed_files)}")
        print(f"⏱️  Total time: {total_time/60:.1f} minutes")
        if count > 0:
            print(f"⚡ Average time per file: {total_time/count:.1f} seconds")
        return count

if __name__ == "__main__":
    api_key = os.getenv('GEMINI_API_KEY', 'your_api_key_here')
    
    data_prep = DataPreparationContainer(api_key)
    training_data = data_prep.prepare_training_data("processed_pdfs", "training_data")