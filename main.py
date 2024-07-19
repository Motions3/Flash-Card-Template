from tkinter import *
import pandas as pd
import random
import os

BACKGROUND_COLOR = "#B1DDC6"
current_card = {}
to_learn = []
known_words = []
selected_language = ""
selected_mode = ""  # Track practice mode
flip_timer = None  # Initialize flip_timer
countdown_timer = None  # Initialize countdown_timer
countdown_seconds = 15  # Duration of the countdown timer in seconds


def load_data(language, mode):
    global to_learn
    file_path_learn = f"data/{language}_words_to_learn.csv"
    file_path_original = f"data/{language}_words.csv"

    print(f"Loading data for language: {language}, mode: {mode}")

    if mode == "all_words":
        try:
            if os.path.exists(file_path_original):
                data = pd.read_csv(file_path_original, on_bad_lines='warn')
                to_learn = data.to_dict(orient="records")
                print(f"Loaded {len(to_learn)} words from {file_path_original}")
            else:
                print(f"File not found: {file_path_original}")
                to_learn = []  # Ensure to_learn is empty if file is not found
        except Exception as e:
            print(f"Error loading data: {e}")
            to_learn = []  # Ensure to_learn is empty if there is an error
    elif mode == "words_to_learn":
        try:
            if os.path.exists(file_path_learn):
                data = pd.read_csv(file_path_learn, on_bad_lines='warn')
                to_learn = data.to_dict(orient="records")
                print(f"Loaded {len(to_learn)} words from {file_path_learn}")
            else:
                print(f"File not found: {file_path_learn}. Trying fallback: {file_path_original}")
                if os.path.exists(file_path_original):
                    original_data = pd.read_csv(file_path_original, on_bad_lines='warn')
                    to_learn = original_data.to_dict(orient="records")
                    print(f"Loaded {len(to_learn)} words from fallback file {file_path_original}")
                else:
                    print(f"Both files are missing: {file_path_learn} and {file_path_original}")
                    to_learn = []  # Ensure to_learn is empty if files are not found
        except Exception as e:
            print(f"Error loading data: {e}")
            to_learn = []  # Ensure to_learn is empty if there is an error


def load_known_words():
    global known_words
    file_path_known = f"data/{selected_language}_words_known.csv"
    if os.path.exists(file_path_known):
        try:
            data = pd.read_csv(file_path_known, on_bad_lines='warn')
            known_words = data.to_dict(orient="records")
            print(f"Loaded {len(known_words)} known words from {file_path_known}")
        except Exception as e:
            print(f"Error loading known words: {e}")
            known_words = []
    else:
        known_words = []


def save_known_words():
    try:
        known_data = pd.DataFrame(known_words)
        if not known_data.empty:
            known_data.to_csv(f"data/{selected_language}_words_known.csv", index=False)
            print(f"Saved {len(known_words)} known words to CSV")
        else:
            print("No known words to save.")
    except Exception as e:
        print(f"Error saving known words: {e}")


def save_to_learn_words():
    try:
        data = pd.DataFrame(to_learn)
        if not data.empty:
            data.to_csv(f"data/{selected_language}_words_to_learn.csv", index=False)
            print(f"Saved {len(to_learn)} words to learn to CSV")
        else:
            print("No words to learn to save.")
    except Exception as e:
        print(f"Error saving words to learn: {e}")


def start_flashcards(language):
    global selected_language
    selected_language = language.lower()
    show_practice_mode_menu()  # Show the new practice mode menu


def show_practice_mode_menu():
    global practice_mode_frame

    language_menu_frame.grid_forget()
    practice_mode_frame = Frame(window, bg=BACKGROUND_COLOR)
    practice_mode_label = Label(practice_mode_frame, text="Choose practice mode", bg=BACKGROUND_COLOR,
                                font=("Arial", 24, "bold"))
    practice_mode_label.pack(pady=20)

    all_words_button = Button(practice_mode_frame, text="Practice All Words", font=("Arial", 20, "bold"),
                              command=lambda: start_practice("all_words"))
    all_words_button.pack(pady=10)

    unknown_button = Button(practice_mode_frame, text="Practice Unknown Words", font=("Arial", 20, "bold"),
                            command=lambda: start_practice("words_to_learn"))
    unknown_button.pack(pady=10)

    known_button = Button(practice_mode_frame, text="Practice Known Words", font=("Arial", 20, "bold"),
                          command=lambda: start_practice("words_known"))
    known_button.pack(pady=10)

    practice_mode_frame.grid(row=0, column=0, columnspan=2)


def start_practice(mode):
    global selected_mode
    selected_mode = mode
    load_data(selected_language, selected_mode)
    load_known_words()

    if selected_mode == "all_words":
        if to_learn:
            next_card()
            practice_mode_frame.grid_forget()
            flashcard_frame.grid(row=0, column=0, columnspan=2)
            unknown_button.grid(row=1, column=0)
            known_button.grid(row=1, column=1)
        else:
            show_error_popup("No data available to practice.")
    elif selected_mode == "words_to_learn":
        if to_learn:
            next_card()
            practice_mode_frame.grid_forget()
            flashcard_frame.grid(row=0, column=0, columnspan=2)
            unknown_button.grid(row=1, column=0)
            known_button.grid(row=1, column=1)
        else:
            show_error_popup("No data available to learn.")
    elif selected_mode == "words_known":
        if known_words:
            next_card()
            practice_mode_frame.grid_forget()
            flashcard_frame.grid(row=0, column=0, columnspan=2)
            keep_card_button.grid(row=1, column=0)  # Show the "Keep Card" button
            remove_card_button.grid(row=1, column=1)  # Show the "Remove Card" button
        else:
            show_error_popup("No known words available.")


