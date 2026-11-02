import os
import json
import random
import urllib.parse
import urllib.request
import tkinter as tk
from tkinter import ttk, messagebox

# --- CONFIGURATION & CONSTANTS ---
DATA_FILE = "linguakey_data.json"

LANGUAGES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Japanese": "ja",
    "Chinese": "zh"
}

# --- DATA MANAGER ---
class DataManager:
    def __init__(self, filename=DATA_FILE):
        self.filename = filename
        self.data = self.load_data()

    def load_data(self):
        if not os.path.exists(self.filename):
            initial_data = {"users": {}}
            self.save_data(initial_data)
            return initial_data
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data file: {e}")
            return {"users": {}}

    def save_data(self, data=None):
        if data is None:
            data = self.data
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {e}")

    def get_users(self):
        return list(self.data.get("users", {}).keys())

    def add_user(self, username):
        if username not in self.data["users"]:
            self.data["users"][username] = {}
            self.save_data()
            return True
        return False

    def get_language_pairs(self, username):
        return list(self.data["users"].get(username, {}).keys())

    def add_language_pair(self, username, pair_key, known_code, target_code):
        if pair_key not in self.data["users"][username]:
            self.data["users"][username][pair_key] = {
                "known_code": known_code,
                "target_code": target_code,
                "words": {} # Dict keyed by foreign word
            }
            self.save_data()
            return True
        return False

