import os
import tkinter as tk
from tkinter import filedialog
import PyPDF2
from openai import OpenAI
from timeit import default_timer as timer
from dotenv import load_dotenv, dotenv_values


def is_meaningful_text(text):
    # Define a threshold for meaningful text length
    min_text_length = 10
    # Check if the text is meaningful based on its length
    return len(text.strip()) >= min_text_length


def extract_text_from_pdf(pdf_path, txt_path):
    try:
        # Open the PDF file
        with open(pdf_path, 'rb') as pdf_file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            # Initialize an empty string to store the text
            text = ''

            # Loop through each page of the PDF
            for page_num in range(len(pdf_reader.pages)):
                # Extract text from the current page
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()

                # Check if the extracted text is meaningful
                if is_meaningful_text(page_text):
                    text += page_text + '\n'

                    # Timer start
                    if page_num == 0:
                        start = timer()
                        number_of_questions = 0

                    number_of_questions += 1

                    # Generate mistral questions and print them
                    print("\"question" + str(number_of_questions) + "\": ")
                    print(make_call_to_mistral(page_text, system_message) + ",")

                    # # Generate ChatGPT questions and print them
                    # print("\"question" + str(number_of_questions) + "\": ")
                    # print(make_call_to_chat_gpt(page_text, system_message) + ",")

            # Stop timer
            end = timer()
            print("GENERATING TOOK: ", end - start)
            print("Prompt tokens: ", number_of_prompt_tokens)
            print("Output tokens: ", number_of_completion_tokens)

            # Write the filtered text to a text file
            with open(txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(text)

        return True, None
    except Exception as e:
        return False, str(e)


def select_pdf():
    pdf_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    pdf_path_entry.delete(0, tk.END)
    pdf_path_entry.insert(0, pdf_path)


def extract_text():
    pdf_path = pdf_path_entry.get()
    if pdf_path:
        txt_path = pdf_path.replace('.pdf', '.txt')
        success, message = extract_text_from_pdf(pdf_path, txt_path)
        if success:
            tk.messagebox.showinfo('Success', 'Text extracted successfully!')
        else:
            tk.messagebox.showerror('Extraction Failed', f'Error: {message}')
    else:
        tk.messagebox.showerror('Error', 'Please select a PDF file!')


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


number_of_prompt_tokens = 0
number_of_completion_tokens = 0

# Point to the local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

# ChatGPT

# loading variables from .env file
load_dotenv()
chatGptClient = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

system_message = (
    "Create 1 quiz question from the text. "
    "Give 3 possible answers, 1 of these answers is correct, the others should be wrong. "
    "Mark the correct answer."
    "Formulate answer in json formate where: "
    "under 'question' tag question is stated, "
    "under 'optionA' tag option A is stated, "
    "under 'optionB' tag option B is stated, "
    "under 'optionC' tag option C is stated, "
    "under 'correctAnswerLetter' tag correct option letter is stated"
    "no need for '```json' at the beginning and end"

)

# Create the main window
root = tk.Tk()
root.title('PDF Text Extractor')

# Create and place widgets
tk.Label(root, text='Select PDF file:').pack()
pdf_path_entry = tk.Entry(root, width=50)
pdf_path_entry.pack()
tk.Button(root, text='Browse', command=select_pdf).pack(pady=5)
tk.Button(root, text='Extract Text', command=extract_text).pack(pady=5)
tk.Button(root, text='Exit', command=root.destroy).pack(pady=5)

# Run the application
root.mainloop()
