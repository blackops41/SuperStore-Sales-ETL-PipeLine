import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# .env dosyasını bul (Script nerede olursa olsun)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

def get_engine():
    db_password = os.getenv("DB_PASSWORD")
    url = (
        f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:{db_password}"
        f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}"
        f"/{os.getenv('DB_NAME', 'superstore_son')}"
    )
    return create_engine(url)

if __name__ == "__main__":
    try:
        engine = get_engine()
        
        # SQL dosyasının yolunu bul
        sql_path = os.path.join(BASE_DIR, "sql", "business_queries.sql")
        
        with open(sql_path, "r", encoding="utf-8") as f:
            sql_script = f.read()

        # ---------------------------------------------------------
        # HAYAT KURTARAN SATIR: Kopyalama kaynaklı görünmez 'hayalet' 
        # boşlukları (\xa0) ve gereksiz karakterleri normal boşluğa çevir!
        # ---------------------------------------------------------
        sql_script = sql_script.replace('\xa0', ' ')

        # Noktalı virgüle göre ayır (Sorguları listele)
        queries = [q.strip() for q in sql_script.split(";") if q.strip()]

        print("🚀 İş Zekası (BI) Raporları Çekiliyor...\n")
        
        with engine.connect() as conn:
            for i, query in enumerate(queries, 1):
                try:
                    # Sadece SELECT içeren sorguları çalıştır (Yorum satırlarını atla)
                    if "SELECT" not in query.upper():
                        continue
                        
                    # Pandas ile sorguyu çalıştırıp terminale hizalı tablo olarak bas
                    df = pd.read_sql(text(query), conn)
                    print(f"📊 --- BUSINESS QUERY {i} ---")
                    print(df.to_string(index=False)) 
                    print("\n" + "="*60 + "\n")
                    
                except Exception as inner_e:
                    print(f"⚠️ Sorgu {i} Atlandı (Hata: {inner_e})")
                    continue
                    
    except FileNotFoundError:
        print(f"❌ HATA: SQL dosyası bulunamadı! Lütfen şu yolda olduğundan emin ol: {sql_path}")
    except Exception as e:
        print(f"❌ Beklenmeyen bir hata oluştu: {e}")
