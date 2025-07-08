from transformers import T5ForConditionalGeneration, T5TokenizerFast
import torch
import os
import sys
import logging
from datetime import datetime
from pathlib import Path
import json

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "final_crochet_model")
FALLBACK_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "enhanced_crochet_model")
FALLBACK_MODEL_PATH_2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "simple_retrained_model")
FALLBACK_MODEL_PATH_3 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crochet_pattern_model")

# Setup logging
logging.basicConfig(
    filename='model_test.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_model_and_tokenizer(model_path=None):
    if model_path is None:
        model_path = MODEL_PATH
    try:
        logging.info("Starting model loading process")
        logging.info(f"Model path exists: {os.path.exists(model_path)}")
        
        if not os.path.exists(model_path):
            logger.warning(f"Primary model not found at {model_path}, trying fallback...")
            if os.path.exists(FALLBACK_MODEL_PATH):
                model_path = FALLBACK_MODEL_PATH
                logger.info(f"Using fallback model at {model_path}")
            elif os.path.exists(FALLBACK_MODEL_PATH_2):
                model_path = FALLBACK_MODEL_PATH_2
                logger.info(f"Using second fallback model at {model_path}")
            elif os.path.exists(FALLBACK_MODEL_PATH_3):
                model_path = FALLBACK_MODEL_PATH_3
                logger.info(f"Using third fallback model at {model_path}")
            else:
                raise FileNotFoundError(f"No model found at any of the specified paths")
        
        # Try different tokenizer loading approaches
        tokenizer = None
        model = None
        
        # Approach 1: Try loading from model path
        try:
            tokenizer = T5TokenizerFast.from_pretrained(model_path)
            logging.info("Loaded tokenizer from model path")
        except Exception as e1:
            logging.warning(f"Failed to load tokenizer from model path: {e1}")
            
            # Approach 2: Try base T5 tokenizer
            try:
                tokenizer = T5TokenizerFast.from_pretrained('t5-small')
                logging.info("Loaded base T5 tokenizer")
            except Exception as e2:
                logging.warning(f"Failed to load base tokenizer: {e2}")
                
                # Approach 3: Try regular T5Tokenizer
                from transformers import T5Tokenizer
                tokenizer = T5Tokenizer.from_pretrained('t5-small')
                logging.info("Loaded regular T5 tokenizer")
        
        # Load the model
        model = T5ForConditionalGeneration.from_pretrained(model_path)
        logging.info("Successfully loaded model and tokenizer")
        return model, tokenizer
        
    except Exception as e:
        logging.error(f"Error loading model and tokenizer: {str(e)}")
        raise

def generate_pattern_section(model, tokenizer, pattern_info, section_type, max_length=384):
    try:
        # Create section-specific prompts
        if section_type == "materials":
            prompt = (
                f"Generate ONLY the materials section for this crochet pattern:\n{pattern_info}\n"
                "Include:\n"
                "- Specific yarn brand and weight\n"
                "- Hook size in mm and US size\n"
                "- Notions needed (stitch markers, tapestry needle)\n"
                "- Yarn amounts"
            )
        elif section_type == "gauge":
            prompt = (
                f"Generate ONLY the gauge information for this crochet pattern:\n{pattern_info}\n"
                "Include:\n"
                "- Stitches per 4 inches in pattern stitch\n"
                "- Rows per 4 inches\n"
                "- Gauge swatch size"
            )
        else:  # instructions
            prompt = (
                f"Generate ONLY the step-by-step instructions for this crochet pattern:\n{pattern_info}\n"
                "Include:\n"
                "- Foundation chain or starting round\n"
                "- Row by row or round by round instructions\n"
                "- Stitch counts for each row/round\n"
                "- Finishing steps"
            )
        
        logging.info(f"Generating {section_type} with prompt:\n{prompt}")
        
        inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=128)
        
        outputs = model.generate(
            **inputs,
            max_length=max_length,
            num_beams=3,
            temperature=0.8,
            top_k=40,
            top_p=0.9,
            no_repeat_ngram_size=2,
            length_penalty=1.0,
            early_stopping=True,
            do_sample=True,
            repetition_penalty=1.3
        )
        
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        logging.info(f"Generated {section_type} text:\n{generated_text}")
        return generated_text
        
    except Exception as e:
        logging.error(f"Error generating {section_type}: {str(e)}")
        raise

def generate_pattern(model, tokenizer, input_text, max_length=384):
    try:
        # Generate each section separately
        materials = generate_pattern_section(model, tokenizer, input_text, "materials", max_length)
        gauge = generate_pattern_section(model, tokenizer, input_text, "gauge", max_length)
        instructions = generate_pattern_section(model, tokenizer, input_text, "instructions", max_length)
        
        # Format the complete pattern
        formatted_output = (
            f"{input_text}\n\n"
            "MATERIALS\n"
            "--------\n"
            f"{materials}\n\n"
            "GAUGE\n"
            "-----\n"
            f"{gauge}\n\n"
            "ABBREVIATIONS\n"
            "-------------\n"
            "ch = chain\n"
            "sc = single crochet\n"
            "dc = double crochet\n"
            "hdc = half double crochet\n"
            "st(s) = stitch(es)\n"
            "sl st = slip stitch\n"
            "rep = repeat\n"
            "sp = space\n"
            "rnd = round\n"
            "sk = skip\n\n"
            "INSTRUCTIONS\n"
            "-----------\n"
            f"{instructions}\n"
        )
        
        return formatted_output
        
    except Exception as e:
        logging.error(f"Error generating pattern: {str(e)}")
        raise

def main():
    try:
        logging.info("Starting main function")
        model, tokenizer = load_model_and_tokenizer()
        
        test_patterns = [
            "Basic Infinity Scarf\n"
            "Skill Level: Beginner\n"
            "Finished Size: 60\" circumference x 8\" width\n"
            "Style: Worked in continuous rounds using single crochet\n"
            "Description: A cozy winter accessory worked in the round",
            
            "Simple Shell Border Baby Blanket\n"
            "Skill Level: Easy\n"
            "Finished Size: 30\" x 40\"\n"
            "Style: Solid single crochet body with shell stitch border\n"
            "Description: A warm blanket with decorative shell edging",
            
            "Classic Granny Square\n"
            "Skill Level: Beginner\n"
            "Finished Size: 8\" x 8\"\n"
            "Style: Traditional granny square using double crochet clusters\n"
            "Description: Basic granny square with corner chains"
        ]
        
        # Write patterns to file and display
        with open('generated_patterns.txt', 'w') as f:
            for pattern in test_patterns:
                logging.info(f"\nGenerating pattern for: {pattern}")
                result = generate_pattern(model, tokenizer, pattern)
                
                # Format output nicely
                output = (
                    f"\n{'='*70}\n"
                    f"{result}\n"
                    f"{'='*70}\n"
                )
                
                f.write(output)
                print(output)
                logging.info(f"Generated result:\n{result}\n")
                
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    logging.info("Script started")
    main()