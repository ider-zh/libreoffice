import os, time, zipfile, tempfile, uuid, shutil, subprocess, json

TIMEOUT = 20
def convert_odg():
    cmd = ['libreoffice6.0','--convert-to','odg','--outdir','test/out','test/a.pdf']
    # subprocess.check_output(cmd,timeout=1)
    popen = subprocess.Popen(cmd,)
    try:
        popen.wait(TIMEOUT)
    except subprocess.TimeoutExpired as e:
        popen.terminate()
    odg_path = os.path.join('test/out','test/a.pdf'.split('/')[-1].split('.')[0] + '.odg')
    return odg_path

def modif_zip():
    fp = tempfile.TemporaryFile()
    source = 'test/out/a.odg'
    folder_path = os.path.join('test/out',  str(uuid.uuid4()))
    with zipfile.ZipFile(source, 'r') as myzip:
        myzip.extractall(folder_path)

    content_path = os.path.join(folder_path, 'content.xml')
    modify_cmd = ['sed','-i','s/style:text-outline="true"/style:text-outline="false"/g',content_path]
    subprocess.check_output(modify_cmd,timeout=TIMEOUT)

    with zipfile.ZipFile('test/out/b.odg', 'w') as myzip:
        for obj in os.walk(folder_path):
            for file_name in obj[2]:
                file_path = obj[0] + os.sep + file_name
                myzip.write(file_path,arcname=file_path.replace(folder_path,'').lstrip('/'))

def convert_pdf():
    cmd = ['libreoffice6.0','--convert-to','pdf','--outdir','test/out','test/out/b.odg']
    popen = subprocess.Popen(cmd,)
    try:
        popen.wait(TIMEOUT)
    except subprocess.TimeoutExpired as e:
        popen.terminate()

# print(convert_odg())

# modif_zip()
# convert_pdf()
pf = open('test/temp.txt','r')
os.remove('test/temp.txt')
print(pf.read())
pf.close()
