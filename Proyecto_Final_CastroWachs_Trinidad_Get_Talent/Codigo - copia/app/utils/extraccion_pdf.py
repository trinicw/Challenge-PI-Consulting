import pdfplumber

def extraer_texto_pdf(pdf_path, txt_path):
    """
    Extrae el texto de un archivo PDF y lo guarda en un archivo de texto.
    :param pdf_path: Ruta del archivo PDF.
    :param txt_path: Ruta del archivo de salida (.txt).
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            texto = ""
            # Iterar sobre cada página del PDF
            for pagina in pdf.pages:
                texto += pagina.extract_text()

        # Guardar el texto extraído en un archivo .txt
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(texto)

        print(f"Texto extraído y guardado en: {txt_path}")

    except Exception as e:
        print(f"Error extrayendo el texto: {e}")

# Ejecutar el proceso de extracción
if __name__ == "__main__":
    extraer_texto_pdf("./data/INFORMACION.pdf", "./data/INFORMACION_LIMPIO.txt")
