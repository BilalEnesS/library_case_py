from .celery_config import celery_app
from . import crud
import time

@celery_app.task
def send_overdue_reminders():
    """Gecikmiş kitaplar için hatırlatma gönderir."""
    print("Gecikmiş kitaplar kontrol ediliyor...")
    overdue_books = crud.get_overdue_books()
    if not overdue_books:
        print("Gecikmiş kitap bulunamadı.")
        return

    for book in overdue_books:
        patron_id = book.get("checked_out_to")
        # Gerçek bir projede burada e-posta gönderilir.
        print(f"HATIRLATMA: {patron_id} nolu üyeye, '{book['title']}' kitabının iade tarihi geçtiği bildirildi.")
        time.sleep(1) # Simülasyon
    print("Hatırlatma görevi tamamlandı.")


@celery_app.task
def generate_weekly_report():
    """Haftalık ödünç alma istatistiklerini oluşturur."""
    print("Haftalık rapor oluşturuluyor...")
    checked_out_books = [book for book in crud.db_books.values() if book["checked_out_to"]]
    report = {
        "total_checked_out": len(checked_out_books),
        "checked_out_list": checked_out_books
    }
    # Gerçek bir projede bu rapor bir dosyaya yazılır veya mail atılır.
    print(f"HAFTALIK RAPOR: {report}")
    print("Haftalık rapor görevi tamamlandı.")