# compose_flask/app.py
from flask import Flask, render_template, request
from PyPDF2 import PdfFileReader, PdfFileWriter
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import redis
import os

app = Flask(__name__)
#redis = Redis(host='redis', port=6379)

path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, 'upload')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

@app.route('/')
def hello():
 #   redis.incr('hits')
    html='''<html>
       <body>
          <form action = "http://103.56.148.64:5000/uploader" method = "POST" 
             enctype = "multipart/form-data">
             Test gita
             <input type = "file" name = "file" />
             <input type = "submit"/>
          </form>   
       </body>
    </html>'''
    return html

@app.route('/upload')
def upload_file():
   return render_template('upload.html')
	
@app.route('/uploader', methods = ['GET', 'POST'])
def uploader_file():
   if request.method == 'POST':
      f = request.files['file']
      file_name=secure_filename(f.filename)
      f.save(os.path.join(app.config['UPLOAD_FOLDER'],file_name))
      #f.save(secure_filename(f.filename))
      #return 'file uploaded successfully'
      # name = os.path.join(app.config['UPLOAD_FOLDER'],file_name)
      link = secure_filename(f.filename)
      html="""<html>
         <body>
            <a href="parse?file={}"> Parse PDF</a> 
            <br>
         </body>
      </html>""".format(
        link
      )
      return html
      # return os.path.join(app.config['UPLOAD_FOLDER'],file_name)

@app.route('/parse')
def read_pdf():
   if request.method == 'GET':
      # link = request.args.get('file')
      content=""""""
      pdf = PdfFileReader(os.path.join(app.config['UPLOAD_FOLDER'],link))
      for page_num in range(pdf.numPages):
         pageObj = pdf.getPage(page_num)
         try:
            txt=pageObj.extractText()
            content = content+''.center(100,'-')
         except:
            pass
         else:
            content = content+'Page {0}\n'.format(page_num+1)
            content = content+''.center(100,'-')

      # link = os.path.join(app.config['UPLOAD_FOLDER'],file_name)
      html="""<html>
         <body>
            <h3>"{}"</h3>
         </body>
      </html>""".format(
        content
      )
      return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)