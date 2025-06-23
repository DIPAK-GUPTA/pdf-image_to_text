from flask import Flask, request, jsonify
import os
import subprocess
import tempfile
import uuid
from PIL import Image 
import glob
import base64
import re
from openai import OpenAI
import time
import json
import shutil
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
char_limit = 2000

def process_local_file(file_path, prompt=""):
    # Check if the prompt is empty
    if prompt == "":
        prompt = "Describe this image concisely."
        
    # Check if the file is a PDF
    if file_path.endswith('.pdf'):
        pdf_path = tempfile.mkdtemp().rstrip(' _')  # /tmp/asfbuywvfuh
        os.makedirs(pdf_path, exist_ok=True)
        pdf_file_name = os.path.basename(pdf_path).rstrip(' _')  # asfbuywvfuh
        pdf_full_path = os.path.join(pdf_path, f"{pdf_file_name}.pdf")
        
        # Copy the file instead of using save()
        shutil.copy(file_path, pdf_full_path)
        
        pdf_file_name_original = os.path.basename(file_path).split(".")[0]
        dict_var = {'file name': pdf_file_name_original}
        time.sleep(2)
        
        command = f"marker_single {pdf_full_path} {pdf_path}"
        try:
            subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error during marker_single execution: {e.stderr}")
            return {'message': e.stderr}
        
        folder_path = os.path.join(pdf_path, pdf_file_name)
        image_files = glob.glob(os.path.join(folder_path, '*.jpg')) + \
                     glob.glob(os.path.join(folder_path, '*.png')) + \
                     glob.glob(os.path.join(folder_path, '*.jpeg'))
        
        # Create local image directory for storing processed images
        local_image_dir = os.path.join('pdf_to_text', pdf_file_name, 'images')
        os.makedirs(local_image_dir, exist_ok=True)
        
        image_size_dict = {}
        for filename in image_files:
            image_size = os.path.getsize(filename)
            filename_only = os.path.basename(filename)   
            image_size_dict[filename_only] = image_size
            
            # Copy images to local directory
            shutil.copy(filename, os.path.join(local_image_dir, filename_only))
        
        # Process images using OpenAI if API key is available
        image_dict = {}
        if 'OPENAI_API_KEY' in os.environ:
            client = OpenAI()
            for file in image_files:
                file_name = os.path.basename(file)    
                if image_size_dict[file_name] > 20000:
                    with open(file, 'rb') as img_file:
                        base64_image = base64.b64encode(img_file.read()).decode('utf-8')   
                    
                    try:
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": prompt},
                                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                                    ],
                                }
                            ],
                        )   
                        description = response.choices[0].message.content.strip()
                        image_dict[file_name] = description
                    except Exception as e:
                        print(f"Error processing image with OpenAI: {e}")
                        image_dict[file_name] = ""
                else:
                    image_dict[file_name] = ""
            
            # Save image descriptions to JSON
            json_file_path = os.path.join('pdf_to_text', pdf_file_name, 'image_dict.json')
            os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
            with open(json_file_path, 'w') as file:
                json.dump(image_dict, file, indent=4)
        
        # Find and process the markdown file
        output_dir = os.path.join(folder_path, f"{pdf_file_name}.md")
        if os.path.exists(output_dir):
            with open(output_dir, 'r') as file:
                content = file.read()
            
            # Replace the image references with local paths and add descriptions
            for image_name, replacement_string in image_dict.items():
                if isinstance(replacement_string, dict) and 'content' in replacement_string:
                    data = replacement_string['content']
                else:
                    data = replacement_string
                
                old_string = f"![{image_name}]({image_name})"
                
                # Create relative path to image
                relative_image_path = f"images/{image_name}"
                
                if data == "":
                    replacement_string = f"![{image_name}]({relative_image_path})"
                else:
                    replacement_string = f"![{image_name}]({relative_image_path})<image_description>{data}</image_description>"
                
                content = content.replace(old_string, replacement_string)
            
            # Save the modified markdown
            pdf_dest_folder = os.path.join('pdf_to_text', pdf_file_name)
            os.makedirs(pdf_dest_folder, exist_ok=True)
            
            modified_md_path = os.path.join(pdf_dest_folder, f"{pdf_file_name}.md")
            with open(modified_md_path, 'w') as file:
                file.write(content)
            
            # Copy PDF file
            shutil.copy(pdf_full_path, os.path.join(pdf_dest_folder, f"{pdf_file_name}.pdf"))
            
            # Read the markdown content for the response
            with open(modified_md_path, 'r') as md_file:
                md_content = md_file.read() 
            
            if len(md_content) > char_limit:
                truncated = md_content[:char_limit] + '...'
            else:
                truncated = md_content
            
            # Update file dictionary
            json_file_path = 'files_dict.json'
            if os.path.exists(json_file_path):
                with open(json_file_path, 'r') as f:
                    files_dict = json.load(f)
            else:
                files_dict = {}
            
            files_dict[pdf_file_name] = pdf_file_name_original
            with open(json_file_path, 'w') as f:
                json.dump(files_dict, f, indent=4)
            
            dict_var['message'] = "converted"
            dict_var['text'] = truncated
            dict_var['output_path'] = pdf_dest_folder
            print(f"Done processing. Output saved to {pdf_dest_folder}")
            return dict_var
        else:
            dict_var['message'] = "No .md file found in the output directory."
            return dict_var
    else:
        return {'error': 'Only PDF files are allowed'}

if __name__ == '__main__':
    file_path = "input_pdf_file.pdf"  # Replace with your PDF file path
    prompt = "Analyze the provided image and extract detailed information. The image may contain a map, diagram, chart, or other visual elements. Your task is to describe the content meaningfully and provide a comprehensive explanation of the key components, patterns, and any insights that can be drawn from the image. Ensure the description is clear and relevant, avoiding any unnecessary details"
    
    result = process_local_file(file_path, prompt)
    print(json.dumps(result, indent=2))
