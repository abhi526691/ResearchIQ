
# ResearchIQ

ResearchIQ is a cutting-edge Retrieval-Augmented Generation (RAG) application designed to assist users in extracting meaningful insights from documents through Question Answering (QnA) and Summarization features. It leverages a robust tech stack and state-of-the-art models to ensure accurate and efficient results.



https://github.com/user-attachments/assets/e4e7bca1-4679-4819-803a-0648737352f3


## Features

### 1. Document Processing
Users can upload documents, and the application processes the document to extract headings and content using Adobe PDF Services. Key-value pairs (Heading: Content) are created after preprocessing.

#### Preprocessing Steps:
- Handle Emojis, Slangs, Punctuations, and ShortForms
- Spelling Corrections
- Part-of-Speech (POS) Tagging
- Handling Pronouns and Special Characters
- Tokenization
- Convert text to lowercase and generate n-grams
- Remove Special Characters
- Remove Extra Whitespaces

### 2. Question Answering (QnA)
Users can ask questions about the uploaded document. The process includes:
- Converting the question into embeddings using Sentence Transformer.
- Fetching relevant content from the document using ChromaDB and cosine similarity.
- Using the Groq (Llama-70b) model to generate precise answers based on the top 5 matching data points.

### 3. Summarization
- **Title-wise Summarization:** Generate summaries for specific headings extracted from the document.
- **Whole Document Summarization:** Summarize the entire document. For large documents, content is split into 6000-token segments (approx. 24,000 words per call) due to the Groq model's max token limit.


## Tech Stack
- **Backend:** Django or FastAPI(For Speed)
- **Frontend:** Streamlit
- **Vector Database:** ChromaDB
- **Language Model:** Groq (Llama-70b)
- **Embedding Creation:** Sentence Transformer
- **Document Processing:** Adobe PDF Services
- **Containerization:** Docker
- **Hashing:** `hashlib` (to avoid redundant API calls for duplicate documents)

## Endpoints
| Endpoint | Description |
|----------|-------------|
| `EXTRACTOR_API_URL` | Uploads and processes documents to extract headings and content. |
| `QNA_API_URL` | Handles user questions and returns answers using RAG. |
| `SUMMARIZER_API_URL` | Summarizes the entire document. |
| `SUMMARIZER_API_HEADING_URL` | Summarizes content under specific headings. |
| `SUMMARIZER_API_TITLE_URL` | Summarizes specific titles from the document. |

## .env file
- populate your env file as given in the sample

## Getting Started

### Prerequisites
1. **Groq API Key:** [Get your API key here](https://console.groq.com/keys).
2. **Adobe PDF Services Credentials:** [Generate credentials here](https://acrobatservices.adobe.com/dc-integration-creation-app-cdn/main.html?api=pdf-services-api).

### Implementation Resources
- [Adobe PDF Services API Documentation](https://developer.adobe.com/document-services/docs/overview/pdf-services-api/)

### Installation
1. Clone the repository:

   ```bash
   git clone [https://github.com/abhi526691/promptEngineering](https://github.com/abhi526691/ResearchIQ)
   cd ResearchIQ
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Set up a virtual environment:

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: .\env\Scripts\activate
   ```
   
#### Option 1: Run with Docker
1. Clone the repository.
2. Build and run the Docker container:
   ```bash
   docker-compose up --build
   ```

#### Option 2: Run Backend and Frontend Separately
1. **Backend (Django):**
   ```bash
   cd backend
   python manage.py runserver
   ```

2. **Frontend (Streamlit):**
   ```bash
   cd frontend
   streamlit run app.py
   ```

### Text Extraction Options
While Adobe PDF Services is the primary extraction tool, the following alternatives are also available:
- AWS Textract
- Azure Form Recognizer
- PyMuPDF
- PyPDF

## Usage
1. **Upload a Document:**
   - The document is processed, and key-value pairs (Heading: Content) are extracted.
   - Preprocessing ensures clean and structured data.
2. **Ask Questions:**
   - Use the QnA feature to get precise answers to your queries.
3. **Generate Summaries:**
   - Choose between Heading-wise or Whole Document summarization.


## Contributions
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License.
