import os
import tkinter as tk
from tkinter import filedialog, messagebox
import PyPDF2
from openai import OpenAI
from timeit import default_timer as timer
from dotenv import load_dotenv


# Function to check if the extracted text is meaningful based on its length
def is_meaningful_text(text):
    min_text_length = 10
    return len(text.strip()) >= min_text_length


# Function to extract text from PDF and generate questions
def extract_text_from_pdf(pdf_path, selected_model):
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            number_of_questions = 0

            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if is_meaningful_text(page_text):

                    if number_of_questions == 0:
                        start = timer()

                    number_of_questions += 1

                    question = generate_question(page_text, selected_model)
                    print(f"\"question{number_of_questions}\": {question},")

            end = timer()
            print(f"GENERATING TOOK: {end - start}")
            print(f"Prompt tokens: {number_of_prompt_tokens}")
            print(f"Output tokens: {number_of_completion_tokens}")

        return True, None
    except Exception as e:
        return False, str(e)


# Function to select PDF file
def select_pdf():
    pdf_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    pdf_path_entry.delete(0, tk.END)
    pdf_path_entry.insert(0, pdf_path)


# Function to extract text from the selected PDF file and generate questions
def generate_questions():
    pdf_path = pdf_path_entry.get()
    if pdf_path:
        selected_model = model_var.get()
        success, message = extract_text_from_pdf(pdf_path, selected_model)
        if success:
            messagebox.showinfo('Success', 'Text extracted successfully!')
        else:
            messagebox.showerror('Extraction Failed', f'Error: {message}')
    else:
        messagebox.showerror('Error', 'Please select a PDF file!')


# Function to generate a question using the selected model
def generate_question(user_input, model):
    if model == "mistral":
        return make_call_to_mistral(user_input, system_message)
    elif model == "chat_gpt":
        return make_call_to_chat_gpt(user_input, system_message)


# Function to call Mistral model API
def make_call_to_mistral(user_input, system_input):
    completion = client.chat.completions.create(
        model="TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
        messages=[
            {"role": "system", "content": system_input},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7,
    )
    return completion.choices[0].message.content


# Function to call ChatGPT model API
def make_call_to_chat_gpt(user_input, system_input):
    completion = chatGptClient.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": system_input},
            {"role": "user", "content": user_input}
        ]
    )
    global number_of_prompt_tokens
    global number_of_completion_tokens

    number_of_prompt_tokens += completion.usage.prompt_tokens
    number_of_completion_tokens += completion.usage.completion_tokens

    return completion.choices[0].message.content


# Initialization of token counters
number_of_prompt_tokens = 0
number_of_completion_tokens = 0

# Point to the local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

# Load environment variables
load_dotenv()
chatGptClient = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define system message for generating questions
system_message = (
    "Create 1 quiz question from the text. "
    "Give 3 possible answers, 1 of these answers is correct, the others should be wrong. "
    "Mark the correct answer. "
    "Formulate answer in JSON format where: "
    "under 'question' tag question is stated, "
    "under 'optionA' tag option A is stated, "
    "under 'optionB' tag option B is stated, "
    "under 'optionC' tag option C is stated, "
    "under 'correctAnswerLetter' tag correct option letter is stated. "
    "No need for '```json' at the beginning and end."
)

# Create the main window
root = tk.Tk()
root.title('PDF Text Extractor')

# Create and place widgets
tk.Label(root, text='Select PDF file:').pack()
pdf_path_entry = tk.Entry(root, width=50)
pdf_path_entry.pack()
tk.Button(root, text='Browse', command=select_pdf).pack(pady=5)

# Create and place radiobuttons for model selection
model_var = tk.StringVar(value="mistral")
tk.Label(root, text='Select Model:').pack()
tk.Radiobutton(root, text="Mistral", variable=model_var, value="mistral").pack(anchor=tk.W)
tk.Radiobutton(root, text="ChatGPT", variable=model_var, value="chat_gpt").pack(anchor=tk.W)

# Create and place buttons
tk.Button(root, text='Generate questions', command=generate_questions).pack(pady=5)
tk.Button(root, text='Exit', command=root.destroy).pack(pady=5)

# Run the application
root.mainloop()
