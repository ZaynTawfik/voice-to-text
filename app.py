import streamlit as st
import whisper
import tempfile
import os

st.title("Audio to Text Transcription with Whisper")
    
# File uploader
#audio_file = st.file_uploader("Upload Audio", type=["wav", "mp3", "m4a", "ogg", "flac"])
audio_file = st_audiorec()

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
                    
                # Clean up temporary file
                os.unlink(tmp_path)
                    
                # Display results
                st.success("Transcription Complete")
                st.subheader("Transcribed Text:")
                st.write(result["text"])
                  
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
