# PDF to JSON Schema: Enterprise Extraction Pipeline

This project extracts structured data from digital invoice PDFs and converts it into clean JSON schemas for automation and analysis.

What started as a simple text extractor has been upgraded into an **Enterprise-Grade Ingestion Pipeline**. It acts as a secure gatekeeper, actively defending the server against common file vulnerabilities (corruption, encryption, memory leaks) while intelligently preserving complex table layouts.

## 🌟 Features & Enterprise Defenses

* **Resource Exhaustion Protection (DoS):** Hardcoded page limits to prevent "PDF Bombs" from spiking server RAM.
* **Security & Integrity Checks:** Detects corrupted files and password-protected/encrypted PDFs upfront to prevent infinite pipeline hangs.
* **Memory-Safe Execution:** Wraps all C-binding PyMuPDF operations in Python context managers to guarantee memory release, even during fatal errors.
* **Dynamic Geometry Routing:** Mathematically calculates text vs. image areas to gracefully reject scanned images (e.g., JPGs disguised as PDFs) and skips blank cover pages.
* **Structural DOM Probing:** Probes the document's vector graphics to detect "Invisible Tables" (tables built with whitespace instead of lines) upstream.

## 🏗️ Pipeline Architecture

The pipeline uses a two-step modular approach to ensure data normalization and easy debugging:

1. **The Extractor (`detector.py`):** Validates the PDF and extracts the text.
   * **Track A:** Uses `pymupdf4llm` for lightning-fast extraction of standard digital PDFs.
   * **Track B:** Uses `pdfplumber` as a fallback to natively reconstruct borderless/whitespace tables.
   * *Both tracks normalize the output into standard Markdown tables (.txt).*
2. **The Parser (`parser_json.py`):** Scans the normalized Markdown file, identifies the primary line-items table, maps the values to headers, and exports a structured `.json` array.

## 📋 Prerequisites & Installation

Ensure your system has **Python 3.8+** installed. It is highly recommended to use a virtual environment.

Install the required extraction and parsing libraries:
```bash
pip install pymupdf4llm PyMuPDF pdfplumber

## Usage

1. Install dependencies (recommended: use a virtual environment):
   ```
   pip install pymupdf
   ```

2. Run the detector script:
   ```
   python pipeline/detector.py --pdf input/your_invoice.pdf --debug
   ```
   - `--pdf`: Path to the PDF file to process
   - `--debug`: (Optional) Enable debug output

3. Output will be saved in the `output/` directory with the same name as the PDF file.

```
PDF_to_JSON_Schema/
├── input/                # Place your PDF files here
│   ├── digital_invoice_test.pdf
│   └── dummy.pdf
├── output/               # Extracted Markdown and final JSON files are saved here
├── pipeline/
│   ├── detector.py       # Main enterprise script for PDF extraction
│   └── parser_json.py    # Script to convert Markdown tables to JSON
└── README.md
```

- `input/`: Folder for input PDF files.
- `output/`: Folder for extracted text files (created by the script).
- `pipeline/`: Contains the main extraction script and output subfolder.

## Example
See `pipeline/output/digital_invoice_test.txt` for a sample output.

## License
Einatec License

## Author
Einatec Team

## 🛠️ Usage

### Step 1: Extract PDF to Markdown
Run the detector script to validate the PDF and extract layout-aware text.
```bash
python pipeline/detector.py --pdf input/digital_invoice_test.pdf --debug
```

### Step 2: Parse Markdown to JSON
Pass the resulting text file into the parser to generate the final JSON schema.
```bash
python pipeline/parser_json.py --input output/digital_invoice_test.txt --debug
```

*Output files will be saved in the `output/` directory with the same base name as the PDF file.*

## 📂 Project Structure

```text
PDF_to_JSON_Schema/
├── input/                # Place your PDF files here
│   ├── digital_invoice_test.pdf
│   └── dummy.pdf
├── output/               # Extracted Markdown and final JSON files are saved here
├── pipeline/
│   ├── detector.py       # Main enterprise script for PDF extraction
│   └── parser_json.py    # Script to convert Markdown tables to JSON
└── README.md
```

## ⚠️ Scope & Off-Ramps
This specific pipeline is strictly optimized for Native Digital PDFs. If the detector.py script identifies a scanned document (image-based PDF), it will safely reject the file. Scanned documents should be routed to a dedicated OCR or AI Vision pipeline.
## 📄 License
Einatec License

## ✍️ Author
Einatec Team / Rohit
```

***

This version perfectly bridges the gap between your original vision and the highly advanced backend system you just built. 

Once you get this committed and pushed, would you like to run a full end-to-end test of a PDF through both scripts to see the final JSON output?

