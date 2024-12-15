#TEXT EXTRACTION
from langchain_community.document_loaders import PyMuPDFLoader

# Define the path to the PDF file
pdf_path = "E:/Projects_Langchain/Group_projects/Podcast_Generator/test.pdf"

# Load and extract text from the PDF
loader = PyMuPDFLoader(pdf_path)
documents = loader.load()

# Combine text from all pages into a single string
extracted_text = " ".join([doc.page_content for doc in documents])

# Check if extracted_text is empty
if not extracted_text.strip():
    print("Warning: The extracted text is empty. Please check the PDF content.")
else:
    # Save the extracted text to a file with UTF-8 encoding
    output_path = "E:/Projects_Langchain/Group_projects/Podcast_Generator/extracted_text.txt"
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(extracted_text)

    print("Text extraction completed and saved to extracted_text.txt")

#CLEAN TEXT
import re

# Define the path to the extracted text file
extracted_text_path = "E:/Projects_Langchain/Group_projects/Podcast_Generator/extracted_text.txt"

# Read the extracted text
with open(extracted_text_path, "r", encoding="utf-8") as file:
    extracted_text = file.read()

# Function to clean the text
def clean_text(text):
    # Remove unwanted characters and normalize spaces
    text = re.sub(r'\s+', ' ', text)  # Remove multiple spaces
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters

    # Specific unwanted characters and symbols removal
    text = text.replace('', ' ')
    text = text.replace('', ' ')
    text = text.replace('', ' ')
    text = text.replace('“', '"').replace('”', '"')
    text = text.replace('‘', "'").replace('’', "'")

    # Replace placeholders and decode symbols
    text = text.replace("•", "-").replace("€", "EUR")
    text = text.replace("±", "+/-")
    text = text.replace("�", "'")

    # Fix common OCR errors (optional)
    text = text.replace('ﬁ', 'fi').replace('ﬂ', 'fl')
    text = text.replace('œ', 'oe').replace('æ', 'ae')

    # Normalize spacing
    text = re.sub(r'\s+', ' ', text)

    return text

# Clean the extracted text
cleaned_text = clean_text(extracted_text)

# Save the cleaned text to a new file
cleaned_text_path = "E:/Projects_Langchain/Group_projects/Podcast_Generator/cleaned_text.txt"
with open(cleaned_text_path, "w", encoding="utf-8") as file:
    file.write(cleaned_text)

print("Text cleaning completed and saved to cleaned_text.txt")


#SUMMARIZE TEXT
from transformers import pipeline

# Define the path to the cleaned text file
cleaned_text_path = "E:/Projects_Langchain/Group_projects/Podcast_Generator/cleaned_text.txt"

# Read the cleaned text
with open(cleaned_text_path, "r", encoding="utf-8") as file:
    cleaned_text = file.read()

# Initialize the summarization pipeline
summarizer = pipeline("summarization",model="sshleifer/distilbart-cnn-6-6")

# Summarize the cleaned text
# Since the text might be long, split it into manageable chunks and summarize each chunk
max_chunk_size = 1000  # Define the maximum chunk size for summarization
chunks = [cleaned_text[i:i + max_chunk_size] for i in range(0, len(cleaned_text), max_chunk_size)]
summaries = [summarizer(chunk, max_length=150, min_length=30, do_sample=False)[0]['summary_text'] for chunk in chunks]

# Combine the summaries into a single string
summary_text = " ".join(summaries)

# Save the summary to a new file
summary_path = "E:/Projects_Langchain/Group_projects/Podcast_Generator/summaries.txt"
with open(summary_path, "w", encoding="utf-8") as file:
    file.write(summary_text)

print("Summarization completed and saved to summaries.txt")


#GENERATE SCRIPT
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

# Define your API key and model name
groq_api_key = os.getenv("GROQ_API_KEY")
model_name = "Llama3-70b-8192"

# Initialize the ChatGroq model
llm = ChatGroq(groq_api_key=groq_api_key, model_name=model_name)

# Define the path to the summary text file
summary_path = "E:/Projects_Langchain/Group_projects/Podcast_Generator/summaries.txt"

# Read the summary text
with open(summary_path, "r", encoding="utf-8") as file:
    summary_text = file.read()

# Craft a precise and detailed prompt
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

# Generate the script using ChatGroq
response = llm.invoke(prompt)
generated_script = response.content  # Access the content attribute

# Save the script to a new file
script_path = "E:/Projects_Langchain/Group_projects/Podcast_Generator/script.txt"
with open(script_path, "w", encoding="utf-8") as file:
    file.write(generated_script)

print("Script generation completed and saved to script.txt")


#CONVERT TO AUDIO
import os
import re
from google.cloud import texttospeech
from pydub import AudioSegment

# Set the path to the service account key file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "E:/Projects_Langchain/PREMIUM_KEYS_DONT_SHARE/gctts_private_key.json"

