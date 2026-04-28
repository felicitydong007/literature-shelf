# Literature Shelf

A small local PDF literature manager built with Python, SQLite, and Streamlit.

It scans a folder of PDF papers, builds a local database, guesses publication year, assigns a category, creates short English search tags, and gives you a browser-based shelf for searching and editing metadata.

## Features

- Scan local PDF files into a SQLite database
- Guess title, year, category, and short English tags
- Search by filename, title, author, tag, or notes
- Filter papers by category
- Edit category, tags, and notes in the browser
- Open the original PDF from the shelf
- Export the current filtered list to CSV
- Keep your manual tags when rescanning

## Important

Do not upload copyrighted PDF papers to GitHub.

This project is designed so the code can be public, while your PDFs and local database stay private. The `.gitignore` file excludes:

- `*.pdf`
- `literature.db`
- `.venv/`
- log files

## Quick Start

### 1. Install Python

Install Python 3.9 or newer from:

https://www.python.org/downloads/

On Windows, check `Add python.exe to PATH` during installation.

### 2. Create a virtual environment

Open a terminal in the project folder:

```powershell
cd D:\download_papers
py -3.9 -m venv .venv
.\.venv\Scripts\activate
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If PyPI is slow in China, you can use:

```powershell
python -m pip install --isolated --no-cache-dir -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com -r requirements.txt
```

### 4. Add PDFs

Put your PDF files in the project folder.

### 5. Scan papers

```bash
python scan_papers.py
```

To regenerate all automatic tags:

```bash
python scan_papers.py --refresh-tags
```

Normal rescanning keeps manually edited tags.

### 6. Run the shelf

```bash
streamlit run app.py
```

Then open:

```text
http://127.0.0.1:8501
```

On Windows, you can also double-click:

```text
scan_papers.bat
run_shelf.bat
```

## Suggested Workflow

1. Put new PDFs into the folder.
2. Run `python scan_papers.py`.
3. Run `streamlit run app.py`.
4. Search, filter, and manually improve tags while reading.
5. Use tags as your personal retrieval memory.

## Categories

The current rule-based classifier is tuned for biomedical and drug-discovery literature, including:

- GPCR structural pharmacology
- Screening methods / DEL
- Targeted protein degradation
- Protein design / AI
- Structural biology / Cryo-EM
- Antibody / CAR-T / immunotherapy
- Medicinal chemistry / drug discovery
- Psychiatry / neuropharmacology
- Metabolism / endocrine
- Methods / assays / biosensors

You can customize these rules in `scan_papers.py`.

## Project Files

```text
app.py              Streamlit browser interface
scan_papers.py      PDF scanner and classifier
requirements.txt    Python dependencies
scan_papers.bat     Windows helper script for scanning
run_shelf.bat       Windows helper script for launching the app
.streamlit/         Streamlit local config
.gitignore          Keeps PDFs, database, and local environment out of Git
```

## License

MIT License.
