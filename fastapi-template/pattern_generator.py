import google.generativeai as genai
import json
import random
from pathlib import Path

class CrochetPatternGenerator:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.training_data = self.load_training_data()
    
    def load_training_data(self):
        """Load training examples for context"""
        training_file = Path("training_data/training_data.jsonl")
        examples = []
        
        if training_file.exists():
            print(f"Loading training data from {training_file}...")
            with open(training_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        examples.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            print(f"Loaded {len(examples)} training examples")
        else:
            print(f"Training data file not found at {training_file}")
        
        return examples
    
    def generate_pattern(self, description, skill_level="INTERMEDIATE"):
        """Generate a crochet pattern based on description"""
        if not self.training_data:
            return "No training data available"
        
        # Get relevant examples based on description keywords
        relevant_examples = self.find_relevant_examples(description, skill_level)
        
        # Build context from best examples
        context = "Based on these similar crochet patterns:\n\n"
        for i, example in enumerate(relevant_examples[:2], 1):
            # Extract clean pattern info from training data
            output = example['output']
            if '```json' in output:
                try:
                    json_str = output.replace('```json', '').replace('```', '').strip()
                    pattern_data = json.loads(json_str)
                    title = pattern_data.get('title', 'Pattern')
                    materials = pattern_data.get('materials', [])
                    instructions = pattern_data.get('instructions', {})
                    context += f"Example {i} - {title}:\nMaterials: {str(materials)[:200]}...\nInstructions: {str(instructions)[:300]}...\n\n"
                except:
                    context += f"Example {i}: {output[:400]}...\n\n"
            else:
                context += f"Example {i}: {output[:400]}...\n\n"
        
        prompt = f"""You are an expert crochet pattern designer. Create a complete, professional crochet pattern for: {description}

Skill Level: {skill_level}

{context}

Create a detailed pattern with these sections:

═══════════════════════════════════════════════════════════════
                    [CREATIVE PATTERN NAME]
═══════════════════════════════════════════════════════════════

🧶 SKILL LEVEL: {skill_level}

📏 FINISHED SIZE: [dimensions]

🧵 MATERIALS:
   • Yarn: [specific weight, brand, amount]
   • Hook: [size in mm and US]
   • Notions: [scissors, tapestry needle, etc.]

📐 GAUGE: [stitches and rows per 4 inches]

📝 ABBREVIATIONS:
   • ch = chain
   • sc = single crochet
   • dc = double crochet
   • [other abbreviations used]

📋 INSTRUCTIONS:

   Foundation:
   [starting instructions]

   Main Pattern:
   Round/Row 1: [detailed instructions with stitch counts]
   Round/Row 2: [detailed instructions with stitch counts]
   [continue pattern]

   Finishing:
   [assembly and finishing instructions]

═══════════════════════════════════════════════════════════════
                        Happy Crocheting! 🧶
═══════════════════════════════════════════════════════════════

Make it professional, detailed, and beautifully formatted."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating pattern: {e}"
    
    def find_relevant_examples(self, description, skill_level="INTERMEDIATE"):
        """Find training examples most relevant to the description"""
        description_lower = description.lower()
        scored_examples = []
        
        for example in self.training_data:
            score = 0
            example_text = example.get('output', '').lower()
            
            # Score based on keyword matches
            keywords = ['scarf', 'hat', 'blanket', 'sweater', 'amigurumi', 'toy', 'bag', 'dishcloth', 'coaster']
            for keyword in keywords:
                if keyword in description_lower and keyword in example_text:
                    score += 10
            
            # Score based on skill level
            if skill_level.lower() in example_text:
                score += 5
            
            scored_examples.append((score, example))
        
        # Sort by score and return top examples
        scored_examples.sort(key=lambda x: x[0], reverse=True)
        return [ex[1] for ex in scored_examples[:5]] if scored_examples else random.sample(self.training_data, min(3, len(self.training_data)))