from sqlalchemy.orm import Session
from . import crud, models

def seed_db(db: Session):
    print("Başlangıç verileri (tohumlama) ekleniyor...")

    # 10 kitap ekle (her başlatmada tekrar eklenmesin diye başlığa göre kontrol)
    kitaplar = [
        {"title": "Suç ve Ceza", "author": "Fyodor Dostoyevski"},
        {"title": "Sefiller", "author": "Victor Hugo"},
        {"title": "Kürk Mantolu Madonna", "author": "Sabahattin Ali"},
        {"title": "1984", "author": "George Orwell"},
        {"title": "Hayvan Çiftliği", "author": "George Orwell"},
        {"title": "Beyaz Diş", "author": "Jack London"},
        {"title": "Simyacı", "author": "Paulo Coelho"},
        {"title": "Dönüşüm", "author": "Franz Kafka"},
        {"title": "Tutunamayanlar", "author": "Oğuz Atay"},
        {"title": "İnce Memed", "author": "Yaşar Kemal"},
    ]
    for kitap in kitaplar:
        mevcut_kitap = db.query(models.Book).filter_by(title=kitap["title"]).first()
        if not mevcut_kitap:
            crud.create_book(db, book=models.BookCreate(title=kitap["title"], author=kitap["author"]))

    # Örnek patron (kullanıcı) ve ödünç alma işlemi
    patron1_data = models.PatronCreate(username="ahmet", password="sifre123")
    patron_1_db = crud.get_patron_by_username(db, username=patron1_data.username)
    if not patron_1_db:
        patron_1_db = crud.create_patron(db, patron=patron1_data)

    # Ahmet'e bir kitap ödünç ver
    book_to_checkout = db.query(models.Book).filter_by(title="Hayvan Çiftliği").first()
    if book_to_checkout and book_to_checkout.patron_id is None:
        crud.checkout_book(db=db, book_id=book_to_checkout.id, patron_id=patron_1_db.id)

    print("Tohumlama tamamlandı.")