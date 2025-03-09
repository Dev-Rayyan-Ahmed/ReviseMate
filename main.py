# Revise Smarter, Retain Better ~!

import customtkinter as C
from tkinter import filedialog,messagebox
import json,random,pdfplumber,os
import tkinter as Tk
import genanki

#Main GUI Window for thee User:
C.set_appearance_mode("light")
C.set_default_color_theme("dark-blue")

def browseFile():
    PageContent = []
    filePath = filedialog.askopenfilename(title="Choose a PDF file", filetypes=[("PDF Files", "*.pdf")])
    with pdfplumber.open(filePath) as pdf:
        for page in pdf.pages:
            PageContent.append(page.extract_text())

    allContent = " \n ".join(PageContent)

    CreatingLable = C.CTkLabel(frame,text="Generating Flash Cards......",font = ("Times New Roman",14,"italic"),text_color="blue")
    CreatingLable.pack()
    root.update_idletasks()
    frame.update_idletasks()

    # Extracting PDF Name:-->
    pdf_name = os.path.splitext(os.path.basename(filePath))[0]
    generate_FlashCards(allContent,pdf_name)
    jsonFileName = pdf_name + " FlashCards.json"

    load_and_Display_FlashCards(jsonFileName)



def changeTheme():
    current_mode = C.get_appearance_mode()
    new_mode = "Dark" if current_mode == "Light" else "Light"
    C.set_appearance_mode(new_mode)

def load_and_Display_FlashCards(fileName=""):

    if fileName == "":
        fileName = filedialog.askopenfilename(title="Choose a JSON file",
                                                                    filetypes=[("JSON Files", "*.json")])
    def show_menu(event):
        ConfigMenu.post(event.x_root, event.y_root)

    def show_answer(i):
        AnswerLable.configure(text=flashcards[i[0]]["answer"])
    def reset_answer():
        AnswerLable.configure(text="")
    def next(i):
        i[0] = min(i[0] + 1,len(flashcards)-1)
        QuestionLable.configure(text=flashcards[i[0]]["question"])
        reset_answer()
    def prev(i):
        i[0] = max(i[0] - 1,0)
        QuestionLable.configure(text=flashcards[i[0]]["question"])
        reset_answer()

    def Export_Anki():
        with open(fileName, "r", encoding="utf-8") as f:
            data = json.load(f)
        flashcards = data["flashcards"]

        # unique deck and model IDs
        deck_id = random.randint(1_000_000_000, 2_000_000_000)
        model_id = random.randint(1_000_000_000, 2_000_000_000)

        deck_name = "ReviseMate Flashcards"
        my_deck = genanki.Deck(deck_id, deck_name)

        # simple card model
        my_model = genanki.Model(
            model_id,
            'Simple Model',
            fields=[
                {'name': 'Question'},
                {'name': 'Answer'},
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': '{{Question}}',  # Front side (question)
                    'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',  # Back side (answer)
                },
            ]
        )

        # Add each flashcard as a note to the deck
        for flashcard in flashcards:
            note = genanki.Note(
                model=my_model,
                fields=[flashcard["question"], flashcard["answer"]]
            )
            my_deck.add_note(note)

        # Export:-->
        output_file = f"{fileName[:-15]} ReviseMate_Deck.apkg"
        genanki.Package(my_deck).write_to_file(output_file)

    # Question Iterator [ i ] :-->
    i = [0]

    C.set_appearance_mode("light")
    C.set_default_color_theme("dark-blue")

    Flashy = C.CTk()
    Flashy.title("Flash Cards")
    Flashy.geometry("800x400+450+200")

    Flashy.rowconfigure(0, weight=1)  # Increase weight to give more space to frame2

    frame2 = C.CTkFrame(Flashy, fg_color="lightgray",height=200)
    frame2.grid(column=0, row=0, columnspan=2, rowspan=2 ,padx=80, pady=20, sticky="nsew")

    Flashy.columnconfigure(0, weight=1)
    Flashy.columnconfigure(1, weight=1)

    b1 = C.CTkButton(Flashy, text="Previous", width=40, height=30,command=lambda: prev(i))
    b1.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

    b2 = C.CTkButton(Flashy, text="Next", width=40, height=30,command=lambda: next(i))
    b2.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

    b3 = C.CTkButton(Flashy, text="Show Answer", width=40, height=30,command=lambda: show_answer(i))
    b3.grid(column=0, row=4, columnspan=2, padx=20, pady=20, sticky="ew")

    Config = C.CTkButton(Flashy, text="⚙", width=10, height=30)
    Config.place(x=750, y=20)

    ConfigMenu = Tk.Menu(Flashy, tearoff=0)
    ConfigMenu.add_command(label="Change Theme", command=changeTheme)
    ConfigMenu.add_command(label="Export to Anki", command=Export_Anki)

    Config.bind("<Button-1>", show_menu)

    with open(fileName,"r") as f:
        data = json.load(f)

    flashcards = data["flashcards"]

    QuestionLable = C.CTkLabel(frame2,text=flashcards[i[0]]["question"],font=("Times New Roman",25,"italic"),text_color="black",wraplength=500)
    QuestionLable.pack(padx=20, pady=10)

    AnswerLable = C.CTkLabel(frame2,text="",font=("Times New Roman",25,"bold"),text_color="green",wraplength=500)
    AnswerLable.pack(padx=20, pady=10)

    Flashy.mainloop()

