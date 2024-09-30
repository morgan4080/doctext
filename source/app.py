from flask import Flask, render_template, request, redirect, url_for, flash
from config.config import Config
from file_handlers import save_file
from extractors import extract_text_from_docx, extract_content_from_pptx

app = Flask(__name__, template_folder='../templates')
app.config.from_object(Config)

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        flash('No files selected')
        return redirect(request.url)
    
    files = request.files.getlist('files[]')
    extracted_data = []
    
    for file in files:
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        file_path = save_file(file)
        if file_path:
            if file.filename.endswith('.docx'):
                data = (file.filename, extract_text_from_docx(file_path))
            elif file.filename.endswith('.pptx'):
                data = (file.filename, extract_content_from_pptx(file_path))
            else:
                flash(f"Unsupported file type: {file.filename}")
                continue
            
            extracted_data.append(data)
    
    return render_template('results.html', extracted_data=extracted_data)

if __name__ == "__main__":
    app.run(debug=True)
