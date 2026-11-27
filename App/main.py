from database import initialize_database
from backup import create_auto_backup
from gui import start_gui
import ttkbootstrap as tb

if __name__ == '__main__':
    db, cursor = initialize_database()

    create_auto_backup()

    start_gui(theme='darkly')

    cursor.close()
    db.close()
