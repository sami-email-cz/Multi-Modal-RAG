# Multi-Modal RAG System

A powerful multi-modal RAG (Retrieval-Augmented Generation) system built with Streamlit, allowing users to upload multiple PDF documents and query them using natural language. The system combines advanced RAG capabilities with visual understanding through the Qwen-VL model.

## 🌟 Features

- **Multiple PDF Support**: Upload and manage multiple PDF documents simultaneously
- **Interactive UI**: Modern, intuitive interface with sidebar navigation
- **Visual Understanding**: Leverages Qwen-VL model for image-aware responses
- **Smart Search**: RAG-powered search across all uploaded documents
- **Context Visualization**: View relevant PDF pages alongside model responses
- **Document Management**: Easy document upload, indexing, and deletion

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- CUDA-compatible GPU (for optimal performance)
- Poppler (for PDF processing)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/imanoop7/Multi-Modal-RAG.git
cd Multi-Model-RAG

2. Install Poppler:
Windows: Download from http://blog.alivate.com.au/poppler-windows/
Linux:sudo apt-get install -y poppler-utils
Mac: brew install poppler

3. Install Python dependencies:
pip install -r requirements.txt

4. Run the app:
streamlit run app.py

5. Access the app at http://localhost:8501

## 📖 Usage
1.Upload Documents:
- Click on "Upload PDFs" in the sidebar
- Drag and drop or select PDF files
- Wait for the indexing process to complete
2. Query Documents:
- Navigate to "Query Documents" in the sidebar
- Enter your question in the text input
- View results with relevant page images and model responses
- Explore additional context in the Context tab

## 🛠️ Technical Details
The system uses:

- Byaldi: For RAG capabilities and document indexing
- Qwen-VL: For visual language understanding
- Streamlit: For the web interface
- PyTorch: For deep learning operations
- PDF2Image: For PDF processing

## 📝 Notes
- First-time model loading may take a few minutes
- GPU is recommended for optimal performance
- Ensure sufficient disk space for PDF storage and indexing
## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.