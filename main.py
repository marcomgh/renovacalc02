from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
import pandas as pd

app = FastAPI()

# Pagina principale
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <body style="font-family: Arial; margin: 40px;">
            <h2>Carica un file e cerca una voce</h2>
            <form action="/search" method="post" enctype="multipart/form-data">
                <p><input type="file" name="file" required></p>
                <p><input type="text" name="query" placeholder="Voce da cercare" required></p>
                <button type="submit">Cerca</button>
            </form>
        </body>
    </html>
    """

# Ricerca nel file
@app.post("/search", response_class=HTMLResponse)
async def search(file: UploadFile = File(...), query: str = Form(...)):
    try:
        # Legge CSV o Excel
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file.file)
        elif file.filename.endswith(".xlsx"):
            df = pd.read_excel(file.file)
        else:
            return "<h3>Formato non supportato. Usa CSV o XLSX.</h3>"

        # Cerca la voce in tutte le colonne
        mask = df.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)
        results = df[mask]

        if results.empty:
            return f"<h3>Nessun risultato trovato per: <b>{query}</b></h3>"

        # Converte risultati in tabella HTML
        table_html = results.to_html(index=False)

        return f"""
        <h3>Risultati per: <b>{query}</b></h3>
        {table_html}
        <br><a href="/">Torna indietro</a>
        """

    except Exception as e:
        return f"<h3>Errore: {str(e)}</h3>"
