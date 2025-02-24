import streamlit as st
import whisper
import tempfile
import os
from st_audiorec import st_audiorec
import pytesseract
from PIL import Image

st.title("Document Collection AI Agent")

# Reset session
if st.button("Start Over"):
    st.session_state.clear()

# Instructions
st.markdown("---")
st.write("**How it works:**")
st.write("1. Upload a voice recording with your intent, 'I need to open an account or I need to upload my passport/id'.")
st.write("2. Upload the requested document.")

# Initialize session state
if 'transcript' not in st.session_state:
    st.session_state.transcript = None
if 'intent' not in st.session_state:
    st.session_state.intent = None
    
# File uploader
audio_file = st.file_uploader("Upload Audio", type=["wav", "mp3", "m4a", "ogg", "flac"])
#audio_file = st_audiorec()

if audio_file is not None:
    st.audio(audio_file, format='audio/wav')
        
    if st.button("Transcribe Audio"):
        with st.spinner("Processing audio..."):
            try:
                # Save uploaded file to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    tmp_file.write(audio_file.read())
                    tmp_path = tmp_file.name
                    
                # Load Whisper model (base model for faster processing)
                model = whisper.load_model("tiny")
                    
                # Transcribe audio
                result = model.transcribe(tmp_path)
                st.session_state.transcript = result["text"]    
                # Clean up temporary file
                os.unlink(tmp_path)
                    
                # Display results
                st.success("Transcription Complete")
                st.subheader("Transcribed Text:")
                st.write(st.session_state.transcript)
                              
            except Exception as e:
                st.error(f"Error processing audio: {str(e)}")
                os.unlink(tmp_path)

# Intent detection
if st.session_state.transcript:
    if "hello" in st.session_state.transcript.lower():
        st.session_state.intent = "passport"
    elif "invoice" in st.session_state.transcript.lower():
        st.session_state.intent = "invoice"
    else:
        st.session_state.intent = None


# Document upload (only shown if intent is detected)
if st.session_state.intent:
    uploaded_file = st.file_uploader(
        f"Upload your {st.session_state.intent}",
        type=["pdf", "jpg", "png"]
    )

    if uploaded_file is not None:
            try:
                # Open and display image
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)

                # Extract text
                extracted_text = pytesseract.image_to_string(image).lower()
            
                if extracted_text:
                    if st.session_state.intent in extracted_text.lower():
                        st.success("✅ Valid document!")
                    else:
                        st.error("❌ Invalid document")
                    # Show extracted text
                    st.subheader("Extracted Text:")
                    st.write(extracted_text)
                else:
                    st.warning("No text found in the document")
                
            except Exception as e:
                st.error(f"Error processing document: {str(e)}")
