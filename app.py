# compose_flask/app.py
# import redis
import os
import re
# import requests
import nltk

from flask import Flask, render_template, request
# from PyPDF2 import PdfFileReader, PdfFileWriter
from werkzeug.utils import secure_filename
# from werkzeug.datastructures import  FileStorage

from io import StringIO

from pdfminer.converter import TextConverter 
from pdfminer.pdfinterp import PDFPageInterpreter 
from pdfminer.pdfinterp import PDFResourceManager 
from pdfminer.pdfpage import PDFPage 
from pdfminer.layout import LAParams

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('stopwords')
 
PHONE_REG = re.compile(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]')
EMAIL_REG = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+')
 
SKILLS_DB = [
    'machine learning',
    'data science',
    'python',
    'word',
    'excel',
    'English','Git', 'Django', 'PostgreSQL', 'Gitlab', 'CI/CD', 'Ansible', 'Aliyun'
]
 
RESERVED_WORDS = [
    'school',
    'college',
    'univers',
    'academy',
    'faculty',
    'institute',
    'faculdades',
    'Schola',
    'schule',
    'lise',
    'lyceum',
    'lycee',
    'polytechnic',
    'kolej',
    'ünivers',
    'okul',
]
 
app = Flask(__name__)
#redis = Redis(host='redis', port=6379)

path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, 'upload')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

def extract_names(txt):
    person_names = []
 
    for sent in nltk.sent_tokenize(txt):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
            if hasattr(chunk, 'label') and chunk.label() == 'PERSON':
                person_names.append(
                    ' '.join(chunk_leave[0] for chunk_leave in chunk.leaves())
                )
 
    return person_names

def extract_phone_number(resume_text):
    phone = re.findall(PHONE_REG, resume_text)
 
    if phone:
        number = ''.join(phone[0])
 
        if resume_text.find(number) >= 0 and len(number) < 16:
            return number
    return None
 
def extract_emails(resume_text):
   email=re.findall(EMAIL_REG, resume_text)
   return email[0]

 
def extract_skills(input_text):
    stop_words = set(nltk.corpus.stopwords.words('english'))
    word_tokens = nltk.tokenize.word_tokenize(input_text)
 
    # remove the stop words
    filtered_tokens = [w for w in word_tokens if w not in stop_words]
 
    # remove the punctuation
    filtered_tokens = [w for w in word_tokens if w.isalpha()]
 
    # generate bigrams and trigrams (such as artificial intelligence)
    bigrams_trigrams = list(map(' '.join, nltk.everygrams(filtered_tokens, 2, 3)))
 
    # we create a set to keep the results in.
    found_skills = set()
 
    # we search for each token in our skills database
    for token in filtered_tokens:
        if token.lower() in SKILLS_DB:
            found_skills.add(token)
 
    # we search for each bigram and trigram in our skills database
    for ngram in bigrams_trigrams:
        if ngram.lower() in SKILLS_DB:
            found_skills.add(ngram)
 
    return found_skills

def extract_education(input_text):
    organizations = []
 
    # first get all the organization names using nltk
    for sent in nltk.sent_tokenize(input_text):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
            if hasattr(chunk, 'label') and chunk.label() == 'ORGANIZATION':
                organizations.append(' '.join(c[0] for c in chunk.leaves()))
 
    # we search for each bigram and trigram for reserved words
    # (college, university etc...)
    education = set()
    for org in organizations:
        for word in RESERVED_WORDS:
            if org.lower().find(word) >= 0:
                education.add(org)
 
    return education

@app.route('/')
def hello():
 #   redis.incr('hits')
    html='''<html>
       <body>
          <form action = "http://103.56.148.64:5000/parse" method = "POST" 
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

@app.route('/parse', methods = ['GET', 'POST'])
def read_pdf():
   if request.method == 'POST':

      f = request.files['file']
      file_name=secure_filename(f.filename)
      f.save(os.path.join(app.config['UPLOAD_FOLDER'],file_name))

      # link = request.args.get('file')
      FILE_PATH=os.path.join(app.config['UPLOAD_FOLDER'],file_name)
      # link = os.path.join(app.config['UPLOAD_FOLDER'],file_name)
      codec = 'utf-8'  # 'utf16','utf-8'
      laparams = LAParams()
      resource_manager = PDFResourceManager()
      fake_file_handle = StringIO()
      converter = TextConverter(resource_manager, fake_file_handle, laparams=laparams)
      page_interpreter = PDFPageInterpreter(resource_manager, converter)
      with open(FILE_PATH, 'rb') as fh:
         for page in PDFPage.get_pages(fh, caching=True,check_extractable=True):           
               page_interpreter.process_page(page)     
         text = fake_file_handle.getvalue() 
      # close open handles      
      converter.close() 
      fake_file_handle.close() 
      
      final_content=text

      name=extract_names(final_content)
      contact=extract_phone_number(final_content)
      email=extract_emails(final_content)
      skills=extract_skills(final_content)
      education=extract_education(final_content)
      # print(final_content)
      html="""<html>
         <body>
         <h4>Name: {}</h4>
         <p>Contact: {}/{}</p>
         <p>Skills: {}</p>
         <p>education: {}</p>
         <p>{}</p>
         </body>
      </html>""".format(
         name,
         contact,
         email,
         skills,
         education,
         final_content
      )
      return html



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)