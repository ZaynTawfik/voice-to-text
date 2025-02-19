import streamlit as st
import whisper
import tempfile
import os
from st_audiorec import st_audiorec
import pytesseract
from PIL import Image

st.title("Audio to Text Transcription with Whisper")
    
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
                transcript = result["text"]
                    
                # Clean up temporary file
                os.unlink(tmp_path)
                    
                # Display results
                st.success("Transcription Complete")
                st.subheader("Transcribed Text:")
                st.write(transcript)
                  
                # Add download button
                st.download_button(
                    label="Download Transcription",
                    data=result["text"],
                    file_name="transcription.txt",
                    mime="text/plain"
                )
                    
            except Exception as e:
                st.error(f"Error processing audio: {str(e)}")
                os.unlink(tmp_path)

# Detect intent from transcript
if 'transcript' in locals():
    intent = None
    if "hello" in transcript.lower():
        intent = "passport"
    elif "invoice" in transcript.lower():
        intent = "invoice"

    if intent:
        st.session_state.intent = intent
        st.write(f"**Action needed:** Upload your {intent}!")
    else:
        st.error("Could not detect document type. Please try again.")

if 'intent' in st.session_state:
    uploaded_file = st.file_uploader(
        f"Upload your {st.session_state.intent}",
        type=["pdf", "jpg", "png"]
    )

    if uploaded_file:
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            img_path = tmp_file.name

        # Simple validation using OCR (for images)
        if uploaded_file.type.startswith("image"):
            text = pytesseract.image_to_string(Image.open(img_path))
            if st.session_state.intent in text.lower():
                st.success("✅ Valid document uploaded!")
            else:
                st.error("❌ Document does not match the request.")
    
        os.unlink(img_path)  # Delete temp file
