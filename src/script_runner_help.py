"""Scrollable command-help window for the Script Runner."""

import tkinter as tk


def show_commands_help(root, editor, status):
    """Show a scrollable help window with insertable command examples."""
    window = tk.Toplevel(root)
    window.title("Commandes disponibles")
    window.geometry("700x620")
    window.minsize(560, 420)
    window.configure(bg="#202124")
    window.transient(root)

    tk.Label(
        window, text="Commandes disponibles",
        font=("Segoe UI", 16, "bold"), bg="#202124", fg="white"
    ).pack(anchor="w", padx=16, pady=(14, 4))

    tk.Label(
        window,
        text="Une commande par ligne. Les lignes commençant par # sont ignorées.",
        font=("Segoe UI", 9), bg="#202124", fg="#bdbdbd"
    ).pack(anchor="w", padx=16, pady=(0, 10))

    container = tk.Frame(window, bg="#202124")
    container.pack(fill="both", expand=True, padx=12, pady=(0, 8))

    canvas = tk.Canvas(container, bg="#202124", highlightthickness=0, borderwidth=0)
    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    content = tk.Frame(canvas, bg="#202124")
    content_window = canvas.create_window((0, 0), window=content, anchor="nw")

    def update_scroll_region(_event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def resize_content(event):
        canvas.itemconfigure(content_window, width=event.width)

    content.bind("<Configure>", update_scroll_region)
    canvas.bind("<Configure>", resize_content)

    entries = [
        ("Exécuter une macro", 'JOUER "Exo 1"',
         "Lance la macro dont le nom correspond exactement à celui enregistré."),
        ("Répéter une macro", 'JOUER "Skip" * 5',
         "Lance la macro Skip cinq fois. Le nombre doit être un entier supérieur ou égal à 1."),
        ("Attendre", "ATTENDRE 2",
         "Attend deux secondes. Les nombres décimaux sont acceptés, par exemple ATTENDRE 0.5."),
        ("Capture d'écran nommée", 'SCREENSHOT "Checkpoint"',
         "Enregistre une capture d'écran avec le nom Checkpoint."),
        ("Capture d'écran sans nom", "SCREENSHOT",
         "Enregistre une capture d'écran avec le nom automatique « Capture »."),
        ("Commentaire", "# Préparation de la prochaine étape",
         "Les lignes commençant par # et les lignes vides sont ignorées."),
    ]

    def insert_command(command):
        editor.insert(tk.INSERT, command + "\n")
        editor.focus_set()
        status.set(f"Commande insérée : {command.split(' ', 1)[0]}")

    for title, example, description in entries:
        card = tk.Frame(content, bg="#303134")
        card.pack(fill="x", padx=4, pady=5)

        tk.Label(
            card, text=title, font=("Segoe UI", 10, "bold"),
            bg="#303134", fg="#8ab4f8"
        ).pack(anchor="w", padx=10, pady=(7, 0))

        tk.Label(
            card, text=example, font=("Consolas", 10),
            bg="#202124", fg="white", anchor="w", padx=8, pady=6
        ).pack(fill="x", padx=10, pady=(4, 3))

        tk.Label(
            card, text=description, font=("Segoe UI", 9),
            bg="#303134", fg="#e0e0e0", anchor="w", justify="left",
            wraplength=600
        ).pack(fill="x", padx=10, pady=(0, 5))

        tk.Button(
            card, text="Insérer",
            command=lambda cmd=example: insert_command(cmd)
        ).pack(anchor="e", padx=10, pady=(0, 7))

    def on_mousewheel(event):
        if getattr(event, "delta", 0):
            canvas.yview_scroll(int(-event.delta / 120), "units")

    canvas.bind("<MouseWheel>", on_mousewheel)
    content.bind("<MouseWheel>", on_mousewheel)

    def on_key_scroll(event):
        if event.keysym == "Down":
            canvas.yview_scroll(1, "units")
        elif event.keysym == "Up":
            canvas.yview_scroll(-1, "units")
        elif event.keysym == "Next":
            canvas.yview_scroll(1, "pages")
        elif event.keysym == "Prior":
            canvas.yview_scroll(-1, "pages")
        elif event.keysym == "Home":
            canvas.yview_moveto(0)
        elif event.keysym == "End":
            canvas.yview_moveto(1)

    for key in ("<Down>", "<Up>", "<Next>", "<Prior>", "<Home>", "<End>"):
        window.bind(key, on_key_scroll)

    tk.Button(window, text="Fermer", command=window.destroy, width=12).pack(
        anchor="e", padx=16, pady=(0, 12)
    )
