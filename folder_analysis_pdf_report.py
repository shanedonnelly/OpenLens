import os
import json
import glob
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import re
from PIL import Image as PILImage

def create_pdf_report(input_dir, output_pdf):
    """Create a PDF report from image-analysis pairs"""
    # Find all image and analysis files
    image_files = sorted(glob.glob(os.path.join(input_dir, "image_*.jpg")))
    image_files.extend(sorted(glob.glob(os.path.join(input_dir, "image_*.png"))))
    image_files.extend(sorted(glob.glob(os.path.join(input_dir, "image_*.jpeg"))))
    analysis_files = sorted(glob.glob(os.path.join(input_dir, "analysis_*.json")))
    
    # Make sure we have matching pairs
    if len(image_files) != len(analysis_files):
        print(f"Warning: Number of images ({len(image_files)}) doesn't match analyses ({len(analysis_files)})")
    
    # Extract numbers from filenames to ensure proper pairing
    image_dict = {}
    for img_path in image_files:
        num = re.search(r'image_(\d+)', os.path.basename(img_path))
        if num:
            image_dict[int(num.group(1))] = img_path
    
    analysis_dict = {}
    for analysis_path in analysis_files:
        num = re.search(r'analysis_(\d+)', os.path.basename(analysis_path))
        if num:
            analysis_dict[int(num.group(1))] = analysis_path
    
    # Create PDF document
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY
    )
    
    # Field styles for structured data
    field_title_style = ParagraphStyle(
        'FieldTitleStyle',
        parent=styles['Heading2'],
        fontSize=12,
        leading=14,
        spaceAfter=6
    )
    
    # Calculate available width and height for images
    available_width = A4[0] - doc.leftMargin - doc.rightMargin - 36  # 36 pts buffer
    # Allow for title, spacers, and some text - max 60% of page height for image
    available_height = (A4[1] - doc.topMargin - doc.bottomMargin) * 0.6
    
    # Build the document content
    content = []
    
    # Sort the keys to process files in order
    keys = sorted(set(image_dict.keys()).intersection(analysis_dict.keys()))
    
    for key in keys:
        img_path = image_dict[key]
        analysis_path = analysis_dict[key]
        
        # Start a new page section
        if content:  # Skip PageBreak for the first item
            content.append(PageBreak())
        
        # Add a title for this pair
        content.append(Paragraph(f"Analysis Report #{key}", title_style))
        content.append(Spacer(1, 0.2*inch))
        
        # Get original image dimensions to preserve aspect ratio
        try:
            with PILImage.open(img_path) as pil_img:
                img_width, img_height = pil_img.size
                aspect_ratio = img_height / img_width
                
                # Check if image is very tall
                is_tall_image = aspect_ratio > 1.5  # Height more than 1.5x width
                
                if is_tall_image:
                    print(f"Image {key} is tall (portrait): {img_width}x{img_height}, ratio: {aspect_ratio:.2f}")
                
        except Exception as e:
            print(f"Error opening image {img_path}: {e}")
            aspect_ratio = 0.75  # Default fallback
            is_tall_image = False
        
        # Calculate image dimensions to fit page while preserving aspect ratio
        # First try width-based sizing
        width_based_width = min(available_width, 5*inch)
        width_based_height = width_based_width * aspect_ratio
        
        # Check if height exceeds limit and recalculate if needed
        if width_based_height > available_height:
            # Height constraint dominates, so calculate width based on height
            height_based_height = available_height
            height_based_width = height_based_height / aspect_ratio
            
            img_width = height_based_width
            img_height = height_based_height
            print(f"Resized tall image {key} to fit height: {img_width:.1f}x{img_height:.1f}")
        else:
            # Width constraint works fine
            img_width = width_based_width
            img_height = width_based_height
        
        # Add the image with preserved aspect ratio
        img = Image(img_path, width=img_width, height=img_height)
        img.hAlign = 'CENTER'
        content.append(img)
        content.append(Spacer(1, 0.3*inch))
        
        # Read and parse the analysis JSON
        with open(analysis_path, 'r') as f:
            analysis_data = json.load(f)
            analysis_text = analysis_data.get('analysis', 'No analysis available')
        
        # Process the analysis text - split by newlines and create paragraphs
        if "title:" in analysis_text:
            # Try to extract structured fields if they appear to be present
            lines = analysis_text.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Check if line appears to be a field
                if ':' in line and line.split(':', 1)[0].strip().lower() in ['title', 'description', 'consistency', 'consticency']:
                    # Field title
                    field_name = line.split(':', 1)[0].strip()
                    field_value = line.split(':', 1)[1].strip()
                    
                    # Add field name as small heading
                    content.append(Paragraph(f"{field_name}:", field_title_style))
                    # Add field value as normal text
                    content.append(Paragraph(field_value, normal_style))
                    content.append(Spacer(1, 0.1*inch))
                else:
                    # Regular paragraph
                    content.append(Paragraph(line, normal_style))
                    content.append(Spacer(1, 0.1*inch))
        else:
            # Just split by newlines and create paragraphs
            for paragraph in analysis_text.split('\n'):
                if paragraph.strip():
                    content.append(Paragraph(paragraph, normal_style))
                    content.append(Spacer(1, 0.1*inch))
    
    # Build and save the PDF
    doc.build(content)
    return output_pdf

if __name__ == "__main__":
    input_dir = "input_images_analysis"
    output_pdf = "image_analysis_report.pdf"
    
    pdf_path = create_pdf_report(input_dir, output_pdf)
    print(f"PDF report created: {pdf_path}")