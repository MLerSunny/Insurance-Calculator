import requests
import base64
import json
import os

def generate_png_from_mermaid(input_file, output_file):
    # Read the Mermaid content
    with open(input_file, 'r') as f:
        mermaid_content = f.read()
    
    # Encode the Mermaid content to Base64
    encoded_content = base64.b64encode(mermaid_content.encode('utf-8')).decode('utf-8')
    
    # Prepare the URL for Mermaid.ink service
    url = f"https://mermaid.ink/img/{encoded_content}"
    
    print(f"Generating PNG from Mermaid diagram...")
    print(f"Using URL: {url}")
    
    # Download the PNG
    response = requests.get(url)
    
    if response.status_code == 200:
        with open(output_file, 'wb') as f:
            f.write(response.content)
        print(f"Successfully generated PNG: {output_file}")
        return True
    else:
        print(f"Failed to generate PNG. Status code: {response.status_code}")
        return False

if __name__ == "__main__":
    input_file = "final-architecture.mmd"
    output_file = "architecture-hd.png"
    
    if os.path.exists(input_file):
        generate_png_from_mermaid(input_file, output_file)
    else:
        print(f"Input file {input_file} not found!") 