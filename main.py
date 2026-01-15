from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
import pandas as pd

app = FastAPI()


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


@app.post("/search", response_class=HTMLResponse)
async def search(file: UploadFile = File(...), query: str = Form(...)):
    try:
        filename = file.filename.lower()

        # --- CSV in streaming, super-veloce ---
        if filename.endswith(".csv"):
            results = []
            chunksize = 2000  # dimensione blocco per non saturare RAM

            # reset del puntatore del file (per sicurezza)
            file.file.seek(0)

            for chunk in pd.read_csv(file.file, chunksize=chunksize, dtype=str):
                chunk = chunk.fillna("").astype(str)

                # colonna unica per la ricerca (molto veloce)
                combined = chunk.agg(" ".join, axis=1)
                mask = combined.str.contains(query, case=False, na=False)

                if mask.any():
                    results.append(chunk[mask])

            if not results:
                return f"<h3>Nessun risultato trovato per: <b>{query}</b></h3>"

            final_df = pd.concat(results, ignore_index=True)
            table_html = final_df.to_html(index=False)

            return f"""
            <h3>Risultati per: <b>{query}</b></h3>
            {table_html}
            <br><a href="/">Torna indietro</a>
            """

        # --- XLSX veloce ---
        elif filename.endswith(".xlsx"):
            file.file.seek(0)
            df = pd.read_excel(file.file, dtype=str)
            df = df.fillna("").astype(str)

            combined = df.agg(" ".join, axis=1)
            mask = combined.str.contains(query, case=False, na=False)

            results = df[mask]

            if results.empty:
                return f"<h3>Nessun risultato trovato per: <b>{query}</b></h3>"

            table_html = results.to_html(index=False)

            return f"""
            <h3>Risultati per: <b>{query}</b></h3>
            {table_html}
            <br><a href="/">Torna indietro</a>
            """

        else:
            return "<h3>Formato non supportato. Usa CSV o XLSX.</h3>"

    except Exception as e:
        return f"<h3>Errore: {str(e)}</h3>"
