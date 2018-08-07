#!/home/ider/anaconda3/bin/python

import os, time, zipfile, tempfile, uuid, shutil, subprocess
from flask import Flask, request, send_from_directory, send_file
from werkzeug.utils import secure_filename
from concurrent.futures import ThreadPoolExecutor


app = Flask(__name__)

TIMEOUT = os.environ.get('TIMEOUT',180)

bin = "/usr/local/bin/pdf2htmlEX"
ALLOWED_EXTENSIONS = set(['pdf',])


app.config['UPLOAD_FOLDER'] = '/tmp'
app.config['COUNT'] = 0
app.config['executor_file'] = ThreadPoolExecutor(max_workers=5)

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.urandom(24)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/pdf2pdf', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "no file", 404
        file = request.files['file']
        if file.filename == '':
            return "no filename", 404
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            pdf_folder_uuid =  str(uuid.uuid4())
            pdf_floder_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_folder_uuid)
            pdf_path = os.path.join(pdf_floder_path, filename)
            os.mkdir(pdf_floder_path)
            file.save(pdf_path)
            try:
                fp = pdf2pdf(pdf_path)
                app.config['executor_file'].submit(shutil.rmtree, pdf_floder_path)
            except subprocess.TimeoutExpired as e:
                app.config['executor_file'].submit(shutil.rmtree, pdf_floder_path)
                return "convert timeout",403
            except Exception as e:
                app.config['executor_file'].submit(shutil.rmtree, pdf_floder_path)
                return str(e),500

            app.config['COUNT'] += 1
            return send_file(fp,as_attachment=True,attachment_filename=filename)
    elif request.method == 'GET':
        return 'Completing %s document conversions'%app.config['COUNT']
    return "unknow error", 500


def pdf2pdf(pdf_path):
    out_folder_uuid =  str(uuid.uuid4())
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], out_folder_uuid)
    os.mkdir(folder_path)
    odg_path = convert_odg(folder_path,pdf_path)
    modif_zip(folder_path,odg_path)
    pdf_path = convert_pdf(folder_path,odg_path)
    fp = tempfile.TemporaryFile()
    with open(pdf_path,'rb')as f:
        fp.write(f.read())
        fp.seek(0)
    app.config['executor_file'].submit(shutil.rmtree, folder_path)
    return fp

def convert_odg(out_dir, pdf_path):
    cmd = ['libreoffice6.0','--convert-to','odg','--outdir',out_dir, pdf_path]
    # subprocess.check_output(cmd,timeout=1)
    popen = subprocess.Popen(cmd,)
    try:
        popen.wait(TIMEOUT)
    except Exception as e:
        popen.terminate()
        raise e
    odg_path = os.path.join(out_dir,pdf_path.split('/')[-1].split('.')[0] + '.odg')
    return odg_path


def modif_zip(out_dir, odg_path):
    folder_path = os.path.join(out_dir,  str(uuid.uuid4()))
    with zipfile.ZipFile(odg_path, 'r') as myzip:
        myzip.extractall(folder_path)

    content_path = os.path.join(folder_path, 'content.xml')
    modify_cmd = ['sed','-i','s/style:text-outline="true"/style:text-outline="false"/g',content_path]
    subprocess.check_output(modify_cmd,timeout=TIMEOUT)

    with zipfile.ZipFile(odg_path, 'w') as myzip:
        for obj in os.walk(folder_path):
            for file_name in obj[2]:
                file_path = obj[0] + os.sep + file_name
                myzip.write(file_path,arcname=file_path.replace(folder_path,'').lstrip('/'))

def convert_pdf(out_dir, odg_path):
    cmd = ['libreoffice6.0','--convert-to','pdf','--outdir',out_dir, odg_path]
    popen = subprocess.Popen(cmd,)
    try:
        popen.wait(TIMEOUT)
    except Exception as e:
        popen.terminate()
        raise e

    pdf_path = os.path.join(out_dir,odg_path.split('/')[-1].split('.')[0] + '.pdf')
    return pdf_path


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=5000)
