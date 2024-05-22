# PDF to Quiz Question Generator

This project provides a tool for generating quiz questions from PDF documents. It utilizes OpenAI models to extract meaningful text from PDFs and generate questions based on the extracted text. The tool is built using Python and Tkinter for the graphical user interface.

## Features

- **PDF Text Extraction:** Extracts meaningful text from PDF files.
- **Question Generation:** Generates quiz questions with three possible answers, one of which is correct.
- **Model Selection:** Allows users to choose between different AI models for question generation.

## Requirements

- Python 3.x
- `PyPDF2`
- `openai`
- `python-dotenv`
- `tkinter`
- `time`

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/pdf-to-quiz-question-generator.git
    cd pdf-to-quiz-question-generator
    ```

2. Install the required Python packages:

    ```bash
    pip install PyPDF2 openai python-dotenv
    ```

3. Set up your environment variables:

    - Create a `.env` file in the project root.
    - Add your OpenAI API key to the `.env` file:

    ```plaintext
    OPENAI_API_KEY=your_openai_api_key
    ```

## Usage

1. Run the script:

    ```bash
    python main.py
    ```

2. Use the GUI to:
    - Select a PDF file from which to extract text.
    - Choose the AI model for generating questions.
    - Generate quiz questions and save them as a JSON file.

## File Structure

- `main.py`: The main script containing the GUI and logic for text extraction and question generation.
- `.env`: File to store environment variables.
- `README.md`: This file.
