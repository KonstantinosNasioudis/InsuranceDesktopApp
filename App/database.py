import os
import mysql.connector


def get_db_config() -> dict:
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "asfalies"),
    }


def connect():
    return mysql.connector.connect(**get_db_config())


def initialize_database():
    db = connect()
    cursor = db.cursor()
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sumbolaia (
            arithmos_parastatikou VARCHAR(50) PRIMARY KEY,

            -- Στοιχεία συμβολαίου
            arithmos VARCHAR(50),
            enarxi DATE,
            lixi DATE,
            paroxos VARCHAR(100),
            paketo VARCHAR(50),
            typos VARCHAR(50),
            kalypseis VARCHAR(1000),
            mikta DECIMAL(10,2),

            -- Στοιχεία πελάτη
            onoma VARCHAR(100),
            epwnymo VARCHAR(100),
            address VARCHAR(100),
            afm VARCHAR(20),
            tilefono VARCHAR(20),
            synergatis VARCHAR(100),
            sxolia TEXT,

            -- Στοιχεία οχήματος
            pinakida VARCHAR(20),
            marka VARCHAR(100),
            modelo VARCHAR(100),
            kathgoria VARCHAR(100),
            ippoi INT,
            eidos VARCHAR(50),
            promitheies DECIMAL(10,2),
            kathara DECIMAL(10,2)
        )
        """)
        db.commit()
    finally:
        cursor.close()
        db.close()


if __name__ == "__main__":
    initialize_database()