import os
from tkinter import filedialog, messagebox
import mysql.connector
import ttkbootstrap as tb
from ttkbootstrap import Window

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from asfalistiria import build_asfalistiria_section
from database import connect, initialize_database
from import_csv.company1 import import_company1, load_covers
from import_csv.company2 import import_company2
from management_section import build_management_section


def _parse_optional_float(value: str, field_label: str):
    cleaned = value.strip().replace(",", ".")
    if cleaned == "":
        return None
    try:
        return float(cleaned)
    except ValueError:
        raise ValueError(f"Το πεδίο '{field_label}' πρέπει να είναι έγκυρος αριθμός.")


def _parse_optional_int(value: str, field_label: str):
    cleaned = value.strip()
    if cleaned == "":
        return None
    try:
        return int(cleaned)
    except ValueError:
        raise ValueError(f"Το πεδίο '{field_label}' πρέπει να είναι ακέραιος αριθμός.")


def _parse_optional_str(value: str):
    cleaned = value.strip()
    return cleaned if cleaned != "" else None


def build_insert_section(parent, db, cursor):
    canvas = tb.Canvas(parent)
    scrollbar = tb.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = tb.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
    )

    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    def _on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)

    canvas.bind("<Configure>", _on_canvas_configure)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_scroll(_event):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

    def _unbind_scroll(_event):
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")

    canvas.bind("<Enter>", _bind_scroll)
    canvas.bind("<Leave>", _unbind_scroll)

    frame = tb.Labelframe(
        scrollable_frame, text="Καταχώρηση Συμβολαίου", padding=10, bootstyle="success"
    )
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    labels = [
        "Αρ. Παραστατικού", "Αρ. Συμβολαίου", "Έναρξη", "Λήξη", "Πάροχος",
        "Πακέτο", "Τύπος", "Καλύψεις", "Μικτά",
        "Όνομα", "Επώνυμο", "Διεύθυνση", "ΑΦΜ", "Τηλέφωνο", "Συνεργάτης", "Σχόλια",
        "Πινακίδα", "Μάρκα", "Μοντέλο", "Κατηγορία", "Ίπποι", "Είδος", "Προμήθειες", "Καθαρά",
    ]

    entries = {}
    for i, label in enumerate(labels):
        tb.Label(frame, text=label + ":").grid(row=i, column=0, sticky="e", padx=5, pady=2)

        if label == "Καλύψεις":
            frame_text = tb.Frame(frame)
            frame_text.grid(row=i, column=1, sticky="ew", pady=2)
            frame.columnconfigure(1, weight=1)

            text_widget = tb.Text(frame_text, width=50, height=7, wrap="word")
            text_widget.pack(side="left", fill="both", expand=True)

            text_scrollbar = tb.Scrollbar(frame_text, command=text_widget.yview)
            text_scrollbar.pack(side="right", fill="y")

            text_widget.config(yscrollcommand=text_scrollbar.set)
            entries[label] = text_widget
        else:
            entry = tb.Entry(frame, width=40)
            entry.grid(row=i, column=1, sticky="w", pady=2)
            entries[label] = entry

    def insert():
        raw_values = []
        for label in labels:
            widget = entries[label]
            if isinstance(widget, tb.Text):
                raw_values.append(widget.get("1.0", "end-1c"))
            else:
                raw_values.append(widget.get())

        arithmos_parastatikou = raw_values[0].strip()
        if not arithmos_parastatikou:
            messagebox.showerror("Σφάλμα", "Ο αριθμός παραστατικού είναι υποχρεωτικός.")
            return

        try:
            values = [
                arithmos_parastatikou,
                _parse_optional_str(raw_values[1]),   # arithmos
                _parse_optional_str(raw_values[2]),   # enarxi (YYYY-MM-DD)
                _parse_optional_str(raw_values[3]),   # lixi (YYYY-MM-DD)
                _parse_optional_str(raw_values[4]),   # paroxos
                _parse_optional_str(raw_values[5]),   # paketo
                _parse_optional_str(raw_values[6]),   # typos
                _parse_optional_str(raw_values[7]),   # kalypseis
                _parse_optional_float(raw_values[8], "Μικτά"),
                _parse_optional_str(raw_values[9]),   # onoma
                _parse_optional_str(raw_values[10]),  # epwnymo
                _parse_optional_str(raw_values[11]),  # topos / address
                _parse_optional_str(raw_values[12]),  # afm
                _parse_optional_str(raw_values[13]),  # tilefono
                _parse_optional_str(raw_values[14]),  # synergatis
                _parse_optional_str(raw_values[15]),  # sxolia
                _parse_optional_str(raw_values[16]),  # pinakida
                _parse_optional_str(raw_values[17]),  # marka
                _parse_optional_str(raw_values[18]),  # modelo
                _parse_optional_str(raw_values[19]),  # kathgoria
                _parse_optional_int(raw_values[20], "Ίπποι"),
                _parse_optional_str(raw_values[21]),  # eidos
                _parse_optional_float(raw_values[22], "Προμήθειες"),
                _parse_optional_float(raw_values[23], "Καθαρά"),
            ]
        except ValueError as err:
            messagebox.showerror("Σφάλμα", str(err))
            return

        try:
            cursor.execute(
                """
                INSERT INTO sumbolaia (
                    arithmos_parastatikou, arithmos, enarxi, lixi, paroxos, paketo, typos, kalypseis, mikta,
                    onoma, epwnymo, topos, afm, tilefono, synergatis, sxolia,
                    pinakida, marka, modelo, kathgoria, ippoi, eidos, promitheies, kathara
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                values,
            )
            db.commit()
            messagebox.showinfo("Επιτυχία", "Το συμβόλαιο καταχωρήθηκε.")
            for widget in entries.values():
                if isinstance(widget, tb.Text):
                    widget.delete("1.0", "end")
                else:
                    widget.delete(0, "end")

        except mysql.connector.IntegrityError:
            messagebox.showerror(
                "Σφάλμα",
                "Υπάρχει ήδη συμβόλαιο με αυτόν τον αριθμό παραστατικού (PRIMARY KEY).",
            )
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Αποτυχία: {e}")

    tb.Button(frame, text="Καταχώρηση", command=insert, bootstyle="success").grid(
        row=len(labels), column=0, columnspan=2, pady=10
    )


def start_gui(theme="flatly"):
    initialize_database()
    db = connect()
    cursor = db.cursor()

    window = Window(themename=theme)
    window.title("Ασφαλιστική Εφαρμογή")
    window.geometry("700x800")

    def on_close():
        try:
            cursor.close()
            db.close()
        finally:
            window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_close)

    notebook = tb.Notebook(window)
    notebook.pack(fill="both", expand=True)

    tab_insert = tb.Frame(notebook)
    notebook.add(tab_insert, text="Καταχώρηση Συμβολαίου")
    build_insert_section(tab_insert, db, cursor)

    tab_management = tb.Frame(notebook)
    notebook.add(tab_management, text="Διαχείριση")
    build_management_section(tab_management, db, cursor)

    tab_asfalistiria = tb.Frame(notebook)
    notebook.add(tab_asfalistiria, text="Ασφαλιστήρια")
    build_asfalistiria_section(tab_asfalistiria, db, cursor)

    tab_import = tb.Frame(notebook)
    notebook.add(tab_import, text="Εισαγωγή Αρχείων")

    def import_from_company1():
        filepaths = filedialog.askopenfilenames(
            title="Επιλέξτε αρχεία company1",
            filetypes=[("CSV files", "*.csv")],
        )
        if not filepaths:
            return

        covers = {}
        for filepath in filepaths:
            if "covers" in os.path.basename(filepath).lower():
                file_covers = load_covers(filepath)
                for k, v in file_covers.items():
                    covers[k] = f"{covers[k]}; {v}" if k in covers else v

        imported_count = 0
        for filepath in filepaths:
            if "covers" in os.path.basename(filepath).lower():
                continue
            try:
                import_company1(filepath, covers, db=db, cursor=cursor)
                imported_count += 1
            except Exception as e:
                messagebox.showerror(
                    "Σφάλμα", f"Αποτυχία εισαγωγής {os.path.basename(filepath)}: {e}"
                )

        if imported_count > 0:
            messagebox.showinfo(
                "Επιτυχία", f"Εισήχθησαν επιτυχώς {imported_count} αρχεία company1 στη βάση."
            )

    def import_from_company2():
        filepaths = filedialog.askopenfilenames(
            title="Επιλέξτε αρχεία company2",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt")],
        )
        if not filepaths:
            return

        imported_count = 0
        for filepath in filepaths:
            try:
                import_company2(filepath, db=db, cursor=cursor)
                imported_count += 1
            except Exception as e:
                messagebox.showerror(
                    "Σφάλμα", f"Αποτυχία εισαγωγής {os.path.basename(filepath)}: {e}"
                )

        if imported_count > 0:
            messagebox.showinfo(
                "Επιτυχία", f"Εισήχθησαν επιτυχώς {imported_count} αρχεία company2."
            )

    tb.Button(
        tab_import, text="Company 1", command=import_from_company1, bootstyle="primary"
    ).pack(pady=20)
    tb.Separator(tab_import).pack(fill="x", pady=10)
    tb.Button(
        tab_import, text="Company 2", command=import_from_company2, bootstyle="success"
    ).pack(pady=10)

    def toggle_theme():
        current_theme = window.style.theme_use()
        new_theme = "flatly" if current_theme == "darkly" else "darkly"
        window.style.theme_use(new_theme)

    tb.Button(
        window, text="Εναλλαγή Θέματος", command=toggle_theme, bootstyle="secondary"
    ).pack(side="bottom", pady=5)

    window.mainloop()


if __name__ == "__main__":
    start_gui()