# Ensure the audio_files directory exists
os.makedirs("E:/Projects_Langchain/Group_projects/Podcast_Generator/audio_files", exist_ok=True)

# Initialize Google Cloud Text-to-Speech client
client = texttospeech.TextToSpeechClient()

# Define the path to the generated script
script_path = "E:/Projects_Langchain/Group_projects/Podcast_Generator/script.txt"

# Read the generated script
with open(script_path, "r", encoding="utf-8") as file:
    script = file.read()

# Split the script by speakers
dialogues = script.split("\n")
audio_files = []

# Function to clean text
def clean_text(text):
    # Remove Markdown formatting (e.g., asterisks for bold text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    # Remove speaker labels
    text = re.sub(r"Speaker [A-B]:", "", text)
    return text.strip()

def synthesize_speech(text, voice_name, output_file):
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name=voice_name,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    with open(output_file, "wb") as out:
        out.write(response.audio_content)

# Convert each dialogue to speech and save as an audio file
for i, dialogue in enumerate(dialogues):
    if "Speaker A:" in dialogue:
        text = clean_text(dialogue)
        audio_file = f"E:/Projects_Langchain/Group_projects/Podcast_Generator/audio_files/speaker_a_{i}.mp3"
        synthesize_speech(text, "en-US-Wavenet-D", audio_file)  # Change to desired voice
        audio_files.append(audio_file)
    elif "Speaker B:" in dialogue:
        text = clean_text(dialogue)
        audio_file = f"E:/Projects_Langchain/Group_projects/Podcast_Generator/audio_files/speaker_b_{i}.mp3"
        synthesize_speech(text, "en-US-Wavenet-F", audio_file)  # Change to desired voice
        audio_files.append(audio_file)

print("Text-to-speech conversion completed and saved to audio_files/")


#COMBINE AUDIO
from pydub import AudioSegment
import os

# Define the directory containing the audio files
audio_files_dir = "E:/Projects_Langchain/Group_projects/Podcast_Generator/audio_files"
script_path = "E:/Projects_Langchain/Group_projects/Podcast_Generator/script.txt"

# Read the generated script
with open(script_path, "r", encoding="utf-8") as file:
    script = file.read()

# Split the script by lines
lines = script.split("\n")

# Initialize an empty AudioSegment
combined = AudioSegment.empty()

# Function to determine speaker and file index
def get_file_name_and_index(line, speaker_a_count, speaker_b_count):
    if "Speaker A:" in line:
        file_name = f"speaker_a_{speaker_a_count}.mp3"
        speaker_a_count += 4 #You need to set your increment based on the naming condition of your individual generated audios
    elif "Speaker B:" in line:
        file_name = f"speaker_b_{speaker_b_count}.mp3"
        speaker_b_count += 4 #You need to set your increment based on the naming condition of your individual generated audios
    else:
        return None, speaker_a_count, speaker_b_count
    return file_name, speaker_a_count, speaker_b_count

# Counters for speaker A and B
speaker_a_count = 2 #Based on audio naming convention
speaker_b_count = 4 #Based on audio naming convention 

# Combine audio files based on script order
for line in lines:
    file_name, speaker_a_count, speaker_b_count = get_file_name_and_index(line, speaker_a_count, speaker_b_count)
    if file_name:
        file_path = os.path.join(audio_files_dir, file_name)
        if os.path.exists(file_path):
            audio_segment = AudioSegment.from_mp3(file_path)
            combined += audio_segment
        else:
            print(f"File {file_path} not found!")

# Export the combined audio file
combined.export("E:/Projects_Langchain/Group_projects/Podcast_Generator/audio_files/combined_audio.mp3", format="mp3")

print("Audio files combined and saved as combined_audio.mp3")


#ENHANCE AUDIO 
from pydub import AudioSegment
import os

# Define the path to the combined audio file
combined_audio_path = "E:/Projects_Langchain/Group_projects/Podcast_Generator/audio_files/combined_audio.mp3"
enhanced_audio_path = "E:/Projects_Langchain/Group_projects/Podcast_Generator/audio_files/enhanced_audio.mp3"
background_music_path = "E:\Projects_Langchain\Group_projects\Podcast_Generator\podcast_bgm.mp3"

# Load the combined audio file
combined_audio = AudioSegment.from_mp3(combined_audio_path)

# Apply a low pass filter to reduce high-frequency noise
enhanced_audio = combined_audio.low_pass_filter(3000)

# Normalize the audio to ensure consistent volume levels
enhanced_audio = enhanced_audio.normalize()

# Add background music (optional)
background_music = AudioSegment.from_mp3(background_music_path).apply_gain(-20)  # Lower the volume of the background music
combined_with_music = enhanced_audio.overlay(background_music, loop=True)

# Export the enhanced audio file
combined_with_music.export(enhanced_audio_path, format="mp3")

print("Audio enhancement completed and saved as enhanced_audio.mp3")
