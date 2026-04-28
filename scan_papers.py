from __future__ import annotations

import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import fitz


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "literature.db"


CLASSIFICATION_RULES = [
    (
        "Screening methods / DEL",
        [
            "dna-encoded",
            "dna encoded",
            "encoded library",
            "encoded libraries",
            "del technology",
            "del selection",
            "chemical library",
            "selection system",
            "selection methods",
            "hit-finding",
            "compound screening",
            "phenotypic screening",
            "high-throughput selection",
            "affinity chromatography",
            "aptamer",
            "spark-seq",
        ],
    ),
    (
        "GPCR structural pharmacology",
        [
            "gpcr",
            "g protein-coupled",
            "g-protein-coupled",
            "arrestin",
            "gpr",
            "5-ht",
            "serotonin receptor",
            "dopamine d2",
            "opioid receptor",
            "mu-opioid",
            "m-opioid",
            "kappa opioid",
            "glp-1 receptor",
            "apelin receptor",
            "chemokine receptor",
            "neurotensin receptor",
            "melatonin receptor",
            "mglut",
            "metabotropic glutamate",
            "taar1",
            "tgr5",
            "cb1",
            "cckbr",
            "p2ry",
            "oxgr1",
            "lgr4",
            "rhodopsin",
        ],
    ),
    (
        "Olfactory / taste receptors",
        [
            "olfactory",
            "odorant",
            "odor detection",
            "bitter taste",
            "taste gpcr",
            "or6a2",
            "or7a10",
            "or5v1",
            "vomeronasal",
            "taar1",
        ],
    ),
    (
        "Targeted protein degradation",
        [
            "protac",
            "targeted protein degrader",
            "targeted membrane protein degradation",
            "protein degradation",
            "degrade targets",
            "selectac",
            "spytac",
            "molecular glue",
            "crbn",
            "degradation-based",
            "cell-selective targeting chimeras",
            "conditionally activatable chimeras",
        ],
    ),
    (
        "Protein design / AI",
        [
            "de novo design",
            "rfdiffusion",
            "protein design",
            "binder design",
            "alphafold",
            "foldbench",
            "large language models",
            "foundation model",
            "generative design",
            "flow matching",
            "genome language models",
            "odesign",
            "halludesign",
            "mcgpcr",
            "deep learning",
            "virtual screening",
            "ai-driven",
        ],
    ),
    (
        "Structural biology / Cryo-EM",
        [
            "cryo-em",
            "cryo em",
            "cryosparc",
            "structure of",
            "structural basis",
            "structural insights",
            "structural snapshots",
            "high-resolution",
            "nmr probes",
            "mechanistic insights",
            "complex assembly",
        ],
    ),
    (
        "Antibody / CAR-T / immunotherapy",
        [
            "antibody",
            "nanobody",
            "car t",
            "car-t",
            "car-nk",
            "immunotherapy",
            "immune",
            "t cell",
            "t cells",
            "pd-1",
            "pd-l1",
            "pdl1",
            "cytokine",
            "interleukin",
            "tcr",
            "pmhc",
            "vaccine",
        ],
    ),
    (
        "Virology / antiviral",
        [
            "virus",
            "viral",
            "hiv",
            "hsv",
            "epstein",
            "ebv",
            "gammaherpesvirus",
            "cytomegalovirus",
            "antiviral",
            "bacteriophage",
            "kongming",
        ],
    ),
    (
        "Psychiatry / neuropharmacology",
        [
            "schizophrenia",
            "antipsychotic",
            "aripiprazole",
            "lurasidone",
            "latuda",
            "bipolar",
            "psychedelic",
            "psilocybin",
            "antidepressant",
            "ketamine",
            "cognition",
            "dopamine",
            "dystonia",
        ],
    ),
    (
        "Inflammation / pain",
        [
            "inflammatory",
            "inflammation",
            "arthritis",
            "osteoarthritis",
            "pain",
            "analgesic",
            "tlr",
            "sting inhibitor",
            "anti-inflammatory",
            "gout",
            "fibrosis",
        ],
    ),
    (
        "Metabolism / endocrine",
        [
            "metabolism",
            "metabolic",
            "cholesterol",
            "diabetes",
            "obesity",
            "anti-obesity",
            "glucose",
            "insulin",
            "hepatic steatosis",
            "adipose",
            "hormone",
            "bile acid",
            "fat preference",
            "mitochondrial",
        ],
    ),
    (
        "Medicinal chemistry / drug discovery",
        [
            "drug discovery",
            "small molecule",
            "small-molecule",
            "ligand",
            "agonist",
            "antagonist",
            "inhibitor",
            "allosteric modulator",
            "covalent",
            "polypharmacology",
            "therapeutics",
            "pharmacology",
            "drug design",
            "hit discovery",
        ],
    ),
    (
        "Genomics / gene editing",
        [
            "base editing",
            "mrna",
            "chromatin",
            "transcription",
            "genome",
            "gene regulation",
            "sequencing",
            "rna",
            "cas13",
            "pre-rrna",
        ],
    ),
    (
        "Methods / assays / biosensors",
        [
            "biosensor",
            "assay",
            "split luciferase",
            "nanobit",
            "glosensor",
            "fluorescent sensor",
            "luminescence",
            "live cells",
            "recorder",
            "photo-cross-linking",
            "spycatcher",
            "spytag",
        ],
    ),
]


