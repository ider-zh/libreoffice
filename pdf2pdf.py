#!/usr/bin/python3

import requests
import sys
import json
import zipfile
import tempfile
import subprocess

def main():
    files = {'file': open('test/a.pdf', 'rb')}
    req = requests.post('http://localhost:5000/pdf2pdf', files=files)
    if req.status_code != 200:
        print(req.text)
        return
    with open('test/b.pdf','wb')as f:
        f.write(req.content)


if __name__ == '__main__':
    main()
