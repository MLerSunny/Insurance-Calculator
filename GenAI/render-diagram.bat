@echo off
echo Generating architecture diagram...

REM Create a temporary HTML file
echo ^<!DOCTYPE html^> > temp_diagram.html
echo ^<html^> >> temp_diagram.html
echo ^<head^> >> temp_diagram.html
echo     ^<title^>Insurance Application Architecture^</title^> >> temp_diagram.html
echo     ^<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"^>^</script^> >> temp_diagram.html
echo     ^<style^> >> temp_diagram.html
echo         body { >> temp_diagram.html
echo             font-family: Arial, sans-serif; >> temp_diagram.html
echo             margin: 0; >> temp_diagram.html
echo             padding: 20px; >> temp_diagram.html
echo             background-color: white; >> temp_diagram.html
echo         } >> temp_diagram.html
echo         #diagram { >> temp_diagram.html
echo             width: 100%%; >> temp_diagram.html
echo             max-width: 1920px; >> temp_diagram.html
echo             margin: 0 auto; >> temp_diagram.html
echo         } >> temp_diagram.html
echo     ^</style^> >> temp_diagram.html
echo ^</head^> >> temp_diagram.html
echo ^<body^> >> temp_diagram.html
echo     ^<div id="diagram"^> >> temp_diagram.html
echo         ^<pre class="mermaid"^> >> temp_diagram.html

REM Append the Mermaid diagram content
type final-architecture.mmd >> temp_diagram.html

echo         ^</pre^> >> temp_diagram.html
echo     ^</div^> >> temp_diagram.html
echo     ^<script^> >> temp_diagram.html
echo         mermaid.initialize({ >> temp_diagram.html
echo             startOnLoad: true, >> temp_diagram.html
echo             theme: 'default', >> temp_diagram.html
echo             securityLevel: 'loose', >> temp_diagram.html
echo             themeVariables: { >> temp_diagram.html
echo                 fontSize: '16px' >> temp_diagram.html
echo             } >> temp_diagram.html
echo         }); >> temp_diagram.html
echo     ^</script^> >> temp_diagram.html
echo ^</body^> >> temp_diagram.html
echo ^</html^> >> temp_diagram.html

echo HTML file created. Please open temp_diagram.html in a browser and use browser's screenshot feature to save as PNG.
echo Once loaded in browser, press Ctrl+P to print/save as PDF or use browser tools to save as PNG.

REM Open the HTML file in default browser
start temp_diagram.html

echo Browser should open with the diagram. Please manually save as PNG. 