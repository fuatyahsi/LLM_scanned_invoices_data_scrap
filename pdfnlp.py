#!/usr/bin/env python
# coding: utf-8

# In[3]:


#pip install streamlit
#pip install PyMuPDF

# In[44]:


from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline
import torch
import streamlit as st
import pickle
import pdfplumber
from pdfminer.high_level import extract_pages, extract_text
from PIL import Image
import time
#import fitz
import pdf2image
import pytesseract
from pytesseract import Output, TesseractError
import base64
from io import StringIO
import fitz


st.set_page_config(
    page_title="AFAD",
    page_icon="bayrak.png",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={

        'About': "Developed by Fuat YAHŞİ"
    }
)

html_temp = """
<div style="background-color:red;padding:3px">
<h4 style="color:white;text-align:center;">Acil Yardım Fatura Analiz </h4>
</div>"""


img = Image.open("AFAD_page-0001.jpg")
st.markdown(html_temp, unsafe_allow_html=True)
st.markdown(" ")
st.image(img, caption="BARINMA VE YAPIM İŞLERİ GENEL MÜDÜRLÜĞÜ",clamp=False)

tokenizer = AutoTokenizer.from_pretrained("savasy/bert-base-turkish-squad")
model = AutoModelForQuestionAnswering.from_pretrained("savasy/bert-base-turkish-squad")
nlp = pipeline("question-answering", model=model, tokenizer=tokenizer)

def fatura_analiz(fatura_liste):
    text = ""
    fatura = pdfplumber.open(fatura_liste)
    for sayfa in fatura.pages:
        text += sayfa.extract_text(keep_blank_chars=True)
    return text
            
def alternative_fatura_analiz(fatura_liste):
    text = "".join([i.extract_text(keep_blank_chars=True) for i in pdfplumber.open(fatura_liste[0]).pages])

    return text


def displayPDF(uploaded_file):
    
    # Read file as bytes:
    bytes_data = uploaded_file.getvalue()

    # Convert to utf-8
    base64_pdf = base64.b64encode(bytes_data).decode('utf-8')

    # Embed PDF in HTML
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="700" type="application/pdf"></iframe>'

    # Display file
    st.markdown(pdf_display, unsafe_allow_html=True)


###########################################################################################################################################           
pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract.exe' ## adding tesseract path to env
############################################################################################################################################

config = '--oem 3  --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ'




with st.sidebar:
    markdown = st.markdown("#### Kullanıcı Bilgileri")
    form_1 = st.form("my_form", border=True)
    with form_1:
        username = st.text_input("Kullanıcı Adı", placeholder="örnek(fuat.yahsi)",key = 1)
        password = st.text_input("Kullanıcı Şifresi", placeholder="*********", type="password",key=2)
        login_button = st.form_submit_button("Login")
        

fatura_num = ""
    
    
            
