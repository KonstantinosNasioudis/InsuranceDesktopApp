from datetime import date
from tkinter import Toplevel, messagebox
import ttkbootstrap as tb


CLIENT_FIELDS = {"onoma", "epwnymo", "address", "afm", "tilefono"}

COL_LABELS = {
    "arithmos_parastatikou": "Αρ. Παραστατικού",
    "arithmos": "Αριθμός",
    "enarxi": "Έναρξη",
    "lixi": "Λήξη",
    "paroxos": "Πάροχος",
    "paketo": "Πακέτο",
    "typos": "Τύπος",
    "kalypseis": "Καλύψεις",
    "mikta": "Μικτά",
    "onoma": "Όνομα",
    "epwnymo": "Επώνυμο",
    "address": "Τόπος",
    "afm": "ΑΦΜ",
    "tilefono": "Τηλέφωνο",
    "synergatis": "Συνεργάτης",
    "sxolia": "Σχόλια",
    "pinakida": "Πινακίδα",
    "marka": "Μάρκα",
    "modelo": "Μοντέλο",
    "kathgoria": "Κατηγορία",
    "ippoi": "Ίπποι",
    "eidos": "Είδος",
    "promitheies": "Προμήθειες",
    "kathara": "Καθαρά",
}

SELECT_COLUMNS = ", ".join(COL_LABELS.keys())


def greeklish_to_greek(text: str) -> str:
    text = text.lower()

    replacements = {
        "th": "θ",
        "ks": "ξ",
        "ps": "ψ",
        "ch": "χ",
        "mp": "μπ",
        "nt": "ντ",
        "gk": "γκ",
    }
    for eng, gr in replacements.items():
        text = text.replace(eng, gr)

    mapping = {
        "a": "α",
        "b": "β",
        "g": "γ",
        "d": "δ",
        "e": "ε",
        "z": "ζ",
        "h": "η",
        "i": "ι",
        "k": "κ",
        "l": "λ",
        "m": "μ",
        "n": "ν",
        "o": "ο",
        "p": "π",
        "r": "ρ",
        "s": "σ",
        "t": "τ",
        "y": "υ",
        "f": "φ",
        "x": "χ",
        "w": "ω",
    }
    for eng, gr in mapping.items():
        text = text.replace(eng, gr)

    return text


def normalize_plate(text: str) -> str:
    mapping = {
        "Α": "A",
        "Β": "B",
        "Ε": "E",
        "Ζ": "Z",
        "Η": "H",
        "Ι": "I",
        "Κ": "K",
        "Μ": "M",
        "Ν": "N",
        "Ο": "O",
        "Ρ": "P",
        "Τ": "T",
        "Υ": "Y",
        "Χ": "X",
    }
    text = text.upper()
    for gr, en in mapping.items():
        text = text.replace(gr, en)
    return text


def _create_scrollable_container(parent):
    canvas = tb.Canvas(parent)
    scrollbar = tb.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scroll_frame = tb.Frame(canvas)
    canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

    scroll_frame.bind(
        "<Configure>",
        lambda _e: canvas.configure(scrollregion=canvas.bbox("all")),
    )
    canvas.bind(
        "<Configure>",
        lambda e: canvas.itemconfig(canvas_window, width=e.width),
    )
    canvas.configure(yscrollcommand=scrollbar.set)
    return canvas, scrollbar, scroll_frame


