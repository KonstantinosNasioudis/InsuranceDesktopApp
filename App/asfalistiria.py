import os
from datetime import date, datetime
from tkinter import filedialog, messagebox
import pandas as pd
import ttkbootstrap as tb
from ttkbootstrap import DateEntry


def build_asfalistiria_section(parent, db, cursor):
    """
    Κατασκευάζει το tab 'Ασφαλιστήρια'.
    db, cursor: αντικείμενα σύνδεσης στη βάση (mysql.connector).
    """
    frame = tb.Labelframe(parent, text="Ασφαλιστήρια", padding=10, bootstyle="info")
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    tb.Label(frame, text="Από (Ημ. Έναρξης):").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    start_entry = DateEntry(frame, width=15)
    start_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

    tb.Label(frame, text="Έως (Ημ. Έναρξης):").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    end_entry = DateEntry(frame, width=15)
    end_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

    tb.Label(frame, text="Συνεργάτης:").grid(row=0, column=2, sticky="e", padx=5, pady=5)
    partner_combo = tb.Combobox(frame, width=30)
    partner_combo.grid(row=0, column=3, sticky="w", padx=5, pady=5)

    tb.Label(frame, text="Πάροχος:").grid(row=1, column=2, sticky="e", padx=5, pady=5)
    provider_combo = tb.Combobox(frame, width=30)
    provider_combo.grid(row=1, column=3, sticky="w", padx=5, pady=5)

    def load_filter_options():
        current_partner = partner_combo.get() or "<Όλοι>"
        current_provider = provider_combo.get() or "<Όλοι>"
        try:
            cursor.execute(
                "SELECT DISTINCT synergatis FROM sumbolaia "
                "WHERE synergatis IS NOT NULL AND synergatis <> '' ORDER BY synergatis"
            )
            partners = [r[0] for r in cursor.fetchall()]
            partner_values = ["<Όλοι>"] + partners
            partner_combo["values"] = partner_values
            partner_combo.set(
                current_partner if current_partner in partner_values else "<Όλοι>"
            )

            cursor.execute(
                "SELECT DISTINCT paroxos FROM sumbolaia "
                "WHERE paroxos IS NOT NULL AND paroxos <> '' ORDER BY paroxos"
            )
            providers = [r[0] for r in cursor.fetchall()]
            provider_values = ["<Όλοι>"] + providers
            provider_combo["values"] = provider_values
            provider_combo.set(
                current_provider if current_provider in provider_values else "<Όλοι>"
            )
        except Exception as e:
            partner_combo["values"] = ["<Όλοι>"]
            partner_combo.set("<Όλοι>")
            provider_combo["values"] = ["<Όλοι>"]
            provider_combo.set("<Όλοι>")
            print("Προειδοποίηση: Δεν φορτώθηκαν συνεργάτες/πάροχοι:", e)

    load_filter_options()

    totals_frame = tb.Frame(frame)
    totals_frame.grid(row=2, column=0, columnspan=4, sticky="ew", padx=5, pady=8)

    tb.Label(totals_frame, text="Σύνολα:", font=("Helvetica", 10, "bold")).pack(
        side="left", padx=(0, 10)
    )
    lbl_mikta_val = tb.Label(totals_frame, text="Μικτά: 0.00 €", bootstyle="info")
    lbl_mikta_val.pack(side="left", padx=10)
    lbl_kathara_val = tb.Label(totals_frame, text="Καθαρά: 0.00 €", bootstyle="info")
    lbl_kathara_val.pack(side="left", padx=10)
    lbl_promitheies_val = tb.Label(
        totals_frame, text="Προμήθειες: 0.00 €", bootstyle="info"
    )
    lbl_promitheies_val.pack(side="left", padx=10)

    table_frame = tb.Frame(frame)
    table_frame.grid(row=4, column=0, columnspan=4, sticky="nsew", padx=5, pady=5)
    frame.grid_rowconfigure(4, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    columns = (
        "arithmos",
        "pelatis",
        "paroxos",
        "enarxi",
        "lixi",
        "mikta",
        "kathara",
        "promitheies",
        "synergatis",
    )
    tree = tb.Treeview(table_frame, columns=columns, show="headings", height=14)
    tree.pack(side="left", fill="both", expand=True)

    vsb = tb.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=vsb.set)
    vsb.pack(side="right", fill="y")

    headers = {
        "arithmos": "Αρ. Συμβολαίου",
        "pelatis": "Πελάτης",
        "paroxos": "Πάροχος",
        "enarxi": "Έναρξη",
        "lixi": "Λήξη",
        "mikta": "Μικτά (€)",
        "kathara": "Καθαρά (€)",
        "promitheies": "Προμήθειες (€)",
        "synergatis": "Συνεργάτης",
    }
    for col in columns:
        tree.heading(col, text=headers[col])
        tree.column(col, width=110, anchor="center")

    def _format_date(val):
        if not val:
            return ""
        if isinstance(val, (datetime, date)):
            return val.strftime("%Y-%m-%d")
        return str(val)

    def search():
        load_filter_options()
        try:
            start_date = start_entry.get_date()
            end_date = end_entry.get_date()
        except ValueError as ve:
            messagebox.showerror("Σφάλμα", str(ve))
            return

        s_date_raw = start_date.strftime("%Y-%m-%d")
        e_date_raw = end_date.strftime("%Y-%m-%d")

        partner = partner_combo.get()
        provider = provider_combo.get()

        query = """
            SELECT arithmos_parastatikou, arithmos,
                   TRIM(CONCAT(COALESCE(onoma, ''), ' ', COALESCE(epwnymo, ''))) AS pelatis,
                   paroxos, enarxi, lixi, mikta, kathara, promitheies, synergatis
            FROM sumbolaia
            WHERE enarxi BETWEEN %s AND %s
        """
        params = [s_date_raw, e_date_raw]

        if partner and partner != "<Όλοι>":
            query += " AND synergatis = %s"
            params.append(partner)
        if provider and provider != "<Όλοι>":
            query += " AND paroxos = %s"
            params.append(provider)

        try:
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Αποτυχία ερωτήματος στη βάση:\n{e}")
            return

        for item in tree.get_children():
            tree.delete(item)

        total_mikta = total_kathara = total_prom = 0.0
        displayed_rows = []

        for r in rows:
            arithmos = r[1] or r[0] or ""
            pelatis = r[2] or ""
            paroxos = r[3] or ""
            enarxi_str = _format_date(r[4])
            lixi_str = _format_date(r[5])
            mikta = float(r[6] or 0.0)
            kathara = float(r[7] or 0.0)
            promitheies = float(r[8] or 0.0)
            synergatis = r[9] or ""

            tree.insert(
                "",
                "end",
                values=(
                    arithmos,
                    pelatis,
                    paroxos,
                    enarxi_str,
                    lixi_str,
                    f"{mikta:.2f}",
                    f"{kathara:.2f}",
                    f"{promitheies:.2f}",
                    synergatis,
                ),
            )

            total_mikta += mikta
            total_kathara += kathara
            total_prom += promitheies

            displayed_rows.append(
                (
                    arithmos,
                    pelatis,
                    paroxos,
                    enarxi_str,
                    lixi_str,
                    mikta,
                    kathara,
                    promitheies,
                    synergatis,
                )
            )

        lbl_mikta_val.config(text=f"Μικτά: {total_mikta:,.2f} €")
        lbl_kathara_val.config(text=f"Καθαρά: {total_kathara:,.2f} €")
        lbl_promitheies_val.config(text=f"Προμήθειες: {total_prom:,.2f} €")

        tree.data = displayed_rows
        tree.meta = {
            "start": s_date_raw,
            "end": e_date_raw,
            "partner": partner,
            "provider": provider,
        }

    def export_to_excel():
        if not hasattr(tree, "data") or not tree.data:
            messagebox.showwarning("Προσοχή", "Δεν υπάρχουν δεδομένα για εξαγωγή.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Αποθήκευση ως...",
        )
        if not file_path:
            return

        try:
            df = pd.DataFrame(
                tree.data,
                columns=[
                    "Αρ. Συμβολαίου",
                    "Πελάτης",
                    "Πάροχος",
                    "Έναρξη",
                    "Λήξη",
                    "Μικτά (€)",
                    "Καθαρά (€)",
                    "Προμήθειες (€)",
                    "Συνεργάτης",
                ],
            )

            total_mikta = sum(float(row[5]) for row in tree.data)
            total_kathara = sum(float(row[6]) for row in tree.data)
            total_prom = sum(float(row[7]) for row in tree.data)

            totals_row = [
                "Σύνολα",
                "",
                "",
                "",
                "",
                total_mikta,
                total_kathara,
                total_prom,
                "",
            ]
            df_totals = pd.DataFrame([totals_row], columns=df.columns)
            df = pd.concat([df, df_totals], ignore_index=True)

            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                meta = tree.meta if hasattr(tree, "meta") else {}
                filters_df = pd.DataFrame(
                    {
                        "Πεδίο": ["Από", "Έως", "Συνεργάτης", "Πάροχος"],
                        "Τιμή": [
                            meta.get("start", ""),
                            meta.get("end", ""),
                            meta.get("partner", ""),
                            meta.get("provider", ""),
                        ],
                    }
                )
                filters_df.to_excel(writer, sheet_name="Φίλτρα", index=False)
                df.to_excel(writer, sheet_name="Συμβόλαια", index=False)
            messagebox.showinfo(
                "Επιτυχία", f"Η εξαγωγή σε Excel ολοκληρώθηκε:\n{file_path}"
            )
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Αποτυχία εξαγωγής σε Excel:\n{e}")

    def export_to_pdf():
        if not hasattr(tree, "data") or not tree.data:
            messagebox.showwarning("Προσοχή", "Δεν υπάρχουν δεδομένα για εκτύπωση.")
            return

        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.platypus import (
                Image,
                Paragraph,
                SimpleDocTemplate,
                Spacer,
                Table,
                TableStyle,
            )
        except Exception as e:
            messagebox.showerror(
                "Σφάλμα", f"Απαιτείται η βιβλιοθήκη reportlab για PDF.\n{e}"
            )
            return

        try:
            pdfmetrics.registerFont(TTFont("DejaVu", "DejaVuSans.ttf"))
        except Exception as e:
            messagebox.showerror(
                "Σφάλμα", f"Δεν βρέθηκε το font DejaVuSans.ttf.\n{e}"
            )
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Αποθήκευση Αναφοράς ως...",
        )
        if not file_path:
            return

        try:
            page_size = landscape(A4)
            doc = SimpleDocTemplate(
                file_path,
                pagesize=page_size,
                rightMargin=40,
                leftMargin=40,
                topMargin=60,
                bottomMargin=50,
            )
            elements = []
            styles = getSampleStyleSheet()

            title_style = styles["Title"]
            title_style.fontName = "DejaVu"

            normal_style = styles["Normal"]
            normal_style.fontName = "DejaVu"

            logo_path = None
            for ext in ("png", "jpg", "jpeg"):
                if os.path.exists(f"logo.{ext}"):
                    logo_path = f"logo.{ext}"
                    break
            if logo_path:
                elements.append(Image(logo_path, width=100, height=40))
                elements.append(Spacer(1, 6))

            elements.append(Paragraph("<b>ΑΝΑΦΟΡΑ ΣΥΜΒΟΛΑΙΩΝ</b>", title_style))
            elements.append(Spacer(1, 6))

            meta = tree.meta if hasattr(tree, "meta") else {}
            period = f"<b>Περίοδος:</b> {meta.get('start', '')} έως {meta.get('end', '')}"
            filters = (
                f"<b>Συνεργάτης:</b> {meta.get('partner', '<Όλοι>')}  &nbsp;&nbsp;&nbsp; "
                f"<b>Πάροχος:</b> {meta.get('provider', '<Όλοι>')}"
            )
            created = (
                f"<b>Ημερομηνία δημιουργίας:</b> "
                f"{datetime.now().strftime('%d/%m/%Y %H:%M')}"
            )
            elements.append(Paragraph(period, normal_style))
            elements.append(Paragraph(filters, normal_style))
            elements.append(Paragraph(created, normal_style))
            elements.append(Spacer(1, 10))

            headers_pdf = [
                "Αρ. Συμβολαίου",
                "Πελάτης",
                "Πάροχος",
                "Έναρξη",
                "Λήξη",
                "Μικτά (€)",
                "Καθαρά (€)",
                "Προμήθειες (€)",
                "Συνεργάτης",
            ]

            data = [headers_pdf]
            for row in tree.data:
                data.append([Paragraph(str(cell), normal_style) for cell in row])

            total_mikta = sum(float(row[5]) for row in tree.data)
            total_kathara = sum(float(row[6]) for row in tree.data)
            total_prom = sum(float(row[7]) for row in tree.data)

            data.append(
                [
                    Paragraph("<b>Σύνολα</b>", normal_style),
                    "",
                    "",
                    "",
                    "",
                    Paragraph(f"<b>{total_mikta:.2f}</b>", normal_style),
                    Paragraph(f"<b>{total_kathara:.2f}</b>", normal_style),
                    Paragraph(f"<b>{total_prom:.2f}</b>", normal_style),
                    "",
                ]
            )

            col_widths = [70, 150, 100, 60, 60, 60, 60, 70, 100]
            table = Table(data, repeatRows=1, colWidths=col_widths)
            table.setStyle(
                TableStyle(
                    [
                        ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E86C1")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [colors.whitesmoke, colors.lightgrey],
                        ),
                    ]
                )
            )
            elements.append(table)
            elements.append(Spacer(1, 10))

            def add_footer(canvas_obj, doc_obj):
                canvas_obj.saveState()
                canvas_obj.setFont("DejaVu", 8)
                footer_text = (
                    f"Σελίδα {doc_obj.page} | "
                    f"Δημιουργήθηκε: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                )
                canvas_obj.drawCentredString(page_size[0] / 2.0, 15, footer_text)
                canvas_obj.restoreState()

            doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
            messagebox.showinfo(
                "Επιτυχία", f"Η αναφορά PDF δημιουργήθηκε:\n{file_path}"
            )
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Αποτυχία δημιουργίας PDF:\n{e}")

    def clear_filters():
        start_entry.set_date(datetime.today())
        end_entry.set_date(datetime.today())
        partner_combo.set("<Όλοι>")
        provider_combo.set("<Όλοι>")
        for item in tree.get_children():
            tree.delete(item)
        lbl_mikta_val.config(text="Μικτά: 0.00 €")
        lbl_kathara_val.config(text="Καθαρά: 0.00 €")
        lbl_promitheies_val.config(text="Προμήθειες: 0.00 €")
        if hasattr(tree, "data"):
            tree.data = []

    btn_frame = tb.Frame(frame)
    btn_frame.grid(row=3, column=0, columnspan=4, pady=6)

    tb.Button(
        btn_frame, text="Αναζήτηση", command=search, bootstyle="primary"
    ).pack(side="left", padx=6)
    tb.Button(
        btn_frame,
        text="Εξαγωγή σε Excel",
        command=export_to_excel,
        bootstyle="success",
    ).pack(side="left", padx=6)
    tb.Button(
        btn_frame, text="Εκτύπωση σε PDF", command=export_to_pdf, bootstyle="danger"
    ).pack(side="left", padx=6)
    tb.Button(
        btn_frame,
        text="Καθαρισμός Φίλτρων",
        command=clear_filters,
        bootstyle="secondary",
    ).pack(side="left", padx=6)

    def _on_mousewheel(event):
        tree.yview_scroll(int(-1 * (event.delta / 120)), "units")

    tree.bind("<Enter>", lambda _e: tree.bind_all("<MouseWheel>", _on_mousewheel))
    tree.bind("<Leave>", lambda _e: tree.unbind_all("<MouseWheel>"))