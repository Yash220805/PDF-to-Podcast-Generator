from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from langchain_community.document_loaders import PyMuPDFLoader
from transformers import pipeline
from google.cloud import texttospeech
from pydub import AudioSegment
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Set the path for Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "E:/Projects_Langchain/PREMIUM_KEYS_DONT_SHARE/gctts_private_key.json"

# Initialize the FastAPI app
app = FastAPI()

# CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, modify for specific domains if needed
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Define file paths
BASE_DIR = "E:/Projects_Langchain/Group_projects/Podcast_Generator"
os.makedirs(BASE_DIR, exist_ok=True)
EXTRACTED_TEXT_PATH = os.path.join(BASE_DIR, "extracted_text.txt")
CLEANED_TEXT_PATH = os.path.join(BASE_DIR, "cleaned_text.txt")
SUMMARY_PATH = os.path.join(BASE_DIR, "summaries.txt")
SCRIPT_PATH = os.path.join(BASE_DIR, "script.txt")
AUDIO_DIR = os.path.join(BASE_DIR, "audio_files")
COMBINED_AUDIO_PATH = os.path.join(AUDIO_DIR, "combined_audio.mp3")
ENHANCED_AUDIO_PATH = os.path.join(AUDIO_DIR, "enhanced_audio.mp3")
os.makedirs(AUDIO_DIR, exist_ok=True)

# Function to clean text
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)  # Remove multiple spaces
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
    text = text.replace('', ' ').replace('', ' ')
    text = text.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
    text = text.replace("•", "-").replace("€", "EUR").replace("±", "+/-").replace("�", "'")
    text = text.replace('ﬁ', 'fi').replace('ﬂ', 'fl').replace('œ', 'oe').replace('æ', 'ae')
    text = re.sub(r'\s+', ' ', text)  # Normalize spacing again
    return text

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    pdf_path = os.path.join(BASE_DIR, file.filename)
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": "PDF uploaded successfully", "pdf_path": pdf_path}

