import os
import datetime
from flask import Flask, render_template, request, redirect, flash, send_from_directory, url_for
from config.config import Config
from source.file_handlers import save_file
from source.extractors import extract_text_from_docx, extract_content_from_pptx

app = Flask(__name__, template_folder='../templates')
app.config.from_object(Config)


@app.route('/robots.txt')
def robots():
    return send_from_directory('../static', 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('../static', 'sitemap.xml')

@app.route('/docext/')
def upload_form():
    return render_template('upload.html')

@app.route('/docext/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        flash('No files selected')
        return redirect(request.url)
    
    files = request.files.getlist('files[]')
    
    for file in files:
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        save_file(file)
    
    return redirect(url_for('list_uploaded_files'))

# Route to display all uploaded files
@app.route('/docext/uploads')
def list_uploaded_files():
    try:
        extracted_data = []
        # List all files in the upload directory
        files = os.listdir(app.config['UPLOAD_FOLDER'])

        if not files:
            return redirect(url_for('upload_form'))

        for file in files:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
            if os.path.isfile(file_path):
                # Determine the file type and extract data
                if file.endswith('.docx'):
                    data = extract_text_from_docx(file_path)
                elif file.endswith('.pptx'):
                    data = extract_content_from_pptx(file_path)
                else:
                    data = "Unsupported file type"

                # Create a dictionary with file name, upload date, and extracted data
                upload_info = {
                    'file_name': file,
                    'upload_date': datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S'),
                    'data': data
                }

                extracted_data.append(upload_info)

        # Pass the list of dictionaries (file_name, upload_date, data) to the template
        return render_template('uploads.html', files=extracted_data)
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    app.run(debug=True)