# --- MAIN GUI APPLICATION ---
class LinguaKeyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LinguaKey - Desktop Language Tracker")
        self.geometry("850x650")
        self.minsize(750, 550)

        self.db_manager = DataManager()
        self.current_user = None
        self.current_pair = None
        self.quiz_direction = "foreign_to_native" # or 'native_to_foreign'
        self.current_quiz_word = None

        # Build Navigation & Screen Container
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.show_user_selection_screen()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # ==========================================
    # SCREEN 1: USER SELECTION / CREATION
    # ==========================================
    def show_user_selection_screen(self):
        self.clear_container()

        frame = ttk.Frame(self.container, padding="30")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(frame, text="LinguaKey", font=("Helvetica", 24, "bold")).pack(pady=10)
        ttk.Label(frame, text="Select or Create User Profile", font=("Helvetica", 12)).pack(pady=5)

        users = self.db_manager.get_users()
        
        # Select Existing User
        if users:
            ttk.Label(frame, text="Select Existing User:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(15, 2))
            user_var = tk.StringVar(value=users[0])
            user_dropdown = ttk.Combobox(frame, textvariable=user_var, values=users, state="readonly", width=30)
            user_dropdown.pack(pady=5)

            def load_user():
                self.current_user = user_var.get()
                self.show_language_selection_screen()

            ttk.Button(frame, text="Continue as Selected User", command=load_user).pack(pady=5, fill="x")

            ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=15)

        # Create New User
        ttk.Label(frame, text="Create New User:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(5, 2))
        new_user_entry = ttk.Entry(frame, width=32)
        new_user_entry.pack(pady=5)

        def create_user():
            name = new_user_entry.get().strip()
            if not name:
                messagebox.showwarning("Warning", "Please enter a user name.")
                return
            if self.db_manager.add_user(name):
                self.current_user = name
                self.show_language_selection_screen()
            else:
                messagebox.showerror("Error", "User already exists.")

        ttk.Button(frame, text="Create User Profile", command=create_user).pack(pady=5, fill="x")

    # ==========================================
    # SCREEN 2: LANGUAGE PAIR SELECTION / CREATION
    # ==========================================
    def show_language_selection_screen(self):
        self.clear_container()

        frame = ttk.Frame(self.container, padding="30")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(frame, text=f"Welcome, {self.current_user}!", font=("Helvetica", 18, "bold")).pack(pady=5)
        ttk.Label(frame, text="Select or Create a Language Pair", font=("Helvetica", 11)).pack(pady=5)

        pairs = self.db_manager.get_language_pairs(self.current_user)

        # Select Existing Pair
        if pairs:
            ttk.Label(frame, text="Select Existing Pair:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(15, 2))
            pair_var = tk.StringVar(value=pairs[0])
            pair_dropdown = ttk.Combobox(frame, textvariable=pair_var, values=pairs, state="readonly", width=35)
            pair_dropdown.pack(pady=5)

            def load_pair():
                self.current_pair = pair_var.get()
                self.show_main_app_screen()

            ttk.Button(frame, text="Load Language Pair", command=load_pair).pack(pady=5, fill="x")
            ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=15)

        # Create New Pair
        ttk.Label(frame, text="Create New Language Pair:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(5, 2))

        known_frame = ttk.Frame(frame)
        known_frame.pack(fill="x", pady=2)
        ttk.Label(known_frame, text="Language I Know:", width=18).pack(side="left")
        known_cb = ttk.Combobox(known_frame, values=list(LANGUAGES.keys()), state="readonly", width=15)
        known_cb.set("English")
        known_cb.pack(side="right")

        target_frame = ttk.Frame(frame)
        target_frame.pack(fill="x", pady=2)
        ttk.Label(target_frame, text="Language to Learn:", width=18).pack(side="left")
        target_cb = ttk.Combobox(target_frame, values=list(LANGUAGES.keys()), state="readonly", width=15)
        target_cb.set("Spanish")
        target_cb.pack(side="right")

        def create_pair():
            k_name, t_name = known_cb.get(), target_cb.get()
            if k_name == t_name:
                messagebox.showwarning("Warning", "Known and Target languages must be different.")
                return
            pair_key = f"{k_name} -> {t_name}"
            k_code, t_code = LANGUAGES[k_name], LANGUAGES[t_name]

            if self.db_manager.add_language_pair(self.current_user, pair_key, k_code, t_code):
                self.current_pair = pair_key
                self.show_main_app_screen()
            else:
                messagebox.showerror("Error", "This language pair already exists.")

        ttk.Button(frame, text="Create Pair Data", command=create_pair).pack(pady=10, fill="x")

        # Back Button
        ttk.Button(frame, text="← Back to User Selection", command=self.show_user_selection_screen).pack(pady=5)

    # ==========================================
    # MAIN WORKSPACE (TABS)
    # ==========================================
    def show_main_app_screen(self):
        self.clear_container()

        # Top Bar (Header & Switch Profile)
        top_bar = ttk.Frame(self.container, padding="10")
        top_bar.pack(fill="x")

        info_text = f"User: {self.current_user}  |  Profile: {self.current_pair}"
        ttk.Label(top_bar, text=info_text, font=("Helvetica", 10, "bold")).pack(side="left")
        ttk.Button(top_bar, text="Switch Profile / Language", command=self.show_language_selection_screen).pack(side="right")

        # Tab Control
        self.notebook = ttk.Notebook(self.container)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        self.tab_add = ttk.Frame(self.notebook, padding="15")
        self.tab_quiz = ttk.Frame(self.notebook, padding="15")
        self.tab_db = ttk.Frame(self.notebook, padding="15")
        self.tab_stats = ttk.Frame(self.notebook, padding="15")

        self.notebook.add(self.tab_add, text="Add Word")
        self.notebook.add(self.tab_quiz, text="Quiz")
        self.notebook.add(self.tab_db, text="Database")
        self.notebook.add(self.tab_stats, text="Statistics")

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        self.setup_add_tab()
        self.setup_quiz_tab()
        self.setup_db_tab()
        self.setup_stats_tab()

    def get_current_pair_data(self):
        return self.db_manager.data["users"][self.current_user][self.current_pair]

    def on_tab_change(self, event):
        selected_tab = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab == "Database":
            self.refresh_database_table()
        elif selected_tab == "Quiz":
            self.load_quiz_word()
        elif selected_tab == "Statistics":
            self.refresh_statistics()

    # --- TAB 1: ADD WORD & LOOKUP ---
    def setup_add_tab(self):
        pair_data = self.get_current_pair_data()
        k_name, t_name = self.current_pair.split(" -> ")

        # Direct Selection
        radio_frame = ttk.Frame(self.tab_add)
        radio_frame.pack(fill="x", pady=5)
        ttk.Label(radio_frame, text="I am typing in:").pack(side="left", padx=5)

        self.lookup_src_var = tk.StringVar(value="known")
        ttk.Radiobutton(radio_frame, text=k_name, variable=self.lookup_src_var, value="known").pack(side="left", padx=5)
        ttk.Radiobutton(radio_frame, text=t_name, variable=self.lookup_src_var, value="target").pack(side="left", padx=5)

        # Search Bar
        search_frame = ttk.Frame(self.tab_add)
        search_frame.pack(fill="x", pady=10)

        self.lookup_entry = ttk.Entry(search_frame, font=("Helvetica", 12))
        self.lookup_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.lookup_entry.bind("<Return>", lambda event: self.perform_lookup())

        self.btn_search = ttk.Button(search_frame, text="Search Online", command=self.perform_lookup)
        self.btn_search.pack(side="right")

        # Results Frame
        self.res_frame = ttk.LabelFrame(self.tab_add, text=" Word Entry (Editable) ", padding="15")
        self.res_frame.pack(fill="both", expand=True, pady=10)

        ttk.Label(self.res_frame, text="Foreign Word (Primary Key):").grid(row=0, column=0, sticky="w", pady=2)
        self.res_word_entry = ttk.Entry(self.res_frame, width=50, font=("Helvetica", 10, "bold"))
        self.res_word_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(self.res_frame, text="Translations (comma-separated):").grid(row=2, column=0, sticky="w", pady=2)
        self.res_trans_entry = ttk.Entry(self.res_frame, width=50)
        self.res_trans_entry.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(self.res_frame, text="Example Sentences (one per line):").grid(row=4, column=0, sticky="w", pady=2)
        self.res_sent_text = tk.Text(self.res_frame, height=4, width=50)
        self.res_sent_text.grid(row=5, column=0, sticky="ew", pady=(0, 10))

        ttk.Button(self.res_frame, text="Approve & Save to Database", command=self.approve_word).grid(row=6, column=0, sticky="e")

        self.res_frame.columnconfigure(0, weight=1)

    def perform_lookup(self):
        query = self.lookup_entry.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Enter a word to search.")
            return

        pair_data = self.get_current_pair_data()
        src_mode = self.lookup_src_var.get()

        if src_mode == "known":
            src_lang, dest_lang = pair_data["known_code"], pair_data["target_code"]
        else:
            src_lang, dest_lang = pair_data["target_code"], pair_data["known_code"]

        self.btn_search.config(state="disabled", text="Searching...")
        self.update_idletasks()

        try:
            lang_pair = f"{src_lang}|{dest_lang}"
            url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(query)}&langpair={lang_pair}"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))

            if res_data.get("responseStatus") != 200:
                raise Exception("API error")

            trans_text = res_data["responseData"]["translatedText"]
            sentences = []

            if src_mode == "known":
                foreign_word = trans_text
                translations = [query]
            else:
                foreign_word = query
                translations = [trans_text]

            # Extract sentence matches
            for match in res_data.get("matches", []):
                segment = match.get("segment", "")
                translation = match.get("translation", "")
                sentence = translation if src_mode == "known" else segment
                if sentence and sentence.lower() != foreign_word.lower() and len(sentence) > 10:
                    sentences.append(sentence)

            # Deduplicate & cap sentences
            sentences = list(dict.fromkeys(sentences))[:3]

            # Update Fields
            self.res_word_entry.delete(0, tk.END)
            self.res_word_entry.insert(0, foreign_word)

            self.res_trans_entry.delete(0, tk.END)
            self.res_trans_entry.insert(0, ", ".join(translations))

            self.res_sent_text.delete("1.0", tk.END)
            self.res_sent_text.insert("1.0", "\n".join(sentences))

        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch online translation: {e}")
        finally:
            self.btn_search.config(state="normal", text="Search Online")

    def approve_word(self):
        foreign_word = self.res_word_entry.get().strip()
        trans_str = self.res_trans_entry.get().strip()
        sent_str = self.res_sent_text.get("1.0", tk.END).strip()

        if not foreign_word or not trans_str:
            messagebox.showwarning("Warning", "Both Foreign Word and Translations are required.")
            return

        words_db = self.get_current_pair_data()["words"]

        if foreign_word in words_db:
            messagebox.showwarning("Warning", f"'{foreign_word}' already exists in database.")
            return

        translations = [t.strip() for t in trans_str.split(",") if t.strip()]
        sentences = [s.strip() for s in sent_str.split("\n") if s.strip()]

        words_db[foreign_word] = {
            "translations": translations,
            "sentences": sentences,
            "attempts": 0,
            "successes": 0,
            "learned": False
        }

        self.db_manager.save_data()
        messagebox.showinfo("Success", f"Word '{foreign_word}' successfully added to database!")

        # Clear UI
        self.lookup_entry.delete(0, tk.END)
        self.res_word_entry.delete(0, tk.END)
        self.res_trans_entry.delete(0, tk.END)
        self.res_sent_text.delete("1.0", tk.END)

    # --- TAB 2: QUIZ ---
    def setup_quiz_tab(self):
        # Direction Selector
        dir_frame = ttk.Frame(self.tab_quiz)
        dir_frame.pack(fill="x", pady=5)

        ttk.Label(dir_frame, text="Quiz Direction:").pack(side="left", padx=5)
        self.dir_var = tk.StringVar(value="foreign_to_native")
        
        ttk.Radiobutton(dir_frame, text="Foreign -> My Language", variable=self.dir_var, 
                        value="foreign_to_native", command=self.load_quiz_word).pack(side="left", padx=5)
        ttk.Radiobutton(dir_frame, text="My Language -> Foreign", variable=self.dir_var, 
                        value="native_to_foreign", command=self.load_quiz_word).pack(side="left", padx=5)

        # Card Display Area
        self.card_frame = ttk.LabelFrame(self.tab_quiz, text=" Flashcard ", padding="20")
        self.card_frame.pack(fill="both", expand=True, pady=10)

        self.prompt_label = ttk.Label(self.card_frame, text="", font=("Helvetica", 22, "bold"), anchor="center")
        self.prompt_label.pack(pady=15)

        self.answer_entry = ttk.Entry(self.card_frame, font=("Helvetica", 14), justify="center")
        self.answer_entry.pack(pady=10, ipady=4)
        self.answer_entry.bind("<Return>", lambda e: self.check_quiz_answer())

        self.feedback_label = ttk.Label(self.card_frame, text="", font=("Helvetica", 11), wraplength=500, justify="center")
        self.feedback_label.pack(pady=10)

        self.btn_check = ttk.Button(self.card_frame, text="Check Answer", command=self.check_quiz_answer)
        self.btn_check.pack(pady=5)

        self.btn_next = ttk.Button(self.card_frame, text="Next Word", command=self.load_quiz_word)

    def load_quiz_word(self):
        words_db = self.get_current_pair_data()["words"]
        unlearned = [w for w, data in words_db.items() if not data.get("learned", False)]

        self.feedback_label.config(text="")
        self.answer_entry.delete(0, tk.END)
        self.answer_entry.config(state="normal")
        self.btn_check.pack(pady=5)
        self.btn_next.pack_forget()

        if not unlearned:
            self.current_quiz_word = None
            self.prompt_label.config(text="No active words available!")
            self.answer_entry.config(state="disabled")
            self.btn_check.config(state="disabled")
            return

        self.btn_check.config(state="normal")
        self.current_quiz_word = random.choice(unlearned)
        word_data = words_db[self.current_quiz_word]

        if self.dir_var.get() == "foreign_to_native":
            self.prompt_label.config(text=self.current_quiz_word)
        else:
            first_trans = word_data["translations"][0] if word_data["translations"] else "N/A"
            self.prompt_label.config(text=first_trans)
        
        self.answer_entry.focus()

    def check_quiz_answer(self):
        if not self.current_quiz_word:
            return

        user_input = self.answer_entry.get().strip().lower()
        if not user_input:
            return

        words_db = self.get_current_pair_data()["words"]
        word_data = words_db[self.current_quiz_word]

        word_data["attempts"] = word_data.get("attempts", 0) + 1

        is_correct = False
        if self.dir_var.get() == "foreign_to_native":
            valid_answers = [t.lower() for t in word_data["translations"]]
            is_correct = user_input in valid_answers
        else:
            is_correct = (user_input == self.current_quiz_word.lower())

        if is_correct:
            word_data["successes"] = word_data.get("successes", 0) + 1
            fb_text = "Correct!\n"
        else:
            fb_text = "Incorrect.\n"

        fb_text += f"Foreign: {self.current_quiz_word}\n"
        fb_text += f"Translations: {', '.join(word_data['translations'])}\n"
        if word_data.get("sentences"):
            fb_text += f"Example: {word_data['sentences'][0]}"

        self.db_manager.save_data()

        self.feedback_label.config(text=fb_text, foreground="green" if is_correct else "red")
        self.answer_entry.config(state="disabled")
        self.btn_check.pack_forget()
        self.btn_next.pack(pady=5)

    # --- TAB 3: DATABASE TABLE ---
    def setup_db_tab(self):
        columns = ("word", "translations", "sentences", "attempts", "success_rate", "status")
        self.tree = ttk.Treeview(self.tab_db, columns=columns, show="headings")

        self.tree.heading("word", text="Foreign Word")
        self.tree.heading("translations", text="Translations")
        self.tree.heading("sentences", text="Example Sentence")
        self.tree.heading("attempts", text="Attempts")
        self.tree.heading("success_rate", text="Success Rate")
        self.tree.heading("status", text="Status")

        self.tree.column("word", width=120)
        self.tree.column("translations", width=180)
        self.tree.column("sentences", width=250)
        self.tree.column("attempts", width=70, anchor="center")
        self.tree.column("success_rate", width=90, anchor="center")
        self.tree.column("status", width=90, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tab_db, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Context Menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Mark as Learned", command=self.context_mark_learned)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete Word", command=self.context_delete_word)

        self.tree.bind("<Button-3>", self.show_context_menu) # Right click Windows/Linux
        self.tree.bind("<Button-2>", self.show_context_menu) # Right click macOS

        # Style tag for learned rows
        self.tree.tag_configure("learned", background="#d1e7dd")

    def refresh_database_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        words_db = self.get_current_pair_data()["words"]

        for word, data in words_db.items():
            attempts = data.get("attempts", 0)
            successes = data.get("successes", 0)
            rate_str = f"{round((successes / attempts) * 100)}%" if attempts > 0 else "-"
            status_str = "Learned" if data.get("learned") else "Learning"
            sentences_str = data["sentences"][0] if data.get("sentences") else "-"
            trans_str = ", ".join(data.get("translations", []))

            tags = ("learned",) if data.get("learned") else ()

            self.tree.insert("", "end", iid=word, values=(
                word, trans_str, sentences_str, attempts, rate_str, status_str
            ), tags=tags)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.selected_word_ctx = item
            self.context_menu.post(event.x_root, event.y_root)

    def context_mark_learned(self):
        if hasattr(self, 'selected_word_ctx'):
            words_db = self.get_current_pair_data()["words"]
            if self.selected_word_ctx in words_db:
                words_db[self.selected_word_ctx]["learned"] = True
                self.db_manager.save_data()
                self.refresh_database_table()

    def context_delete_word(self):
        if hasattr(self, 'selected_word_ctx'):
            words_db = self.get_current_pair_data()["words"]
            if self.selected_word_ctx in words_db:
                del words_db[self.selected_word_ctx]
                self.db_manager.save_data()
                self.refresh_database_table()

    # --- TAB 4: STATISTICS ---
    def setup_stats_tab(self):
        # Summary Cards
        cards_frame = ttk.Frame(self.tab_stats)
        cards_frame.pack(fill="x", pady=10)

        self.card_total = ttk.LabelFrame(cards_frame, text=" Total Guesses ", padding="15")
        self.card_total.pack(side="left", fill="both", expand=True, padx=5)
        self.lbl_total = ttk.Label(self.card_total, text="0", font=("Helvetica", 20, "bold"))
        self.lbl_total.pack()

        self.card_rate = ttk.LabelFrame(cards_frame, text=" Overall Success ", padding="15")
        self.card_rate.pack(side="left", fill="both", expand=True, padx=5)
        self.lbl_rate = ttk.Label(self.card_rate, text="0%", font=("Helvetica", 20, "bold"))
        self.lbl_rate.pack()

        self.card_learned = ttk.LabelFrame(cards_frame, text=" Learned Words ", padding="15")
        self.card_learned.pack(side="left", fill="both", expand=True, padx=5)
        self.lbl_learned = ttk.Label(self.card_learned, text="0", font=("Helvetica", 20, "bold"))
        self.lbl_learned.pack()

        # Hardest Words Section
        hard_frame = ttk.LabelFrame(self.tab_stats, text=" Top 5 Hardest Words (Randomized Tie-Breaker) ", padding="15")
        hard_frame.pack(fill="both", expand=True, pady=10)

        self.hard_listbox = tk.Listbox(hard_frame, font=("Helvetica", 11), borderwidth=0, highlightthickness=0)
        self.hard_listbox.pack(fill="both", expand=True)

    def refresh_statistics(self):
        words_db = self.get_current_pair_data()["words"]

        total_attempts = 0
        total_successes = 0
        learned_count = 0
        candidates = []

        for word, data in words_db.items():
            att = data.get("attempts", 0)
            succ = data.get("successes", 0)
            total_attempts += att
            total_successes += succ
            if data.get("learned"):
                learned_count += 1
            
            failures = att - succ
            if att > 0:
                candidates.append({"word": word, "failures": failures})

        overall_rate = round((total_successes / total_attempts) * 100) if total_attempts > 0 else 0

        self.lbl_total.config(text=str(total_attempts))
        self.lbl_rate.config(text=f"{overall_rate}%")
        self.lbl_learned.config(text=str(learned_count))

        # Tie breaking for top 5 hardest words
        self.hard_listbox.delete(0, tk.END)

        if not candidates:
            self.hard_listbox.insert(tk.END, "No attempt data recorded yet.")
            return

        candidates.sort(key=lambda x: x["failures"], reverse=True)

        top_5 = []
        if len(candidates) <= 5:
            top_5 = candidates
        else:
            threshold = candidates[4]["failures"]
            guaranteed = [w for w in candidates if w["failures"] > threshold]
            ties = [w for w in candidates if w["failures"] == threshold]
            
            random.shuffle(ties)
            top_5 = (guaranteed + ties)[:5]

        for idx, item in enumerate(top_5, 1):
            self.hard_listbox.insert(tk.END, f"{idx}.  {item['word']}  —  {item['failures']} Failed Attempts")

# --- ENTRY POINT ---
if __name__ == "__main__":
    app = LinguaKeyApp()
    app.mainloop()
