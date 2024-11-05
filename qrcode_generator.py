import streamlit as st
import segno
import time

st.set_page_config(
    page_title="qrcode generator"
)

st.title("QR CODE Generator")

url = st.text_input("Please enter your url you want to encode:")

def generate_qrcode(url):
    qrcode = segno.make_qr(url)
    qrcode.save("C:/Users/Tom/OneDrive/Pictures/qrcode_streamlit.png",
                scale=5)

if url:
    with st.spinner("Generate QR Code"):
        time.sleep(1)
    generate_qrcode(url)
    st.image("C:/Users/Tom/OneDrive/Pictures/qrcode_streamlit.png")

st.write(url)