def next_card():
    global current_card, flip_timer, countdown_timer, countdown_seconds

    if flip_timer is not None:
        window.after_cancel(flip_timer)
    if countdown_timer is not None:
        window.after_cancel(countdown_timer)

    if selected_mode in ["words_to_learn", "all_words"]:
        if not to_learn:
            print("No cards to display.")
            return
        current_card = random.choice(to_learn)
    elif selected_mode == "words_known":
        if not known_words:
            print("No known words to display.")
            return
        current_card = random.choice(known_words)

    canvas.itemconfig(card_title, text=selected_language.capitalize(), fill="black")
    canvas.itemconfig(card_word, text=current_card.get(selected_language.capitalize(), "No Word"), fill="black")
    canvas.itemconfig(card_background, image=card_front_img)
    flip_timer = window.after(15000, func=flip_card)
    start_countdown()  # Start countdown timer


def start_countdown():
    global countdown_seconds, countdown_timer

    countdown_seconds = 15  # Reset countdown seconds
    countdown_timer_label.config(text=f"Answer in: {countdown_seconds} s")
    countdown_timer = window.after(1000, update_countdown)


def update_countdown():
    global countdown_seconds, countdown_timer

    countdown_seconds -= 1
    if countdown_seconds > 0:
        countdown_timer_label.config(text=f"Answer in: {countdown_seconds} s")
        countdown_timer = window.after(1000, update_countdown)
    else:
        # Time's up, automatically flip the card
        flip_card()


def flip_card():
    canvas.itemconfig(card_title, text="English", fill="white")
    canvas.itemconfig(card_word, text=current_card.get("English", "No English"), fill="white")
    canvas.itemconfig(card_background, image=card_back_img)


def keep_card():
    next_card()


def remove_card():
    if current_card in known_words:
        known_words.remove(current_card)
        save_known_words()
    next_card()


def is_known():
    if selected_mode in ["words_to_learn", "all_words"]:
        global to_learn, known_words
        if current_card in to_learn:
            to_learn.remove(current_card)
            save_to_learn_words()  # Save updated list

        # Update the known words list
        known_words.append(current_card)
        save_known_words()  # Save updated list

        next_card()


def is_unknown():
    if selected_mode in ["words_to_learn", "all_words"]:
        global to_learn
        if current_card in to_learn:
            save_to_learn_words()  # Save updated list

        next_card()


def show_error_popup(message):
    error_popup = Toplevel(window)
    error_popup.title("Error")
    error_popup.config(bg=BACKGROUND_COLOR)

    error_message = Label(error_popup, text=message, bg=BACKGROUND_COLOR, font=("Arial", 16, "bold"))
    error_message.pack(pady=20, padx=20)

    ok_button = Button(error_popup, text="OK", font=("Arial", 14, "bold"), command=error_popup.destroy)
    ok_button.pack(pady=10)

    error_popup.mainloop()


def exit_app():
    window.quit()


# Set up the main window
window = Tk()
window.title("Flashy")
window.config(padx=50, pady=50, bg=BACKGROUND_COLOR)
window.resizable(width=False, height=False)

# Language selection menu
language_menu_frame = Frame(window, bg=BACKGROUND_COLOR)
language_menu_label = Label(language_menu_frame, text="Select a language", bg=BACKGROUND_COLOR,
                            font=("Arial", 24, "bold"))
language_menu_label.pack(pady=20)

languages = ["Spanish", "French", "Japanese"]
for language in languages:
    button = Button(language_menu_frame, text=language, font=("Arial", 20, "bold"),
                    command=lambda l=language: start_flashcards(l))
    button.pack(pady=10)


language_menu_frame.grid(row=0, column=0, columnspan=2)

# Flashcard UI
flashcard_frame = Frame(window, bg=BACKGROUND_COLOR)
canvas = Canvas(flashcard_frame, width=800, height=526)
card_front_img = PhotoImage(file="images/card_front.png")
card_back_img = PhotoImage(file="images/card_back.png")
card_background = canvas.create_image(400, 263, image=card_front_img)
card_title = canvas.create_text(400, 150, text="", font=("Arial", 40, "italic"))
card_word = canvas.create_text(400, 263, text="", font=("Arial", 60, "bold"))
canvas.config(bg=BACKGROUND_COLOR, highlightthickness=0)
canvas.grid(row=0, column=0, columnspan=2)

cross_image = PhotoImage(file="images/wrong.png")
unknown_button = Button(flashcard_frame, image=cross_image, highlightthickness=0, command=is_unknown)

check_image = PhotoImage(file="images/right.png")
known_button = Button(flashcard_frame, image=check_image, highlightthickness=0, command=is_known)

keep_image = PhotoImage(file="images/right.png")  # Reusing the "right" image for "Keep Card" button
keep_card_button = Button(flashcard_frame, image=keep_image, highlightthickness=0, command=keep_card)

remove_image = PhotoImage(file="images/wrong.png")  # Reusing the "wrong" image for "Remove Card" button
remove_card_button = Button(flashcard_frame, image=remove_image, highlightthickness=0, command=remove_card)

# Exit button
exit_button_practice = Button(window, text="Exit", font=("Arial", 14, "bold"), command=exit_app)
exit_button_practice.grid(row=2, column=0, columnspan=2)

# Countdown timer label
countdown_timer_label = Label(flashcard_frame, text=f"Answer in: {countdown_seconds} s", bg=BACKGROUND_COLOR,
                              font=("Arial", 16, "bold"))
countdown_timer_label.grid(row=2, column=0, columnspan=2)

# Initially hide the flashcard frame
flashcard_frame.grid_forget()

window.mainloop()
