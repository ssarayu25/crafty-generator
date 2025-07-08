import pdfplumber
import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
import io
import os
from pathlib import Path

class PDFProcessor:
    def __init__(self, use_vision=False):
        self.use_vision = use_vision
        if use_vision:
            from google.cloud import vision
            self.vision_client = vision.ImageAnnotatorClient()
    
    def extract_images_and_text(self, pdf_path):
        """Extract images and text from PDF using pdfplumber and PyMuPDF"""
        results = {'text': '', 'images': [], 'image_descriptions': []}
        
        # Extract text with pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                if page.extract_text():
                    results['text'] += page.extract_text() + '\n'
        
        # Extract images with PyMuPDF
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    
                    if pix.n - pix.alpha < 4:  # GRAY or RGB
                        img_data = pix.tobytes("png")
                        img_pil = Image.open(io.BytesIO(img_data))
                        img_array = np.array(img_pil)
                        
                        # Skip small images
                        if img_array.shape[0] < 50 or img_array.shape[1] < 50:
                            pix = None
                            continue
                        
                        # Process with OpenCV
                        processed_img = self._process_image(img_array)
                        if processed_img is not None:
                            results['images'].append(processed_img)
                            
                            # Get description
                            if self.use_vision:
                                description = self._get_image_description(processed_img)
                                results['image_descriptions'].append(description)
                            else:
                                results['image_descriptions'].append(f"Image {len(results['images'])}: {processed_img.shape}")
                    
                    pix = None
                    
                except Exception as e:
                    print(f"Error extracting image {img_index} from page {page_num}: {str(e)[:100]}")
        
        doc.close()
        return results
    
    def _process_image(self, img_array):
        """Process image using OpenCV"""
        try:
            # Ensure valid image
            if img_array.size == 0 or len(img_array.shape) == 0:
                return None
            
            # Convert to grayscale if needed
            if len(img_array.shape) == 3 and img_array.shape[2] >= 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            elif len(img_array.shape) == 2:
                gray = img_array
            else:
                return img_array
            
            # Apply basic enhancement
            if gray.dtype != np.uint8:
                gray = gray.astype(np.uint8)
            
            enhanced = cv2.equalizeHist(gray)
            return enhanced
        except Exception as e:
            print(f"Image processing error: {e}")
            return img_array
    
    def _get_image_description(self, img_array):
        """Get basic image description"""
        if not self.use_vision:
            return f"Image: {img_array.shape[0]}x{img_array.shape[1]} pixels"
        
        try:
            from google.cloud import vision
            # Convert numpy array to bytes
            pil_img = Image.fromarray(img_array)
            img_byte_arr = io.BytesIO()
            pil_img.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            
            # Create Vision API image object
            image = vision.Image(content=img_bytes)
            
            # Detect text and objects
            text_response = self.vision_client.text_detection(image=image)
            label_response = self.vision_client.label_detection(image=image)
            
            description = ""
            if text_response.text_annotations:
                description += f"Text: {text_response.text_annotations[0].description}\n"
            
            if label_response.label_annotations:
                labels = [label.description for label in label_response.label_annotations[:5]]
                description += f"Objects: {', '.join(labels)}"
            
            return description
        except Exception as e:
            print(f"Error getting image description: {e}")
            return "No description available"
    
    def process_pdf_batch(self, pdf_directory, output_directory, max_files=5):
        """Process multiple PDFs in a directory"""
        pdf_dir = Path(pdf_directory)
        output_dir = Path(output_directory)
        output_dir.mkdir(exist_ok=True)
        
        pdf_files = list(pdf_dir.glob('*.pdf'))[:max_files]
        
        for pdf_file in pdf_files:
            print(f"Processing {pdf_file.name}...")
            try:
                results = self.extract_images_and_text(pdf_file)
                
                # Save results
                output_file = output_dir / f"{pdf_file.stem}_processed.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"PDF: {pdf_file.name}\n")
                    f.write(f"Text length: {len(results['text'])} chars\n")
                    f.write(f"Images found: {len(results['images'])}\n")
                    f.write(f"Text Content:\n{results['text'][:1000]}...\n\n")
                    f.write(f"Image Descriptions:\n")
                    for i, desc in enumerate(results['image_descriptions']):
                        f.write(f"Image {i+1}: {desc}\n")
                
                print(f"✅ Completed {pdf_file.name} - Text: {len(results['text'])} chars, Images: {len(results['images'])}")
                
            except Exception as e:
                print(f"❌ Error processing {pdf_file.name}: {e}")

if __name__ == "__main__":
    processor = PDFProcessor(use_vision=False)
    print("Processing all PDFs from scraped_patterns...")
    processor.process_pdf_batch("scraped_patterns", "processed_pdfs", max_files=3200)