def term_in_text(term: str, text: str) -> bool:
    if term == "gpr":
        return re.search(r"\bgpr\d+\b", text) is not None
    if re.search(r"[^a-z0-9 -]", term):
        return term in text
    pattern = r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])"
    return re.search(pattern, text) is not None


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL UNIQUE,
            path TEXT NOT NULL,
            title TEXT,
            authors TEXT,
            year TEXT,
            abstract TEXT DEFAULT '',
            pages INTEGER,
            category TEXT DEFAULT 'Unsorted',
            tags TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            read_status TEXT DEFAULT 'Unread',
            added_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    ensure_columns(conn)
    return conn


def ensure_columns(conn: sqlite3.Connection) -> None:
    existing = {row[1] for row in conn.execute("PRAGMA table_info(papers)")}
    if "abstract" not in existing:
        conn.execute("ALTER TABLE papers ADD COLUMN abstract TEXT DEFAULT ''")


def clean_title(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text


def title_from_filename(path: Path) -> str:
    name = path.stem.replace("_", " ").replace("-", " ")
    return clean_title(name)


def guess_year(text: str) -> str:
    years = [int(x) for x in re.findall(r"\b(?:19|20)\d{2}\b", text)]
    valid = [year for year in years if 1950 <= year <= datetime.now().year + 1]
    return str(max(valid)) if valid else ""


def guess_category_and_tags(title: str, filename: str = "", abstract: str = "") -> tuple[str, str]:
    title_text = f"{title} {filename}".lower()
    abstract_text = abstract.lower()
    text = f"{title_text} {abstract_text}"
    matched_terms = []

    sensory_terms = [
        "olfactory",
        "odorant",
        "odor detection",
        "bitter taste",
        "taste gpcr",
        "or6a2",
        "or7a10",
        "or5v1",
        "vomeronasal",
    ]
    sensory_hits = [term for term in sensory_terms if term_in_text(term, text)]
    if sensory_hits:
        return "Olfactory / taste receptors", build_tags(title, filename, abstract, sensory_hits[:3])

    category_scores = []
    for category, terms in CLASSIFICATION_RULES:
        title_hits = [term.strip() for term in terms if term_in_text(term, title_text)]
        abstract_hits = [term.strip() for term in terms if term_in_text(term, abstract_text)]
        hits = list(dict.fromkeys(title_hits + abstract_hits))
        if hits:
            score = len(title_hits) * 3 + len(abstract_hits)
            category_scores.append((score, category, hits))

    if category_scores:
        _, category, hits = max(category_scores, key=lambda item: item[0])
        matched_terms.extend(hits[:3])
        return category, build_tags(title, filename, abstract, matched_terms)

    return "Unsorted", build_tags(title, filename, abstract, [])


def build_tags(title: str, filename: str, abstract: str, matched_terms: list[str]) -> str:
    text = f"{title} {filename} {abstract[:800]}".lower()
    words = re.findall(r"[a-z][a-z0-9-]{2,}", text)
    stopwords = {
        "the",
        "and",
        "for",
        "with",
        "from",
        "into",
        "using",
        "based",
        "mediated",
        "human",
        "novel",
        "reveals",
        "discovery",
        "design",
        "study",
        "using",
        "show",
        "shown",
        "important",
        "results",
        "suggest",
        "provide",
        "identify",
        "identified",
        "revealed",
        "analysis",
        "structure",
        "structures",
        "protein",
        "proteins",
    }
    useful = [word for word in words if word not in stopwords]
    tags = list(dict.fromkeys(matched_terms + useful[:5]))
    return " ".join(tags)[:80]


def extract_abstract(text: str) -> str:
    text = clean_title(text)
    if not text:
        return ""

    match = re.search(
        r"(?is)\babstract\b[:.\s-]*(.*?)(?=\b(?:keywords?|introduction|background|significance|results|methods|materials and methods)\b)",
        text,
    )
    if not match:
        match = re.search(r"(?is)\babstract\b[:.\s-]*(.{300,1800})", text)
    if not match:
        return ""

    abstract = clean_title(match.group(1))
    abstract = re.sub(r"^(article|research article|original article)\s+", "", abstract, flags=re.I)
    return abstract[:2000]


def read_pdf_metadata(path: Path) -> tuple[str, str, int, str, str]:
    title = ""
    authors = ""
    pages = 0
    first_page_text = ""
    abstract = ""
    try:
        with fitz.open(path) as doc:
            pages = doc.page_count
            metadata = doc.metadata or {}
            title = clean_title(metadata.get("title", ""))
            authors = clean_title(metadata.get("author", ""))
            sampled_pages = []
            for page_index in range(min(doc.page_count, 3)):
                sampled_pages.append(doc[page_index].get_text("text"))
            first_page_text = clean_title(sampled_pages[0][:3000]) if sampled_pages else ""
            abstract = extract_abstract("\n".join(sampled_pages))
    except Exception:
        pass

    if not title:
        title = title_from_filename(path)
    return title, authors, pages, first_page_text, abstract


def scan() -> None:
    refresh_tags = "--refresh-tags" in sys.argv
    refresh_categories = "--refresh-categories" in sys.argv
    refresh_all = "--refresh-all" in sys.argv
    pdfs = sorted(BASE_DIR.glob("*.pdf"))
    now = datetime.now().isoformat(timespec="seconds")
    conn = connect()

    inserted = 0
    updated = 0
    for pdf in pdfs:
        title, authors, pages, first_page_text, abstract = read_pdf_metadata(pdf)
        year = guess_year(title + " " + pdf.name + " " + first_page_text + " " + abstract)
        category, tags = guess_category_and_tags(title, pdf.name, abstract)

        existing = conn.execute(
            "SELECT id, tags, category, abstract FROM papers WHERE filename = ?",
            (pdf.name,),
        ).fetchone()

        if existing:
            current_tags = existing[1] or ""
            current_category = existing[2] or ""
            current_abstract = existing[3] or ""
            next_tags = tags if refresh_all or refresh_tags or not current_tags.strip() else current_tags
            next_category = (
                category
                if refresh_all or refresh_categories or not current_category.strip() or current_category == "Unsorted"
                else current_category
            )
            next_abstract = abstract if abstract or not current_abstract.strip() else current_abstract
            conn.execute(
                """
                UPDATE papers
                SET path = ?, title = ?, authors = ?, year = ?, abstract = ?, pages = ?,
                    category = ?, tags = ?, updated_at = ?
                WHERE filename = ?
                """,
                (
                    str(pdf),
                    title,
                    authors,
                    year,
                    next_abstract,
                    pages,
                    next_category,
                    next_tags,
                    now,
                    pdf.name,
                ),
            )
            updated += 1
        else:
            conn.execute(
                """
                INSERT INTO papers
                (filename, path, title, authors, year, abstract, pages, category, tags, added_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (pdf.name, str(pdf), title, authors, year, abstract, pages, category, tags, now, now),
            )
            inserted += 1

    conn.commit()
    conn.close()
    print(f"Scan complete: {len(pdfs)} PDFs, {inserted} new, {updated} updated.")
    print(f"Database: {DB_PATH}")


if __name__ == "__main__":
    scan()
