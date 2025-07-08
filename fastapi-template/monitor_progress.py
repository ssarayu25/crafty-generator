#!/usr/bin/env python3
import time
import os
from pathlib import Path

def monitor_progress():
    training_file = Path("training_data/training_data.jsonl")
    
    if not training_file.exists():
        print("Training data file not found. Start train_model.py first.")
        return
    
    last_size = 0
    last_count = 0
    
    print("🔍 Monitoring training progress... (Press Ctrl+C to stop)")
    print("=" * 50)
    
    while True:
        try:
            # Check file size and line count
            current_size = training_file.stat().st_size
            
            with open(training_file, 'r') as f:
                current_count = sum(1 for _ in f)
            
            # Show progress if changed
            if current_count != last_count:
                size_mb = current_size / (1024 * 1024)
                progress = (current_count / 3111) * 100
                
                print(f"[{time.strftime('%H:%M:%S')}] Examples: {current_count:,}/3,111 ({progress:.1f}%) | Size: {size_mb:.1f}MB")
                
                if current_count > last_count:
                    new_examples = current_count - last_count
                    print(f"  ➕ Added {new_examples} new examples")
            
            last_size = current_size
            last_count = current_count
            
            time.sleep(10)  # Check every 10 seconds
            
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_progress()