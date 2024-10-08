from pptx import Presentation
from docx import Document
import os

# Extract headlines and paragraphs from DOCX file
def extract_text_from_docx(file_path):
    doc = Document(file_path)
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    headlines = [para.text for para in doc.paragraphs if para.style.name.startswith('Heading')]
    return {'headlines': headlines, 'paragraphs': paragraphs}

# Extract headlines, paragraphs, and images from PPTX file
# Extract headlines, paragraphs, and images from PPTX file
def extract_content_from_pptx(file_path):
    prs = Presentation(file_path)
    headlines, paragraphs, images = [], [], []
    
    for slide_idx, slide in enumerate(prs.slides):
        for shape in slide.shapes:
            # Extract text
            if hasattr(shape, "text"):
                if shape.text_frame:
                    paragraphs.append(shape.text)
            
            # Extract images
            if hasattr(shape, "image"):
                image = shape.image
                image_bytes = image.blob  # Get the image binary data
                image_extension = os.path.splitext(image.content_type)[1]  # Get the image extension

                # Create image path to save
                image_path = os.path.join(os.getcwd(), 'static', 'uploads', f'image_slide{slide_idx}.{image_extension}')
                
                # Write image data to file
                with open(image_path, 'wb') as img_file:
                    img_file.write(image_bytes)
                    images.append(image_path)

    return {'headlines': paragraphs, 'paragraphs': paragraphs, 'images': images}

# More extractors can be added here (e.g., for DOC format using third-party libraries)