def build_management_section(parent, db, cursor):
    frame = tb.Frame(parent)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    search_var = tb.StringVar()
    tb.Label(frame, text="Αναζήτηση (Όνομα / Πινακίδα):").grid(row=0, column=0, sticky="w")
    search_box = tb.Combobox(frame, textvariable=search_var, width=30)
    search_box.grid(row=0, column=1, sticky="w", pady=5)

    def refresh_search_options():
        cursor.execute(
            "SELECT CONCAT(COALESCE(onoma, ''), ' ', COALESCE(epwnymo, '')), pinakida "
            "FROM sumbolaia ORDER BY epwnymo, onoma"
        )
        rows = cursor.fetchall()
        options = []
        for full_name, plate in rows:
            clean_name = full_name.strip() if full_name else ""
            if clean_name and clean_name not in options:
                options.append(clean_name)
            if plate and plate not in options:
                options.append(plate)
        return options

    all_options = refresh_search_options()
    search_box["values"] = all_options

    def on_keyrelease(_event):
        value = search_var.get().strip().lower()
        search_box["values"] = (
            [opt for opt in all_options if value in opt.lower()] if value else all_options
        )

    search_box.bind("<KeyRelease>", on_keyrelease)

    date_frame = tb.Frame(frame)
    date_frame.grid(row=1, column=0, columnspan=5, sticky="w", pady=5)

    months_gr = [
        "Ιανουάριος", "Φεβρουάριος", "Μάρτιος", "Απρίλιος", "Μάιος", "Ιούνιος",
        "Ιούλιος", "Αύγουστος", "Σεπτέμβριος", "Οκτώβριος", "Νοέμβριος", "Δεκέμβριος",
    ]

    current_year = date.today().year
    current_month = date.today().month

    tb.Label(date_frame, text="Μήνας Λήξης:").pack(side="left", padx=5)
    month_var = tb.StringVar(value=months_gr[current_month - 1])
    month_box = tb.Combobox(date_frame, textvariable=month_var, width=12, values=months_gr)
    month_box.pack(side="left", padx=5)

    tb.Label(date_frame, text="Έτος:").pack(side="left", padx=20)
    year_var = tb.IntVar(value=current_year)
    year_box = tb.Combobox(
        date_frame,
        textvariable=year_var,
        width=6,
        values=[y for y in range(current_year - 2, current_year + 3)],
    )
    year_box.pack(side="left", padx=5)

    canvas, scrollbar, scrollable_frame = _create_scrollable_container(frame)
    canvas.grid(row=2, column=0, columnspan=5, sticky="nsew")
    scrollbar.grid(row=2, column=5, sticky="ns")
    frame.grid_rowconfigure(2, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    def clear_results():
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

    def edit_record(row):
        record_id = row[0]
        edit_win = Toplevel(frame)
        edit_win.title(f"Επεξεργασία Συμβολαίου: {record_id}")

        edit_canvas, edit_scrollbar, scroll_frame = _create_scrollable_container(edit_win)
        edit_canvas.pack(side="left", fill="both", expand=True)
        edit_scrollbar.pack(side="right", fill="y")
        scroll_frame.columnconfigure(1, weight=1)

        vars_list = []
        cols = list(COL_LABELS.keys())

        for i, col in enumerate(cols[1:]):
            tb.Label(scroll_frame, text=COL_LABELS[col] + ":").grid(
                row=i, column=0, sticky="e", padx=5, pady=2
            )
            val = "" if row[i + 1] is None else str(row[i + 1])

            if col in ("kalypseis", "sxolia"):
                frame_text = tb.Frame(scroll_frame)
                frame_text.grid(row=i, column=1, sticky="ew", pady=2)

                text_box = tb.Text(frame_text, width=60, height=6, wrap="word")
                text_box.pack(side="left", fill="both", expand=True)

                text_scrollbar = tb.Scrollbar(
                    frame_text, orient="vertical", command=text_box.yview
                )
                text_scrollbar.pack(side="right", fill="y")
                text_box.config(yscrollcommand=text_scrollbar.set)
                text_box.insert("1.0", val)
                vars_list.append(text_box)
            else:
                var = tb.StringVar(value=val)
                tb.Entry(scroll_frame, textvariable=var, width=40).grid(
                    row=i, column=1, sticky="w", pady=2
                )
                vars_list.append(var)

        def save_changes():
            values = {}
            cols_local = list(COL_LABELS.keys())[1:]

            for i, col in enumerate(cols_local):
                if col in ("kalypseis", "sxolia"):
                    raw = vars_list[i].get("1.0", "end-1c").strip()
                else:
                    raw = vars_list[i].get().strip()
                values[col] = raw if raw != "" else None

            old_afm = row[12]
            new_afm = values.get("afm")

            update_client_all = False
            if old_afm:
                update_client_all = messagebox.askyesno(
                    "Ενημέρωση Στοιχείων Πελάτη",
                    "Να ενημερωθούν τα στοιχεία πελάτη (όνομα, επώνυμο, τόπος, τηλέφωνο, ΑΦΜ) "
                    "σε όλα τα συμβόλαια με το ίδιο ΑΦΜ;",
                )

            try:
                if update_client_all:
                    client_updates = {k: v for k, v in values.items() if k in CLIENT_FIELDS}
                    if client_updates:
                        set_clause = ", ".join([f"{c}=%s" for c in client_updates])
                        cursor.execute(
                            f"UPDATE sumbolaia SET {set_clause} WHERE afm=%s",
                            list(client_updates.values()) + [old_afm],
                        )

                    non_client_updates = {
                        k: v for k, v in values.items() if k not in CLIENT_FIELDS
                    }
                    if non_client_updates:
                        set_clause = ", ".join([f"{c}=%s" for c in non_client_updates])
                        cursor.execute(
                            f"UPDATE sumbolaia SET {set_clause} WHERE arithmos_parastatikou=%s",
                            list(non_client_updates.values()) + [record_id],
                        )
                else:
                    set_clause = ", ".join([f"{c}=%s" for c in values])
                    cursor.execute(
                        f"UPDATE sumbolaia SET {set_clause} WHERE arithmos_parastatikou=%s",
                        list(values.values()) + [record_id],
                    )

                db.commit()
                edit_win.destroy()
                load_data(
                    search_var.get().strip(),
                    month_var.get(),
                    year_var.get(),
                    mode="both",
                )
            except Exception as e:
                db.rollback()
                messagebox.showerror("Σφάλμα", str(e))

        tb.Button(edit_win, text="Αποθήκευση", command=save_changes, bootstyle="success").pack(
            pady=10
        )

    def delete_record(row):
        record_id = row[0]
        if messagebox.askyesno("Διαγραφή", "Είσαι σίγουρος ότι θέλεις να διαγραφεί το συμβόλαιο;"):
            try:
                cursor.execute(
                    "DELETE FROM sumbolaia WHERE arithmos_parastatikou=%s", (record_id,)
                )
                db.commit()
                messagebox.showinfo("Διαγραφή", "Η εγγραφή διαγράφηκε.")
                load_data(
                    search_var.get().strip(),
                    month_var.get(),
                    year_var.get(),
                    mode="both",
                )
            except Exception as e:
                db.rollback()
                messagebox.showerror("Σφάλμα", str(e))

    def view_record(r):
        view_win = Toplevel(frame)
        view_win.title(f"Προβολή Συμβολαίου: {r[1] or r[0]}")

        view_canvas, view_scrollbar, scroll_frame = _create_scrollable_container(view_win)
        view_canvas.pack(side="left", fill="both", expand=True)
        view_scrollbar.pack(side="right", fill="y")
        scroll_frame.columnconfigure(1, weight=1)

        cols = list(COL_LABELS.keys())
        for i, col in enumerate(cols):
            label_text = f"{COL_LABELS.get(col, col)}:"
            tb.Label(scroll_frame, text=label_text, anchor="w").grid(
                row=i, column=0, sticky="ne", padx=5, pady=2
            )

            if col in ("kalypseis", "sxolia"):
                frame_text = tb.Frame(scroll_frame)
                frame_text.grid(row=i, column=1, sticky="ew", padx=5, pady=2)

                text = tb.Text(frame_text, width=60, height=6, wrap="word")
                text.pack(side="left", fill="both", expand=True)

                text_scrollbar = tb.Scrollbar(
                    frame_text, orient="vertical", command=text.yview
                )
                text_scrollbar.pack(side="right", fill="y")
                text.config(yscrollcommand=text_scrollbar.set)
                text.insert("1.0", "" if r[i] is None else str(r[i]))
                text.config(state="disabled")
            else:
                display_val = "" if r[i] is None else str(r[i])
                tb.Label(scroll_frame, text=display_val, anchor="w", justify="left").grid(
                    row=i, column=1, sticky="w", padx=5, pady=2
                )

    def load_data(search="", month_name=None, year=None, mode="both"):
        clear_results()

        query = f"SELECT {SELECT_COLUMNS} FROM sumbolaia WHERE 1=1"
        params = []

        if mode in ("search", "both") and search:
            search_input = search.strip()
            greek_version = greeklish_to_greek(search_input)
            normalized_plate = normalize_plate(search_input)

            query += """ AND (
                CONCAT(COALESCE(onoma, ''), ' ', COALESCE(epwnymo, '')) LIKE %s OR
                CONCAT(COALESCE(onoma, ''), ' ', COALESCE(epwnymo, '')) LIKE %s OR
                pinakida LIKE %s
            )"""
            params += [
                f"%{search_input}%",
                f"%{greek_version}%",
                f"%{normalized_plate}%",
            ]

        if mode in ("month", "both") and month_name and year:
            month_num = months_gr.index(month_name) + 1
            query += " AND MONTH(lixi) = %s AND YEAR(lixi) = %s"
            params += [month_num, year]

        query += " ORDER BY lixi ASC"
        cursor.execute(query, params)
        rows = cursor.fetchall()

        if not rows:
            tb.Label(
                scrollable_frame, text="Δεν βρέθηκαν αποτελέσματα.", bootstyle="warning"
            ).pack(pady=10)
            return

        for row in rows:
            record_frame = tb.Labelframe(
                scrollable_frame, text=f"Συμβόλαιο: {row[1] or row[0]}", padding=10
            )
            record_frame.pack(fill="x", padx=5, pady=5, expand=True)

            btn_frame = tb.Frame(record_frame)
            btn_frame.pack(side="right", padx=10, pady=5)

            tb.Button(
                btn_frame,
                text="Προβολή",
                bootstyle="secondary",
                command=lambda r=row: view_record(r),
            ).pack(fill="x", pady=2)
            tb.Button(
                btn_frame,
                text="Επεξεργασία",
                bootstyle="info",
                command=lambda r=row: edit_record(r),
            ).pack(fill="x", pady=2)
            tb.Button(
                btn_frame,
                text="Διαγραφή",
                bootstyle="danger",
                command=lambda r=row: delete_record(r),
            ).pack(fill="x", pady=2)

            tb.Label(
                record_frame,
                text=(
                    f"Όνομα: {row[9] or ''} {row[10] or ''} | Πινακίδα: {row[16] or ''} | "
                    f"Λήξη: {row[3] or ''} | Πάροχος: {row[4] or ''} | Πακέτο: {row[5] or ''}"
                ),
                anchor="w",
                justify="left",
            ).pack(anchor="w")

    tb.Button(
        frame,
        text="Αναζήτηση",
        bootstyle="info",
        command=lambda: load_data(
            search_var.get().strip(), month_var.get(), year_var.get(), mode="search"
        ),
    ).grid(row=0, column=2, padx=5)

    tb.Button(
        frame,
        text="Αναζήτηση ανά Μήνα",
        bootstyle="primary",
        command=lambda: load_data("", month_var.get(), year_var.get(), mode="month"),
    ).grid(row=0, column=3, padx=5)

    tb.Button(
        frame,
        text="Ανανέωση",
        bootstyle="secondary",
        command=lambda: load_data(
            search_var.get().strip(), month_var.get(), year_var.get(), mode="both"
        ),
    ).grid(row=0, column=4, padx=5)