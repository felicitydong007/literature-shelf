# Literature Shelf

A small local PDF literature manager built with Python, SQLite, and Streamlit.

It scans a folder of PDF papers, builds a local database, extracts abstracts when possible, guesses publication year, assigns a category, creates short English search tags, and gives you a browser-based shelf for searching and editing metadata.

## What this tool does

Literature Shelf is a small local tool for researchers who keep many PDF papers in one folder.

It does not replace Zotero, EndNote, or other reference managers. Instead, it provides a lightweight personal shelf for quickly searching local PDFs, adding simple tags, writing notes, and organizing papers by research topic.

All PDFs and the local database stay on your own computer. The code can be shared publicly on GitHub, but your PDF papers and `literature.db` file should remain private.

## Features

- Scan local PDF files into a SQLite database
- Extract abstracts from the first pages of PDFs when possible
- Guess title, year, category, and short English tags
- Search by filename, title, author, abstract, tag, or notes
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

## One-minute usage

For Windows users:

1. Put your PDF papers in this project folder.
2. Double-click `scan_papers.bat` to scan papers.
3. Double-click `run_shelf.bat` to open the literature shelf.
4. Open the local webpage shown in the terminal, usually:

http://127.0.0.1:8501

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

To regenerate automatic categories and tags after improving the classification rules:

```bash
python scan_papers.py --refresh-all
```

Normal rescanning keeps manually edited tags and categories. Use `--refresh-all` only when you want to rebuild the automatic metadata.

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
refresh_all.bat
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
scan_papers.py      PDF scanner, abstract extractor, and classifier
requirements.txt    Python dependencies
scan_papers.bat     Windows helper script for normal scanning
refresh_all.bat     Windows helper script for rebuilding automatic metadata
run_shelf.bat       Windows helper script for launching the app
.streamlit/         Streamlit local config
.gitignore          Keeps PDFs, database, and local environment out of Git
```

## License

MIT License.
