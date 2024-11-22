import streamlit as st
from byaldi import RAGMultiModalModel
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
import torch
from pdf2image import convert_from_path

# Set page config
st.set_page_config(page_title="Multi-Modal RAG Demo", layout="wide")

@st.cache_resource
def load_models():
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

def main():
    st.title("Multi-Modal RAG System")
    
    # Initialize session state
    if 'indexed' not in st.session_state:
        st.session_state.indexed = False
    
    # Load models
    rag_engine, model, processor = load_models()
    
    # File upload
    uploaded_file = st.file_uploader("Upload a PDF file", type=['pdf'])
    
    if uploaded_file is not None:
        # Index button
        if st.button("Index Document"):
            with st.spinner("Indexing document..."):
                # Save uploaded file temporarily
                with open("temp.pdf", "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                # Index the document
                rag_engine.index(
                    input_path="temp.pdf",
                    index_name="index",
                    store_collection_with_index=False,
                    overwrite=True
                )
                st.session_state.indexed = True
                st.success("Document indexed successfully!")
        
        # Query section
        if st.session_state.indexed:
            query = st.text_input("Enter your query:")
            
            if query:
                with st.spinner("Processing query..."):
                    # Get RAG results
                    results = rag_engine.search(query, k=3)
                    
                    # Convert PDF to images
                    images = convert_from_path("temp.pdf")
                    image_index = results[0]["page_num"] - 1
                    
                    # Prepare messages for model
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
                    
                    # Process with Qwen model
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
                    
                    # Generate response
                    generated_ids = model.generate(**inputs, max_new_tokens=50)
                    generated_ids_trimmed = [
                        out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
                    ]
                    output_text = processor.batch_decode(
                        generated_ids_trimmed, 
                        skip_special_tokens=True, 
                        clean_up_tokenization_spaces=False
                    )
                    
                    # Display results
                    st.subheader("Results")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.image(images[image_index], caption=f"Page {image_index + 1}")
                    
                    with col2:
                        st.write("Model Response:")
                        st.write(output_text[0])
                        
                        st.write("RAG Context:")
                        for idx, result in enumerate(results):
                            st.write(f"Result {idx + 1}:")
                            st.write(result["content"])
                            st.write(f"Page: {result['page_num']}")
                            st.write("---")

if __name__ == "__main__":
    main()