def generate_FlashCards(Content : str, pdf_name: str):
    # Setting up MistralAPI
    from mistralai import Mistral

    api_key = os.getenv("MISTRAL_API_KEY")
    model = "mistral-large-latest"
    client = Mistral(api_key=api_key)

    # Flashcard Generation Prompt:--->
    prompt = f"""
    You are an AI tutor that generates smart flashcards for efficient learning.

    Below is the content of a document. Your task is to extract the most important concepts, definitions, key facts, and questions from it and format them as **flashcards** in the following JSON structure:

    {{
      "flashcards": [
        {{"question": "QUESTION_HERE", "answer": "ANSWER_HERE"}},
        {{"question": "QUESTION_HERE", "answer": "ANSWER_HERE"}}
      ]
    }}

    - Focus on **important terms, definitions, and key takeaways**.  
    - If there are **bold or highlighted words**, treat them as important keywords.  
    - Frame **questions concisely** and provide **clear, to-the-point answers**.  
    - Ensure the answers explain the concept well but remain **brief and useful for review**.  
    - Generate at least **10-15 high-quality flashcards** based on the text.  

    Here is the document content:
    {Content}
    """

    # Sending the request
    chat_response = client.chat.complete(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    FlashCards_json =  chat_response.choices[0].message.content
    FlashCards_json = FlashCards_json.strip("'''").strip("'''json")

    clean_json = FlashCards_json[7:-3].strip() # Apparently the API was adding '''json at the start
                                               # and ''' at the end which was creating issues with Parsing.
    output = f"{pdf_name} FlashCards.json"

    try:
        flashcards = json.loads(clean_json)
        with open(output, "w", encoding="utf-8") as f:
            json.dump(flashcards, f, indent=4)

        # print(f"Flashcards saved to {output}")
        return flashcards["flashcards"]

    except:
        messagebox.showerror(title = "Error" , text = "Error parsing flashcards JSON")

# # # # # ----------------------------------------------------------------------------------

def show_menu_MAIN(event):
    MainConfig.post(event.x_root, event.y_root)

root = C.CTk()
root.geometry("600x250+500+250")
root.title("ReviseMate")

frame = C.CTkFrame(root)
frame.pack(pady = 20 ,padx=60, fill="both", expand=True)

l1 = C.CTkLabel(frame,text = "Welcome to ReviseMate", font = ("Roboto CN",25,"bold"))
l1.pack(pady=(10,0))
l2 = C.CTkLabel(frame,text = "Revise Smarter, Retain Better", font = ("Times New Roman",16,"italic"), text_color="Green")
l2.pack(pady=0)

instruction = C.CTkLabel(frame, text="Select a PDF file to generate smart flashcards.", font=("Verdana", 14))
instruction.pack(pady=10)

button_frame = C.CTkFrame(frame)
button_frame.pack(pady=10)  # Use pack for the frame

BrowseButton = C.CTkButton(button_frame, text="Browse", command=browseFile)
BrowseButton.grid(row=0, column=0, padx=10, pady=10)

ExitButton = C.CTkButton(button_frame, text="Exit", command=root.destroy)
ExitButton.grid(row=0, column=1, padx=10, pady=10)

Config = C.CTkButton(root, text= "⚙", width=10, height=30)
Config.place(x=550, y=20)

MainConfig = Tk.Menu(root, tearoff=0)
MainConfig.add_command(label= "Change Theme", command=changeTheme)
MainConfig.add_command(label="Load FlashCards",command=load_and_Display_FlashCards)

Config.bind("<Button-1>", show_menu_MAIN)

root.mainloop()
