Podcast Generator
=================

Podcast Generator is a web application that automates the process of generating podcast audio from PDF files. The application performs multiple tasks, including text extraction, text cleaning, summarization, script generation, audio synthesis, audio enhancement, and audio combination, delivering a final enhanced audio file as output.

This README will guide you through the setup process, usage, and key features of the project.

Table of Contents
-----------------

  [Project Overview](#project-overview)
    
  [Features](#features)
    
  [Technologies Used](#technologies-used)
    
  [Setup Instructions](#setup-instructions)
    
  [Usage](#usage)
    
  [API Endpoints](#api-endpoints)
    
  [Troubleshooting](#troubleshooting)
    
  [Future Improvements](#future-improvements)
    
  [Contributing](#contributing)
    

    

Project Overview
----------------

Podcast Generator simplifies the process of converting textual content in PDFs into professional-quality podcast audio files. The application takes an uploaded PDF, processes it step by step (text extraction, cleaning, summarization, script generation, and audio synthesis), and combines audio segments into a polished podcast.

The result is an **enhanced audio file** ready for playback.

Features
--------

*   **Upload PDF**: Upload a PDF file for podcast generation.
    
*   **Text Processing**:
    
    *   Extracts text from the PDF.
        
    *   Cleans and summarizes the extracted text.
        
*   **Script Generation**:
    
    *   Creates dialogue-style scripts for a podcast.
        
    *   Assigns roles to speakers dynamically.
        
*   **Audio Synthesis**:
    
    *   Converts script text into individual audio files using TTS (Text-to-Speech) engines.
        
*   **Audio Combination**:
    
    *   Combines the audio files based on the dialogue sequence.
        
*   **Audio Enhancement**:
    
    *   Enhances the quality of the combined audio file.
        
*   **Playback**:
    
    *   Allows the user to listen to the final enhanced podcast audio.
        

Technologies Used
-----------------

### Frontend:

*   **HTML5**: Structure of the webpage.
    
*   **CSS3**: Styling and layout of the web application.
    
*   **JavaScript**: Interactivity, API calls, and dynamic updates.
    

### Backend:

*   **FastAPI**: Backend framework to manage API endpoints.
    
*   **Pydub**: For audio manipulation and combining audio files.
    
*   **PyPDF2**: For text extraction from PDFs.
    
*   **NLTK (Natural Language Toolkit)**: For text cleaning and summarization.
    
*   **gTTS**: Text-to-speech conversion for script audio generation.
    


Setup Instructions
------------------

Follow these steps to set up the project locally:

### 1\. Prerequisites

*   Python 3.9 or later
    
*   Node.js and npm (optional if modifying frontend files)
    
*   Pip (Python package manager)
    

### 2\. Clone the Repository

     bashCopy codegit clone https://github.com/your-username/Podcast-Generator.git  cd Podcast-Generator   `

### 3\. Install Backend Dependencies

Navigate to the backend/ folder:

     bashCopy codecd backend  pip install -r requirements.txt   `

### 4\. Start the FastAPI Backend (main.py)

Run the FastAPI application:

     bashCopy codeuvicorn main:app --reload   `

The backend will run on http://127.0.0.1:8000.

### 5\. Serve the Frontend

Simply open the main.html file in your browser, or host it using a web server.

Usage
-----

1.  Open the application in your web browser by navigating to the index.html file or the hosted address.
    
2.  **Upload PDF**:
    
    *   Select a PDF file from your system and click "Upload PDF."
        
3.  **Processing**:
    
    *   The backend will process the file step-by-step.
        
    *   Follow the progress as each step completes.
        
4.  **Playback**:
    
    *   Once processing is complete, the final enhanced audio will be available for playback.
        

API Endpoints
-------------

The backend exposes several API endpoints:

**EndpointMethodDescription**/upload-pdf/POSTUploads the PDF file./extract-text/POSTExtracts text from the uploaded PDF./clean-text/POSTCleans and prepares the extracted text./summarize-text/POSTSummarizes the cleaned text./generate-script/POSTGenerates a dialogue-style podcast script./convert-to-audio/POSTConverts the script to audio files./combine-audio/POSTCombines the audio files into a single sequence./enhance-audio/POSTEnhances the quality of the combined audio.

Troubleshooting
---------------

### Common Issues

*   **PDF not uploading**:
    
    *   Ensure the PDF file is under the size limit and properly formatted.
        
*   **Audio not generated**:
    
    *   Check if gTTS and pydub are installed.
        
*   **API errors**:
    
    *   Confirm that the backend is running at http://127.0.0.1:8000.
        
*   **Loading forever**:
    
    *   Check the console logs in the browser for debugging.
        


Future Improvements
-------------------

*   Add support for multi-lingual text-to-speech generation.
    
*   Implement user authentication for secure access.
    
*   Integrate advanced audio enhancement tools like Adobe Audition APIs.
    
*   Create a fully responsive frontend with modern frameworks like React.
    

Contributing
------------

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
    
2.  Create a feature branch (git checkout -b feature/your-feature).
    
3.  Commit your changes (git commit -m "Add feature").
    
4.  Push the branch (git push origin feature/your-feature).
    
5.  Open a pull request.



Output Screenshot
------------------

The audio file can be found in the audio files directory named as "enhanced_audio.mp3"


![image](https://github.com/user-attachments/assets/c9606625-af53-4d61-905a-02da5ffcf3cb)
