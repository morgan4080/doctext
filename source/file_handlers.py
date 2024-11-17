import os
from flask import current_app

# Check if the uploaded file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# Save uploaded files to the designated upload folder
def save_file(file):
    if file and allowed_file(file.filename):
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        return file_path
    return None

# Delete all files in the uploads folder
def delete_all_files_in_uploads():
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    if not os.path.exists(upload_folder):
        return "Upload folder does not exist."

    try:
        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return "All files in the uploads folder have been deleted."
    except Exception as e:
        return f"An error occurred while deleting files: {e}"
