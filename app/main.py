from fastapi import FastAPI, Depends, HTTPException, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import crud, models, tasks
from .database import engine, get_db
from .db_seeder import seed_db # YENİ: Veri ekleme fonksiyonunu import et
from fastapi import status
from starlette.responses import Response
from .database import engine, get_db, SessionLocal

# Proje içindeki diğer modülleri import et

# --- Uygulama Kurulumu ve Başlangıç Ayarları ---

# 1. SQLAlchemy'ye veritabanı tablolarını oluşturmasını söyle.
#    Eğer tablolar zaten varsa, herhangi bir işlem yapmaz.
models.Base.metadata.create_all(bind=engine)

# 2. FastAPI uygulamasını oluştur
app = FastAPI(title="Kütüphane Yönetim Sistemi")

try:
    db = SessionLocal()
    seed_db(db)
finally:
    db.close()
# 3. HTML şablonlarını (templates) kullanmak için Jinja2'yi ayarla
#    Bu, projenin ana dizinindeki 'templates' klasörünü arayacak.
templates = Jinja2Templates(directory="templates")

SECRET_KEY = "supersecretkey"  # Gerçek projede .env'den alınmalı
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Kullanıcıyı token'dan bulmak için yardımcı fonksiyon
def get_current_patron(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Geçersiz kimlik doğrulama bilgisi",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    patron = crud.get_patron_by_username(db, username=username)
    if patron is None:
        raise credentials_exception
    return patron

# --- HTML Arayüzü (UI) Endpointleri ---

@app.get("/", response_class=HTMLResponse, tags=["Arayüz"])
async def show_main_page(request: Request, db: Session = Depends(get_db), access_token: str = Cookie(default=None)):
    """
    Ana yönetim panelini (index.html) gösterir.
    Veritabanından tüm kitapları ve üyeleri çeker ve şablona gönderir.
    Ayrıca giriş yapan kullanıcıya ait ödünç alınan kitapları da gösterir.
    """
    all_books = crud.get_books(db)
    patron = None
    patron_books = []
    patron_id = None
    if access_token:
        try:
            token = access_token.replace("Bearer ", "")
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username:
                patron = crud.get_patron_by_username(db, username=username)
        except Exception:
            patron = None
    if patron:
        patron_id = patron.id
        patron_books = db.query(models.Book).filter_by(patron_id=patron_id).all()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "books": all_books,
            "patron": patron,
            "patron_books": patron_books,
            "patron_id": patron_id,
        }
    )

@app.post("/ui/checkout", tags=["Arayüz"])
async def ui_checkout_book(
    db: Session = Depends(get_db),
    book_id: int = Form(...),
    patron_id: int = Form(...)
):
    """
    HTML arayüzündeki formdan gelen verilerle kitap ödünç alma işlemini yapar.
    İşlemden sonra kullanıcıyı ana sayfaya yönlendirir.
    """
    crud.checkout_book(db=db, book_id=book_id, patron_id=patron_id)
    return RedirectResponse(url="/", status_code=303)


@app.post("/ui/return", tags=["Arayüz"])
async def ui_return_book(db: Session = Depends(get_db), book_id: int = Form(...)):
    """
    HTML arayüzündeki formdan gelen verilerle kitap iade işlemini yapar.
    İşlemden sonra kullanıcıyı ana sayfaya yönlendirir.
    """
    crud.return_book(db=db, book_id=book_id)
    return RedirectResponse(url="/", status_code=303)

@app.get("/login", response_class=HTMLResponse, tags=["Arayüz"])
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login", response_class=HTMLResponse, tags=["Arayüz"])
def login_submit(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    patron = crud.get_patron_by_username(db, username=username)
    if not patron or not crud.verify_password(password, patron.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Kullanıcı adı veya şifre hatalı."})
    access_token = create_access_token(data={"sub": patron.username})
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@app.get("/register", response_class=HTMLResponse, tags=["Arayüz"])
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})

@app.post("/register", response_class=HTMLResponse, tags=["Arayüz"])
def register_submit(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    db_patron = crud.get_patron_by_username(db, username=username)
    if db_patron:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Bu kullanıcı adı zaten alınmış."})
    patron = models.PatronCreate(username=username, password=password)
    crud.create_patron(db, patron)
    response = RedirectResponse(url="/login", status_code=303)
    return response

# --- RESTful API Endpointleri (Swagger / Programatik Erişim için) ---

# --- Kitap API Endpointleri ---

@app.post("/api/books/", response_model=models.BookResponse, status_code=201, tags=["API - Kitaplar"])
def create_book_api(book: models.BookCreate, db: Session = Depends(get_db)):
    """API üzerinden yeni bir kitap oluşturur."""
    return crud.create_book(db=db, book=book)

@app.get("/api/books/", response_model=List[models.BookResponse], tags=["API - Kitaplar"])
def get_all_books_api(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """API üzerinden tüm kitapları listeler."""
    books = crud.get_books(db=db, skip=skip, limit=limit)
    return books

@app.get("/api/books/{book_id}", response_model=models.BookResponse, tags=["API - Kitaplar"])
def get_book_by_id_api(book_id: int, db: Session = Depends(get_db)):
    """API üzerinden ID ile tek bir kitap bilgisi alır."""
    db_book = crud.get_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Kitap bulunamadı")
    return db_book

# --- Üye (Patron) API Endpointleri ---

@app.post("/api/patrons/", response_model=models.PatronResponse, status_code=201, tags=["API - Kullanıcılar"])
def create_patron_api(patron: models.PatronCreate, db: Session = Depends(get_db)):
    """API üzerinden yeni bir kütüphane üyesi oluşturur."""
    # Aynı isimde kullanıcı olup olmadığını kontrol et
    db_patron = crud.get_patron_by_username(db, username=patron.username)
    if db_patron:
        raise HTTPException(status_code=400, detail="Bu isimde bir üye zaten mevcut")
    return crud.create_patron(db=db, patron=patron)

@app.get("/api/patrons/", response_model=List[models.PatronResponse], tags=["API - Kullanıcılar"])
def get_all_patrons_api(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """API üzerinden tüm kütüphane üyelerini listeler."""
    patrons = crud.get_patrons(db=db, skip=skip, limit=limit)
    return patrons

# --- Auth API Endpointleri ---

@app.post("/api/auth/register", response_model=models.PatronResponse, tags=["Auth"])
def register_patron_api(patron: models.PatronCreate, db: Session = Depends(get_db)):
    db_patron = crud.get_patron_by_username(db, username=patron.username)
    if db_patron:
        raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten alınmış.")
    return crud.create_patron(db, patron)

@app.post("/api/auth/login", tags=["Auth"])
def login_patron_api(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    patron = crud.get_patron_by_username(db, username=form_data.username)
    if not patron or not crud.verify_password(form_data.password, patron.hashed_password):
        raise HTTPException(status_code=400, detail="Kullanıcı adı veya şifre hatalı.")
    access_token = create_access_token(data={"sub": patron.username})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Celery Görev Tetikleme Endpoint'i ---

@app.post("/api/tasks/send-reminders", tags=["API - Görevler"])
def trigger_reminders_api():
    """
    Gecikmiş kitaplar için hatırlatma görevini manuel olarak tetikler.
    Bu görev arka planda çalışır.
    """
    tasks.send_overdue_reminders.delay()
    return {"message": "Hatırlatma gönderme görevi başarıyla başlatıldı."}