if username and password:
        with st.chat_message("assistant"):
            st.write("Merhaba 👋, Ben fatura bilgilerini okumak için eğitilmiş bir :red[yapay zeka modeli]yim.")
            st.markdown(" ")
            st.write("Bilgilerini öğrenmek istediğin faturayı aşağıya yüklemelisin")
            doc_type =st.selectbox(label = "Dosya tipini seçiniz",options = ["Pdf Formatında Orjinal Fatura","Pdf Formatında Taranmış Fatura"],index = None,placeholder="Lütfen seçiniz")
            text = "" ########################################## empty string is assigned to text
            
            if doc_type == "Pdf Formatında Orjinal Fatura":
                fatura_liste = st.file_uploader(label="",accept_multiple_files=False,key = "original",type="pdf")
                if fatura_liste:
                    st.write("""Faturadaki verileri inceliyorum.....""")
                    text = fatura_analiz(fatura_liste)
                    text = text.replace("-","")


            
            elif doc_type == "Pdf Formatında Taranmış Fatura" :
                fatura_liste = st.file_uploader(label="Taranmıi PDF dosyanızı yükleyiniz",accept_multiple_files=False,key = "scanned",type="pdf")
                fatura_num = st.selectbox(label = "Yüklediğiniz PDF dosyasındaki faturalar adedini seçiniz",
                options=["Yüklediğim PDF dosyası tek bir faturadan oluşuyor","Yüklediğim PDF dosyası birden çok faturadan oluşuyor"],index = None,placeholder = "Lütfen Seçiniz")
                
                if fatura_num  == "Yüklediğim PDF dosyası tek bir faturadan oluşuyor":
                    images = pdf2image.convert_from_path(fatura_liste.name,dpi = 350,poppler_path = "C:\Program Files\poppler-23.11.0\Library\\bin")
              
                    for t in range(len(images)):
                        pil_im = images[t] 
                        text = pytesseract.image_to_string(image = pil_im,lang="tur")
                        
                        text = text.replace("Ek-1","")
                        text = text.replace("-","")
                        text += text
                elif fatura_num  == "Yüklediğim PDF dosyası birden çok faturadan oluşuyor":
                    st.info("Yüklediğiniz fatura dosyasından okumamı istediğiniz faturanın sayfa numaralarını giriniz")
                    first_page = st.number_input(label ="Bilgilerini istediğiniz faturanın başladığı sayfa numarası",value = None,placeholder="İlk sayfa")
                    last_page = st.number_input(label ="Bilgilerini istediğiniz faturanın bittiği sayfa numarası",value = None,placeholder = "Son sayfa")
                    if last_page and first_page and (last_page >= first_page) and( last_page,first_page != 0,0) :
                        file = fitz.open(fatura_liste)
                        tar = fitz.open() 
                        tar.insert_pdf(docsrc = file, from_page=int(first_page)-1, to_page=int(last_page)-1)
                        tar.save("fatura_1.pdf")
                        tar.close()
                        images = pdf2image.convert_from_path(pdf_path="fatura_1.pdf",dpi=350,poppler_path="C:\Program Files\poppler-23.11.0\Library\\bin")
                      
                        for t in range(len(images)):
                            pil_im = images[t] 
                            ocr_dict = pytesseract.image_to_data(pil_im, lang='tur', output_type=Output.DICT)
                            # ocr_dict now holds all the OCR info including text and location on the image
                            text += " ".join(ocr_dict['text'])
                            text = text.replace("Ek-1","")
                            text = text.replace("-","")
                    

                            
                    ##
                
                
            st.write(text)
            if text != "" :
                fatura_tarihi = nlp(question = "fatura tarihi nedir?",context = text)["answer"]
                fatura_tarihi = "".join([i for i in fatura_tarihi if i.isnumeric()])
                fatura_tarihi = fatura_tarihi[:2]+"."+fatura_tarihi[2:4]+"."+fatura_tarihi[4:]
                ETTN = nlp(question = "ETTN :?",context = text)["answer"]
                ETTN = ETTN[:8]+"-"+ETTN[8:12]+"-"+ETTN[12:16]+"-"+ETTN[16:20]+"-"+ETTN[20:]
                fatura_numarası = nlp(question = "fatura numarası nedir?",context = text)["answer"]
                fatura_numarası = "".join([i for i in fatura_numarası if i not in '!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n'])
                mal_ve_hizmet_toplamı = nlp(question = "Mal Hizmet Toplam Tutarı kaç TL'dir?",context = text)["answer"]
                mal_ve_hizmet_toplamı = "".join([i for i in mal_ve_hizmet_toplamı if i in ["0","1","2","3","4","5","6","7","8","9",",","."]])
                vergiler_dahil_toplam = nlp(question = "vergiler dahil toplam kaç TL'dir?",context = text)["answer"]
                vergiler_dahil_toplam = "".join([i for i in vergiler_dahil_toplam if i in ["0","1","2","3","4","5","6","7","8","9",",","."]])
                #KDV = nlp(question = "faturanın KDV değeri kaç TL'dir?",context = text)["answer"]
                genel_toplam=nlp(question = "ödenekcek tutar veya genel toplam veya Ödenecek tutar kaç TL'dir?",context = text)["answer"]
                genel_toplam = "".join([i for i in genel_toplam if i in ["0","1","2","3","4","5","6","7","8","9",",","."]])
                    
    
                with st.form("second_form"):
                    st.write("📋 Yüklediğiniz faturaya ait bilgiler getirilmiştir")
                    st.info(f"Yüklediğiniz faturanın tarihi: {fatura_tarihi}")
                    st.info(f"Yüklediğiniz faturanın ETTN numarası: {ETTN}")
                    st.info(f"Yüklediğiniz faturanın numarası: {fatura_numarası}")
                    st.info(f"Yüklediğiniz faturanın Mal ve Hizmet Toplamı: {mal_ve_hizmet_toplamı}")
                    #st.info(f"Yüklediğiniz faturanın KDV tutarı: {KDV}")
                    st.info(f"Yüklediğiniz faturanın Vergiler Dahil Toplam Tutarı/Genel Toplam: {genel_toplam}")
                    submitted = st.form_submit_button("Faturanın aslını gör")
                    
                    if submitted:
                        if fatura_num  == "Yüklediğim PDF dosyası birden çok faturadan oluşuyor":
                            with open("fatura_1.pdf","rb") as f:
                                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                                pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="700" type="application/pdf"></iframe>'
                                st.markdown(pdf_display, unsafe_allow_html=True)
                        
                        displayPDF(fatura_liste)
                            
                                    
                                
                                




