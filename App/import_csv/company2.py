import csv
import os
from datetime import datetime
import mysql.connector

PROVIDER_MAP = {
    "0": "company2 A",
    "1": "company2 B",
    "2": "company2 C",
}


def _get_col(row: list[str], index: int) -> str:
    return row[index] if index < len(row) else ""


def convert_amount(value: str, divide_by_100: bool = True) -> float | None:
    if not value or not value.strip():
        return None
    cleaned = value.strip().replace(" ", "").replace(",", ".")
    try:
        num = float(cleaned)
        return num / 100.0 if divide_by_100 else num
    except (ValueError, TypeError):
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


def import_company2(
    filepath: str,
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

    print(f"▶ Επεξεργασία company2: {os.path.basename(filepath)}")

    try:
        with open(filepath, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f, delimiter=",", quotechar='"')

            for row in reader:
                if not row or len(row) < 70:
                    continue

                arithmos_parastatikou = (
                    safe_str(_get_col(row, 2), 50).replace("\n", "").replace("\r", "")
                )
                if not arithmos_parastatikou:
                    continue

                arithmos = safe_str(_get_col(row, 1), 50)
                enarxi = convert_date(_get_col(row, 4))
                lixi = convert_date(_get_col(row, 5))
                paroxos = PROVIDER_MAP.get(_get_col(row, 0).strip(), "company2")
                paketo = safe_str(_get_col(row, 23), 50)
                typos = safe_str(_get_col(row, 15), 50)
                kalypseis = safe_str(_get_col(row, 24), 1000)
                mikta = convert_amount(_get_col(row, 13))

                epwnymo = safe_str(_get_col(row, 31), 100)
                onoma = safe_str(_get_col(row, 32), 100)
                address = safe_str(_get_col(row, 37), 100)
                afm = safe_str(_get_col(row, 29), 20)
                tilefono = safe_str(_get_col(row, 39), 20)
                synergatis = safe_str(_get_col(row, 25), 100)
                sxolia = ""

                pinakida = safe_str(_get_col(row, 66), 20)
                marka = safe_str(_get_col(row, 50), 100)
                modelo = safe_str(_get_col(row, 51), 100)
                kathgoria = safe_str(_get_col(row, 55), 100)
                ippoi = safe_int(_get_col(row, 53))
                eidos = safe_str(_get_col(row, 21), 50)
                promitheies = convert_amount(_get_col(row, 68))
                kathara = convert_amount(_get_col(row, 12))

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
                    print(f"❌ ERROR {arithmos_parastatikou}: {err}")

        db.commit()
        print(f"✔ Ολοκληρώθηκε company2 import: {os.path.basename(filepath)}\n")
    finally:
        if close_conn:
            cursor.close()
            db.close()