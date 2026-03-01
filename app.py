import streamlit as st
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from docx import Document
import io

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Skaner QR & AI News", layout="centered")

# --- FUNKCJA GENERUJĄCA PLIK WORD ---
def create_word_file(text):
    doc = Document()
    doc.add_heading('Wynik odczytu kodu QR', 0)
    p = doc.add_paragraph()
    p.add_run('Odczytana treść:').bold = True
    doc.add_paragraph(text)
    
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- MENU GŁÓWNE (ZAKŁADKI) ---
tab1, tab2, tab3 = st.tabs(["📱 Skaner QR (Demo)", "📰 Wiadomości AI", "📞 Kontakt"])

# --- ZAKŁADKA 1: PROGRAM ---
with tab1:
    st.title("Skaner Kodów QR")
    st.write("To jest wersja demonstracyjna mojego programu. Użyj kamery, aby zeskanować kod.")

    img_file_buffer = st.camera_input("Zrób zdjęcie kodu QR")

    if img_file_buffer is not None:
        bytes_data = img_file_buffer.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        decoded_objects = decode(cv2_img)

        if decoded_objects:
            for obj in decoded_objects:
                dane = obj.data.decode("utf-8")
                st.success(f"Znaleziono kod! Treść: {dane}")
                
                docx_file = create_word_file(dane)
                
                st.download_button(
                    label="📥 Pobierz wynik w Word (.docx)",
                    data=docx_file,
                    file_name="wynik_skanowania.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        else:
            st.warning("Nie wykryto kodu QR na zdjęciu. Spróbuj przybliżyć lub poprawić oświetlenie.")

# --- ZAKŁADKA 2: WIADOMOŚCI ---
with tab2:
    st.header("Najnowsze wieści ze świata Sztucznej Inteligencji")
    st.write("Witaj w sekcji newsowej! Tutaj publikuję analizy i nowości.")

# --- ZAKŁADKA 3: KONTAKT ---
with tab3:
    st.header("Zainteresowany pełną wersją?")
    st.info("""
    Prezentowany skaner to tylko wersja demonstracyjna działająca w chmurze.
    Cena pełnej licencji na system Windows: Do uzgodnienia.
    """)
    st.write("📩 Skontaktuj się ze mną prywatnie, aby uzyskać dostęp.")
