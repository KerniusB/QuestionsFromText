import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import PyPDF2
from openai import OpenAI
from timeit import default_timer as timer
from dotenv import load_dotenv
from tkinter import ttk
import time


# Function to check if the extracted text is meaningful based on its length
def is_meaningful_text(text):
    min_text_length = 10
    return len(text.strip()) >= min_text_length


def remove_chars_from_end(string):
    last_comma_index = string.rfind(',')
    if last_comma_index != -1:
        return string[:last_comma_index]
    else:
        return string


def string_to_json(questions_string):
    # Parse the string to a Python dictionary
    questions_dict = json.loads(questions_string)

    # Save the dictionary to a JSON file
    with open(str(time.strftime("%Y%m%d-%H%M%S")) + ".json", 'w') as json_file:
        json.dump(questions_dict, json_file, indent=2)

    print("JSON file saved successfully.")


# Function to extract text from PDF and generate questions
def extract_text_from_pdf_and_generate_questions(pdf_path, selected_model):
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            number_of_questions = 0

            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if is_meaningful_text(page_text):
                    if number_of_questions == 0:
                        start = timer()
                        json_string = '{'

                    number_of_questions += 1

                    question = generate_question(page_text, selected_model)
                    json_string += f"\"question{number_of_questions}\": {question},"

            json_string = remove_chars_from_end(json_string)
            json_string += '}'
            string_to_json(json_string)
            end = timer()
            print(f"GENERATING TOOK: {end - start}")

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
    if pdf_path == "":
        pdf_path = "/Users/kerniusbrazauskas/Desktop/Constitution of the Republic of Lithuania.pdf"
    if pdf_path:
        selected_model = model_var.get()
        success, message = extract_text_from_pdf_and_generate_questions(pdf_path, selected_model)
        if success:
            messagebox.showinfo('Success', 'Text extracted and questions generated successfully!')
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
    return completion.choices[0].message.content


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
root.title('Questions generator from PDF')

# Top label
ttk.Label(root, text='Select PDF file:').pack()

# Create frame for PDF selection
pdf_selection_frame = ttk.Frame(root)
pdf_selection_frame.pack(pady=10)
ttk.Button(pdf_selection_frame, text='Browse', command=select_pdf).pack(side=tk.LEFT, padx=5)
pdf_path_entry = ttk.Entry(pdf_selection_frame, width=70)
pdf_path_entry.pack()

# Create frame for model selection
model_frame = ttk.Frame(root)
model_frame.pack(pady=10)
ttk.Label(model_frame, text='Select Model:').pack(side=tk.LEFT)
model_var = tk.StringVar(value="chat_gpt")
ttk.Radiobutton(model_frame, text="ChatGPT", variable=model_var, value="chat_gpt").pack(side=tk.LEFT)
ttk.Radiobutton(model_frame, text="Mistral", variable=model_var, value="mistral").pack(side=tk.LEFT)

# Create frame for buttons
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)
ttk.Button(button_frame, text='Generate questions', command=generate_questions).pack(side=tk.LEFT)
ttk.Button(button_frame, text='Exit', command=root.destroy).pack(side=tk.LEFT)

# Run the application
root.mainloop()
