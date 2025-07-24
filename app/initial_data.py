from sqlalchemy.orm import Session
from . import crud, models

def seed_db(db: Session):
    # Veritabanında herhangi bir kitap olup olmadığını kontrol et
    book = db.query(models.Book).first()
    
    # Eğer kitap yoksa (yani veritabanı boşsa), örnek verileri ekle
    if not book:
        print("Veritabanı boş, örnek veriler ekleniyor...")
        
        # Örnek Kullanıcılar Oluştur
        patron_1 = crud.create_patron(db, patron=models.PatronCreate(name="Ahmet Yılmaz"))
        patron_2 = crud.create_patron(db, patron=models.PatronCreate(name="Zeynep Kaya"))
        
        # Örnek Kitaplar Oluştur
        crud.create_book(db, book=models.BookCreate(title="Sefiller", author="Victor Hugo"))
        crud.create_book(db, book=models.BookCreate(title="1984", author="George Orwell"))
        crud.create_book(db, book=models.BookCreate(title="Hayvan Çiftliği", author="George Orwell"))
        book_to_checkout = crud.create_book(db, book=models.BookCreate(title="Suç ve Ceza", author="Dostoyevski"))
        
        # Bir kitabı ödünç alınmış olarak ayarla
        crud.checkout_book(db=db, book_id=book_to_checkout.id, patron_id=patron_1.id)
        
        print("Örnek veriler başarıyla eklendi.")
    else:
        print("Veritabanı zaten dolu, veri ekleme atlandı.")