@app.post("/extract-text/")
async def extract_text(pdf_path: str):
    try:
        if not pdf_path:
            raise HTTPException(status_code=400, detail="PDF path is required.")
        
        loader = PyMuPDFLoader(pdf_path)
        documents = loader.load()
        extracted_text = " ".join([doc.page_content for doc in documents])
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="The extracted text is empty. Check the PDF content.")
        
        with open(EXTRACTED_TEXT_PATH, "w", encoding="utf-8") as file:
            file.write(extracted_text)
        return {"message": "Text extracted successfully", "extracted_text": extracted_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clean-text/")
async def clean_extracted_text():
    try:
        with open(EXTRACTED_TEXT_PATH, "r", encoding="utf-8") as file:
            extracted_text = file.read()
        cleaned_text = clean_text(extracted_text)
        with open(CLEANED_TEXT_PATH, "w", encoding="utf-8") as file:
            file.write(cleaned_text)
        return {"message": "Text cleaned successfully", "cleaned_text": cleaned_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize-text/")
async def summarize_text():
    try:
        with open(CLEANED_TEXT_PATH, "r", encoding="utf-8") as file:
            cleaned_text = file.read()
        summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-6-6")
        chunks = [cleaned_text[i:i + 1000] for i in range(0, len(cleaned_text), 1000)]
        summaries = [summarizer(chunk, max_length=150, min_length=30, do_sample=False)[0]['summary_text'] for chunk in chunks]
        summary_text = " ".join(summaries)
        with open(SUMMARY_PATH, "w", encoding="utf-8") as file:
            file.write(summary_text)
        return {"message": "Text summarized successfully", "summary": summary_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-script/")
async def generate_script():
    try:
        from langchain_groq import ChatGroq
        groq_api_key = os.getenv("GROQ_API_KEY")
        model_name = "Llama3-70b-8192"
        llm = ChatGroq(groq_api_key=groq_api_key, model_name=model_name)
        with open(SUMMARY_PATH, "r", encoding="utf-8") as file:
            summary_text = file.read()
        prompt = (
            f"Create a podcast script where two speakers, Speaker A and Speaker B, discuss the following summary "
            f"of the topic that the summary is about. The speakers should alternate their dialogues, each providing "
            f"insights, questions, and thoughts based on the summary. Make the conversation engaging and informative."
            f"You have to ensure that dialogues are not repeated, make sense scientifically and logically, and have a natural flow imitating the flow of human conversations.\n\n"
            f"You also have to ensure that you do not mention explicitly that the summary mentions this or that. Just use the information from the summary without citing it in the dialogues."
            f"Summary:\n{summary_text}\n\n"
            f"Speaker A: Hello! I am here with my guest speaker B. What are your thoughts on this?\n"
            f"Speaker B: I think this is fascinating because...\n"
            f"Speaker A: That's an interesting point. How about...\n"
            f"Speaker B: Indeed, and another aspect to consider is...\n"
            f"Speaker A: It’s clear that...\n"
            f"Speaker B: Additionally, we should note that...\n"
            f"Speaker A: To sum up, it seems...\n"
        )
        response = llm.invoke(prompt)
        generated_script = response.content
        with open(SCRIPT_PATH, "w", encoding="utf-8") as file:
            file.write(generated_script)
        return {"message": "Script generated successfully", "script": generated_script}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert-to-audio/")
async def convert_to_audio():
    try:
        client = texttospeech.TextToSpeechClient()
        with open(SCRIPT_PATH, "r", encoding="utf-8") as file:
            script = file.read()
        dialogues = script.split("\n")
        audio_files = []
        for i, dialogue in enumerate(dialogues):
            if "Speaker A:" in dialogue:
                text = re.sub(r"Speaker A:", "", dialogue).strip()
                output_file = os.path.join(AUDIO_DIR, f"speaker_a_{i}.mp3")
                synthesize_speech(client, text, "en-US-Wavenet-D", output_file)
                audio_files.append(output_file)
            elif "Speaker B:" in dialogue:
                text = re.sub(r"Speaker B:", "", dialogue).strip()
                output_file = os.path.join(AUDIO_DIR, f"speaker_b_{i}.mp3")
                synthesize_speech(client, text, "en-US-Wavenet-F", output_file)
                audio_files.append(output_file)
        return {"message": "Audio files generated successfully", "audio_files": audio_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/combine-audio/")
async def combine_audio():
    try:
        # Define the directory containing the audio files
        audio_files_dir = AUDIO_DIR
        script_path = SCRIPT_PATH

        # Read the generated script
        with open(script_path, "r", encoding="utf-8") as file:
            script = file.read()

        # Clean up the script by removing unwanted characters (like '***')
        script = script.replace("***", "").strip()  # Remove '***' and any leading/trailing whitespace
        script = re.sub(r"\n{2,}", "\n", script)  # Remove extra new lines

        # Split the script by lines
        lines = script.split("\n")

        # Initialize an empty AudioSegment for combining audio
        combined = AudioSegment.empty()

        # Function to determine speaker and file index
        def get_file_name_and_index(line, speaker_a_count, speaker_b_count):
            if "Speaker A:" in line:
                file_name = f"speaker_a_{speaker_a_count}.mp3"
                speaker_a_count += 4  # Adjust based on your audio file naming convention
            elif "Speaker B:" in line:
                file_name = f"speaker_b_{speaker_b_count}.mp3"
                speaker_b_count += 4  # Adjust based on your audio file naming convention
            else:
                return None, speaker_a_count, speaker_b_count
            return file_name, speaker_a_count, speaker_b_count

        # Counters for speaker A and B
        speaker_a_count = 2  # Starting index for speaker A files (adjust based on naming convention)
        speaker_b_count = 4  # Starting index for speaker B files (adjust based on naming convention)

        # Combine audio files based on script order
        for line in lines:
            file_name, speaker_a_count, speaker_b_count = get_file_name_and_index(line, speaker_a_count, speaker_b_count)
            if file_name:
                file_path = os.path.join(audio_files_dir, file_name)
                if os.path.exists(file_path):
                    audio_segment = AudioSegment.from_mp3(file_path)
                    combined += audio_segment  # Add the audio to the combined track
                else:
                    print(f"File {file_path} not found!")

        # Export the combined audio file
        combined.export(COMBINED_AUDIO_PATH, format="mp3")
        print(f"Combined audio saved to {COMBINED_AUDIO_PATH}")  # Debugging output

        return {"message": "Audio files combined successfully", "combined_audio_path": COMBINED_AUDIO_PATH}

    except Exception as e:
        print(f"Error combining audio: {str(e)}")  # Log the error
        raise HTTPException(status_code=500, detail=f"Error combining audio: {str(e)}")



@app.post("/enhance-audio/")
async def enhance_audio():
    try:
        combined_audio = AudioSegment.from_mp3(COMBINED_AUDIO_PATH)
        background_music_path = os.path.join(BASE_DIR, "podcast_bgm.mp3")
        background_music = AudioSegment.from_mp3(background_music_path).apply_gain(-20)
        enhanced_audio = combined_audio.low_pass_filter(3000).normalize().overlay(background_music, loop=True)
        enhanced_audio.export(ENHANCED_AUDIO_PATH, format="mp3")
        return {"message": "Audio enhanced successfully", "enhanced_audio_path": ENHANCED_AUDIO_PATH}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def synthesize_speech(client, text, voice_name, output_file):
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(language_code="en-US", name=voice_name)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
    with open(output_file, "wb") as out:
        out.write(response.audio_content)
