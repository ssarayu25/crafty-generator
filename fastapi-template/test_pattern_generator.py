#!/usr/bin/env python3

from pattern_generator import CrochetPatternGenerator

def test_pattern_generator():
    print("🧶 Testing Crochet Pattern Generator...")
    
    # Initialize generator
    api_key = os.getenv('GEMINI_API_KEY', 'your_api_key_here')
    generator = CrochetPatternGenerator(api_key)
    
    print(f"✅ Loaded {len(generator.training_data)} training examples")
    
    # Test pattern generation
    test_descriptions = [
        "a simple winter scarf",
        "a baby blanket with granny squares",
        "a cute amigurumi cat"
    ]
    
    for desc in test_descriptions:
        print(f"\n🔄 Generating pattern for: {desc}")
        pattern = generator.generate_pattern(desc, "INTERMEDIATE")
        print(f"📝 Generated pattern ({len(pattern)} chars):")
        print("-" * 50)
        print(pattern[:500] + "..." if len(pattern) > 500 else pattern)
        print("-" * 50)

if __name__ == "__main__":
    test_pattern_generator()