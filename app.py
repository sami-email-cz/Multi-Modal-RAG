import streamlit as st
import os
from byaldi import RAGMultiModalModel
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
import torch
from pdf2image import convert_from_path
from streamlit_option_menu import option_menu
import shutil
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Multi-Modal RAG System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .uploadedFile {
        border: 2px solid #f0f2f6;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
    .stProgress > div > div > div > div {
        background-color: #00a0dc;
    }
    </style>
""", unsafe_allow_html=True)

# Create necessary directories
UPLOAD_DIR = "uploaded_pdfs"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@st.cache_resource
def load_models():
    with st.spinner("Loading models... This might take a few minutes."):
        # Load RAG engine
        rag_engine = RAGMultiModalModel.from_pretrained("vidore/colpali")
        
        # Load Qwen model
        model = Qwen2VLForConditionalGeneration.from_pretrained(
            "Qwen/Qwen2-VL-7B-Instruct",
            torch_dtype=torch.float16,
            device_map="cuda"
        )
        
        # Load processor
        processor = AutoProcessor.from_pretrained(
            "Qwen/Qwen2-VL-7B-Instruct", 
            trust_remote_code=True
        )
        
        return rag_engine, model, processor

def save_uploaded_file(uploaded_file):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{uploaded_file.name}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    return file_path

def get_pdf_list():
    if not os.path.exists(UPLOAD_DIR):
        return []
    return [f for f in os.listdir(UPLOAD_DIR) if f.endswith('.pdf')]

def main():
    # Initialize session states
    if 'indexed_files' not in st.session_state:
        st.session_state.indexed_files = set()
    if 'current_pdf' not in st.session_state:
        st.session_state.current_pdf = None
    
    # Sidebar
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/your-repo/your-logo.png", width=100)  # Replace with your logo
        st.title("Navigation")
        
        selected = option_menu(
            menu_title=None,
            options=["Upload PDFs", "Query Documents"],
            icons=["cloud-upload", "search"],
            default_index=0,
        )
    
    # Load models
    rag_engine, model, processor = load_models()
    
    if selected == "Upload PDFs":
        st.title("📚 PDF Document Upload")
        
        # Multiple file upload
        uploaded_files = st.file_uploader(
            "Upload your PDF documents",
            type=['pdf'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                if uploaded_file.name not in [os.path.basename(f) for f in st.session_state.indexed_files]:
                    with st.spinner(f"Processing {uploaded_file.name}..."):
                        # Save file
                        file_path = save_uploaded_file(uploaded_file)
                        
                        # Index document
                        try:
                            rag_engine.index(
                                input_path=file_path,
                                index_name=os.path.basename(file_path),
                                store_collection_with_index=True,
                                overwrite=True
                            )
                            st.session_state.indexed_files.add(file_path)
                            st.success(f"Successfully processed {uploaded_file.name}")
                        except Exception as e:
                            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
        
        # Display uploaded files
        st.subheader("Uploaded Documents")
        if st.session_state.indexed_files:
            for file_path in st.session_state.indexed_files:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"📄 {os.path.basename(file_path)}")
                with col2:
                    if st.button("Delete", key=file_path):
                        os.remove(file_path)
                        st.session_state.indexed_files.remove(file_path)
                        st.experimental_rerun()
        else:
            st.info("No documents uploaded yet.")
            
    elif selected == "Query Documents":
        st.title("🔍 Query Documents")
        
        if not st.session_state.indexed_files:
            st.warning("Please upload and index some documents first!")
            return
        
        # Query input
        query = st.text_input("Enter your query:", placeholder="What would you like to know?")
        
        if query:
            with st.spinner("Processing query..."):
                try:
                    # Get RAG results from all indexed documents
                    all_results = []
                    for file_path in st.session_state.indexed_files:
                        results = rag_engine.search(
                            query,
                            k=3,
                            index_name=os.path.basename(file_path)
                        )
                        all_results.extend([(file_path, r) for r in results])
                    
                    # Sort results by relevance
                    all_results.sort(key=lambda x: x[1].get('score', 0), reverse=True)
                    
                    # Process top result with Qwen
                    if all_results:
                        top_file, top_result = all_results[0]
                        images = convert_from_path(top_file)
                        image_index = top_result["page_num"] - 1
                        
                        # Display results in tabs
                        tab1, tab2 = st.tabs(["📊 Results", "📑 Context"])
                        
                        with tab1:
                            col1, col2 = st.columns([1, 1])
                            
                            with col1:
                                st.image(
                                    images[image_index],
                                    caption=f"Page {image_index + 1} from {os.path.basename(top_file)}",
                                    use_column_width=True
                                )
                            
                            with col2:
                                # Process with Qwen model
                                messages = [
                                    {
                                        "role": "user",
                                        "content": [
                                            {
                                                "type": "image",
                                                "image": images[image_index],
                                            },
                                            {"type": "text", "text": query},
                                        ],
                                    }
                                ]
                                
                                text = processor.apply_chat_template(
                                    messages, tokenize=False, add_generation_prompt=True
                                )
                                
                                image_inputs, video_inputs = process_vision_info(messages)
                                inputs = processor(
                                    text=[text],
                                    images=image_inputs,
                                    videos=video_inputs,
                                    padding=True,
                                    return_tensors="pt",
                                )
                                inputs = inputs.to("cuda")
                                
                                generated_ids = model.generate(**inputs, max_new_tokens=50)
                                generated_ids_trimmed = [
                                    out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
                                ]
                                output_text = processor.batch_decode(
                                    generated_ids_trimmed,
                                    skip_special_tokens=True,
                                    clean_up_tokenization_spaces=False
                                )
                                
                                st.markdown("### Model Response")
                                st.write(output_text[0])
                        
                        with tab2:
                            for file_path, result in all_results[:5]:  # Show top 5 results
                                with st.expander(f"From: {os.path.basename(file_path)} - Page {result['page_num']}"):
                                    st.write(result["content"])
                                    st.caption(f"Relevance Score: {result.get('score', 0):.2f}")
                
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()