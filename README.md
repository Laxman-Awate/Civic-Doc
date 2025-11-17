# CivicDoc: AI-Powered Public Issue Prioritization & Governance Automation System

## Project Overview

CivicDoc is an AI-driven platform designed to automate civic complaint handling and government paperwork creation. It aims to streamline the process of managing thousands of daily civic complaints (e.g., sewage leaks, potholes, garbage overflow) by classifying issues, detecting urgency, assigning priority, and routing them to the correct departments. Additionally, it can process uploaded PDFs or circulars to extract key rules and generate official documents like RTI drafts, scheme applications, legal notices, and internal work orders.

## Key Features

*   **Automatic Issue Categorization:** Classifies citizen complaints into predefined categories (sewage, garbage, water, roads, electricity, pollution, safety).
*   **Urgency Detection & Priority Score (0–100):** Assigns a priority score to each complaint based on its urgency.
*   **Smart Routing:** Automatically routes complaints to the relevant department (PWD, Sanitation, Water Board, Electricity Dept, etc.).
*   **Circular/PDF Understanding:** Extracts rules, eligibility criteria, and deadlines from uploaded circulars and PDFs using OCR and NLP.
*   **RTI, Scheme Application, Notice & Work Order Generation:** Generates government-ready documents instantly using Jinja2 templates.
*   **Multilingual Support:** Provides multilingual summaries and outputs in Hindi, English, Kannada, Marathi, Tamil, Telugu.
*   **Cost & Resource Estimation:** Suggests cost estimations and required resources for civic repair tasks.
*   **Field Officer Action Steps:** Recommends tools, safety notes, and Service Level Agreements (SLA) for field officers.
*   **Citizen Status Tracking:** Allows users to track the status of their submitted complaints.

## Technology Stack

*   **Frontend:** HTML, CSS, JavaScript
*   **Backend:** FastAPI (Python)
*   **AI & NLP:** Scikit-learn (TF-IDF + XGBoost), SpaCy, NLTK
*   **OCR & PDF Handling:** Tesseract OCR, PyMuPDF
*   **Database:** SQLite
*   **Document Generation:** Jinja2 Templates
*   **Deployment:** Hugging Face Spaces

## Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/Civic-Doc.git
    cd Civic-Doc
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Database Setup (SQLite):**
    No separate database server is required for SQLite. A database file named `sql_app.db` will be automatically created in your project's root directory when the application runs for the first time.

4.  **Initialize the Database Tables (Run ONCE):**
    Before running the application for the first time, you need to create the database tables. To do this, temporarily add the following lines to the very beginning of your `app/main.py` file (just after imports):
    ```python
    from .db import init_db
    init_db()
    ```
    Then, run `uvicorn app.main:app` once. You should see messages in your terminal indicating table creation. After this, **remove or comment out** these two lines from `app/main.py`.

5.  **Tesseract OCR:**
    Install Tesseract OCR on your system. Refer to the official Tesseract documentation for installation instructions specific to your OS.

6.  **Run the application locally:**
    ```bash
    uvicorn app.main:app --reload
    ```
    The frontend will be accessible at `http://localhost:8000`.

## Deployment on Hugging Face Spaces

To deploy this application on Hugging Face Spaces, follow these steps:

1.  **Create a new Space:** Go to [Hugging Face Spaces](https://huggingface.co/spaces) and create a new Space. You can choose a Python environment (like `Gradio`) if you're primarily using FastAPI for the backend, or a custom Docker environment for more control.

2.  **Upload Files:** Upload all project files to your Hugging Face Space repository. Ensure your `requirements.txt` is up-to-date with all necessary Python packages.

3.  **App File:** Ensure that `app.py` at the root level correctly imports and launches your FastAPI application. For example:
    ```python
    from app.main import app
    ```

4.  **Database on Hugging Face Spaces (SQLite):**
    For deployment on Hugging Face Spaces, the SQLite database file (`sql_app.db`) will be created within the Space's persistent storage. The `init_db()` call (which you temporarily added for local setup) will ensure tables are created on the first run of the Space.

5.  **Tesseract OCR Installation (if using Docker environment):**
    If you choose a custom Docker environment (e.g., using a `Dockerfile`), you will need to include instructions to install Tesseract OCR and any necessary language packs. A basic `Dockerfile` example would include:

    ```Dockerfile
    FROM python:3.9-slim

    WORKDIR /app

    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    # Install tesseract-ocr and its language packs (example for English)
    RUN apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-eng && \
        rm -rf /var/lib/apt/lists/*

    COPY . .

    CMD exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
    ```
    You would save this as `Dockerfile` in the root of your project.

6.  **Environment Variables:** If you have any other environment variables, configure them in the Space settings on Hugging Face.

After setting up, Hugging Face Spaces will build and deploy your application. You can monitor the build logs on your Space page.
