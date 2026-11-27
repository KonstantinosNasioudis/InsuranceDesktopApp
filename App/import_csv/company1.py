import csv
import os
from datetime import datetime
import mysql.connector

SYNERGATES_MAP = {
    "10001": "Partner1",
    "10002": "Partner2",
    "15001": "Partner3",
    "15002": "Partner4",
    "11001": "Partner5",
}

VEHICLE_MAP = {
    "moto": "Μηχανή",
    "truck": "Φορτηγό",
    "trailer": "Αυτοκινούμενη ρυμούλκα",
    "taxi": "Ταξί",
    "auto": "Ι.Χ.",
}


def _get_col(row: list[str], index: int) -> str:
    return row[index] if index < len(row) else ""


def convert_number(value: str) -> float | None:
    if not value or not value.strip():
        return None
    cleaned = value.strip().replace(" ", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def convert_date(value: str) -> str | None:
    if not value or not value.strip():
        return None
    cleaned = value.strip()
    for fmt in ("%Y%m%d", "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(cleaned, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def safe_str(value: str, max_len: int | None = None) -> str:
    if not value:
        return ""
    val = value.strip()
    if max_len and len(val) > max_len:
        return val[:max_len]
    return val


def safe_int(value: str) -> int | None:
    if not value:
        return None
    cleaned = value.strip()
    if not cleaned.isdigit():
        return None
    return int(cleaned)


def load_covers(cover_file: str) -> dict[str, str]:
    covers: dict[str, str] = {}
    with open(cover_file, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter=";")
        for row in reader:
            if not row or len(row) < 8:
                continue
            arithmos_parastatikou = (
                _get_col(row, 3).strip().replace("\n", "").replace("\r", "")
            )
            if not arithmos_parastatikou:
                continue
            kalypseis = f"{_get_col(row, 6).strip()}\n{_get_col(row, 7).strip()}".strip()
            if not kalypseis:
                continue
            if arithmos_parastatikou in covers:
                covers[arithmos_parastatikou] += f"\n{kalypseis}"
            else:
                covers[arithmos_parastatikou] = kalypseis
    return covers


def import_company1(
    filepath: str,
    covers: dict[str, str],
    db=None,
    cursor=None,
    DB_CONFIG: dict | None = None,
) -> None:
    close_conn = False
    if db is None or cursor is None:
        if DB_CONFIG is None:
            raise ValueError("Χρειάζεται DB_CONFIG αν δεν δίνεται db/cursor.")
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()
        close_conn = True

    print(f"▶ Επεξεργασία company1: {os.path.basename(filepath)}")

    try:
        with open(filepath, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f, delimiter=";")
            for row in reader:
                if not row or len(row) < 20:
                    continue

                arithmos_parastatikou = (
                    safe_str(_get_col(row, 3), 50).replace("\n", "").replace("\r", "")
                )
                if not arithmos_parastatikou:
                    continue

                arithmos = safe_str(_get_col(row, 2), 50)
                enarxi = convert_date(_get_col(row, 5))
                lixi = convert_date(_get_col(row, 7))
                paroxos = "company1"
                paketo = safe_str(_get_col(row, 34), 50)
                typos = ""
                kathgoria = ""
                mikta = convert_number(_get_col(row, 10))

                kalypseis = covers.get(arithmos_parastatikou, "")
                if not kalypseis:
                    print(f"⚠ Δεν βρέθηκε κάλυψη για {arithmos_parastatikou}")

                epwnymo = safe_str(_get_col(row, 12), 100)
                onoma = safe_str(_get_col(row, 13), 100)
                address_raw = f"{_get_col(row, 17)} {_get_col(row, 18)}, {_get_col(row, 19)}"
                address = safe_str(address_raw, 100)
                afm = safe_str(_get_col(row, 15), 20)
                tilefono = safe_str(_get_col(row, 23), 20)

                synergatis_code = safe_str(_get_col(row, 8))
                synergatis = SYNERGATES_MAP.get(synergatis_code, "")
                sxolia = ""

                pinakida = safe_str(_get_col(row, 11), 20)
                marka = safe_str(_get_col(row, 26), 100)
                modelo = safe_str(_get_col(row, 27), 100)
                ippoi = safe_int(_get_col(row, 28))
                eidos = ""
                promitheies = convert_number(_get_col(row, 35))
                kathara = convert_number(_get_col(row, 9))

                paketo_lower = paketo.lower()
                for key, value in VEHICLE_MAP.items():
                    if key in paketo_lower:
                        typos = value
                        kathgoria = "Όχημα"
                        break

                try:
                    cursor.execute(
                        """
                        INSERT INTO sumbolaia (
                            arithmos_parastatikou, arithmos, enarxi, lixi, paroxos, paketo, typos, mikta,
                            onoma, epwnymo, address, afm, tilefono, synergatis, sxolia,
                            pinakida, marka, modelo, kathgoria, ippoi, eidos, kalypseis, promitheies, kathara
                        )
                        VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        ON DUPLICATE KEY UPDATE
                            arithmos = VALUES(arithmos),
                            enarxi = VALUES(enarxi),
                            lixi = VALUES(lixi),
                            paroxos = VALUES(paroxos),
                            paketo = VALUES(paketo),
                            typos = VALUES(typos),
                            mikta = VALUES(mikta),
                            onoma = VALUES(onoma),
                            epwnymo = VALUES(epwnymo),
                            address = VALUES(address),
                            afm = VALUES(afm),
                            tilefono = VALUES(tilefono),
                            synergatis = VALUES(synergatis),
                            sxolia = VALUES(sxolia),
                            pinakida = VALUES(pinakida),
                            marka = VALUES(marka),
                            modelo = VALUES(modelo),
                            kathgoria = VALUES(kathgoria),
                            ippoi = VALUES(ippoi),
                            eidos = VALUES(eidos),
                            kalypseis = VALUES(kalypseis),
                            promitheies = VALUES(promitheies),
                            kathara = VALUES(kathara)
                        """,
                        (
                            arithmos_parastatikou, arithmos, enarxi, lixi, paroxos, paketo, typos, mikta,
                            onoma, epwnymo, address, afm, tilefono, synergatis, sxolia,
                            pinakida, marka, modelo, kathgoria, ippoi, eidos, kalypseis, promitheies, kathara,
                        ),
                    )
                except mysql.connector.Error as err:
                    print(f"ERROR inserting/updating {arithmos_parastatikou}: {err}")

        db.commit()
        print(f"✔ Ολοκληρώθηκε η εισαγωγή company1: {os.path.basename(filepath)}\n")
    finally:
        if close_conn:
            cursor.close()
            db.close()


# Alias για συμβατότητα αν καλείται ακόμα import_csv
import_csv = import_company1