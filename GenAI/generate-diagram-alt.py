import asyncio
from playwright.async_api import async_playwright
import os

# HTML template with Mermaid diagram
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Insurance Application Architecture</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: white;
        }}
        #diagram {{
            width: 100%;
            max-width: 1920px;
            margin: 0 auto;
        }}
    </style>
</head>
<body>
    <div id="diagram">
        <pre class="mermaid">
{mermaid_content}
        </pre>
    </div>

    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            securityLevel: 'loose',
            themeVariables: {{
                fontSize: '16px'
            }}
        }});
    </script>
</body>
</html>
"""

async def generate_png_from_mermaid(input_file, output_file, width=1920, height=1080):
    print(f"Reading Mermaid diagram from {input_file}...")
    
    # Read the Mermaid content
    with open(input_file, 'r') as f:
        mermaid_content = f.read()
    
    # Create HTML with embedded Mermaid content
    html_content = HTML_TEMPLATE.format(mermaid_content=mermaid_content)
    
    # Write HTML to temporary file
    temp_html_file = "temp_diagram.html"
    with open(temp_html_file, 'w') as f:
        f.write(html_content)
    
    print(f"Rendering diagram to PNG...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": width, "height": height})
        
        # Load the HTML file
        await page.goto(f"file://{os.path.abspath(temp_html_file)}")
        
        # Wait for Mermaid to render (adjust timeout as needed)
        await page.wait_for_selector(".mermaid svg", timeout=10000)
        
        # Extra wait to ensure rendering is complete
        await page.wait_for_timeout(2000)
        
        # Take screenshot
        await page.screenshot(path=output_file, full_page=True)
        
        await browser.close()
        
        print(f"Successfully generated PNG: {output_file}")
        
        # Clean up temporary HTML file
        os.remove(temp_html_file)
        print("Cleaned up temporary files")

if __name__ == "__main__":
    input_file = "final-architecture.mmd"
    output_file = "architecture-hd.png"
    
    if not os.path.exists(input_file):
        print(f"Input file {input_file} not found!")
        exit(1)
    
    # Run the async function
    asyncio.run(generate_png_from_mermaid(input_file, output_file)) 