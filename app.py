import streamlit as st
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from docx import Document
import io
import requests
import qrcode
from PIL import Image

# --- Konfiguracja strony ---
st.set_page_config(page_title="Kombajn do kodów qr (wersja demo)", layout="centered")

def create_word_file(text, extra=""):
    doc = Document()
    doc.add_heading('Wynik odczytu kodu', 0)
    p = doc.add_paragraph()
    p.add_run('Odczytana treść: ').bold = True
    doc.add_paragraph(text)
    if extra:
        p2 = doc.add_paragraph()
        p2.add_run('Analiza z bazy danych:').bold = True
        doc.add_paragraph(extra)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def analyze_ean(ean):
    extra_info = ""
    kraj = "Nieznany / reszta świata"
    if ean.startswith('590'): kraj = "Polska"
    elif ean.startswith(('40', '41', '42', '43', '44')): kraj = "Niemcy"
    extra_info += f"Kraj rejestracji: {kraj}\n\n"

    try:
        data_food = requests.get(f"https://world.openfoodfacts.org/api/v0/product/{ean}.json", timeout=3).json()
        if data_food.get('status') == 1 and data_food['product'].get('product_name'):
            extra_info += f"Produkt: {data_food['product'].get('product_name')}\n"
    except: pass
    return extra_info

# --- Tytuł główny ---
st.title("Kombajn do kodów qr i kreskowych")
st.info("To jest wersja demonstracyjna. Pełna, ultraszybka wersja skanująca wideo na żywo (na system Windows) jest dostępna na zamówienie.")

# --- Zakładki ---
tab1, tab2 = st.tabs(["Dekodowanie (skaner)", "Nadawanie (generator)"])

# --- Zakładka 1: Skaner ---
with tab1:
    st.header("Odczytaj kod")
    opcja = st.radio("Wybierz metodę skanowania:", ["Zrób zdjęcie z kamery", "Wgraj plik z dysku"])
    
    img_file_buffer = None
    if opcja == "Zrób zdjęcie z kamery":
        img_file_buffer = st.camera_input("Skieruj kod na kamerę i kliknij 'Take Photo'")
    else:
        img_file_buffer = st.file_uploader("Wybierz zdjęcie z kodem", type=['png', 'jpg', 'jpeg'])

    if img_file_buffer is not None:
        try:
            # Nowe, kuloodporne ładowanie obrazów
            image = Image.open(img_file_buffer)
            img_array = np.array(image.convert('RGB'))
            codes = decode(img_array)

            if codes:
                dane = codes[0].data.decode("utf-8")
                typ = codes[0].type
                st.success(f"Rozpoznano: {typ}")
                
                analiza = ""
                if typ in ['EAN13', 'EAN8', 'UPCA']:
                    analiza = analyze_ean(dane)
                
                st.write("**Oryginalny odczyt:**")
                st.code(dane)
                if analiza:
                    st.write("**Dodatkowe informacje:**")
                    st.text(analiza)
                
                docx_file = create_word_file(dane, analiza)
                st.download_button("📥 Pobierz pełny raport (Word)", data=docx_file, file_name="raport_skanowania.docx")
            else:
                st.error("Nie wykryto kodu qr ani kreskowego na tym zdjęciu. Spróbuj przybliżyć lub użyć wyraźniejszego zdjęcia.")
        except Exception as e:
            st.error(f"Wystąpił techniczny problem z tym plikiem: {e}")

# --- Zakładka 2: Generator ---
with tab2:
    st.header("Wygeneruj własny kod qr")
    tekst_do_kodu = st.text_area("Wpisz tekst, link lub adres portfela:", height=100)
    
    if st.button("🛠️ Generuj kod"):
        if tekst_do_kodu.strip() == "":
            st.warning("Musisz wpisać jakiś tekst!")
        else:
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(tekst_do_kodu)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.image(byte_im, caption="Twój gotowy kod qr", width=300)
            st.download_button("💾 Pobierz obrazek (.png)", data=byte_im, file_name="moj_kod_qr.png", mime="image/png")
