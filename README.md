```markdown
# Interactive Question Generation App - Kurulum Rehberi

Bu rehber, Interactive Question Generation App uygulamasının kurulum ve çalıştırma adımlarını içerir.

## Gereksinimlerin Kurulumu

### 1. Python Kurulumu
Bu proje, Python 3.7 veya daha üst bir sürüm gerektirir. Python yüklü değilse, [Python'un resmi sitesinden](https://www.python.org/downloads/) indirip kurabilirsiniz.

### 2. Sanal Ortam Oluşturma (Önerilir)
Projeyi izole bir ortamda çalıştırmak için bir sanal ortam oluşturabilirsiniz:

```bash
python -m venv env
```

Sanal ortamı etkinleştirin:
- **Windows**:
  ```bash
  .\env\Scripts\activate
  ```
- **MacOS/Linux**:
  ```bash
  source env/bin/activate
  ```

### 3. Gerekli Paketlerin Yüklenmesi
Gerekli Python kütüphanelerini yüklemek için aşağıdaki adımları izleyin:

- Eğer bir `requirements.txt` dosyanız varsa, şu komutu çalıştırarak bağımlılıkları yükleyin:
  ```bash
  pip install -r requirements.txt
  ```

- Eğer `requirements.txt` dosyanız yoksa, ana bağımlılıkları manuel olarak yükleyin:
  ```bash
  pip install streamlit werkzeug plotly pandas python-dotenv
  ```

## Çevresel Değişkenlerin Tanımlanması

### API Anahtarının Ayarlanması
`QuestionGenerator` sınıfı, bir API anahtarına ihtiyaç duyar. Bu anahtarı kullanabilmek için projenin kök dizininde bir `.env` dosyası oluşturarak şu şekilde tanımlayın:

```env
API_KEY="sizin_api_anahtarınız"
```

Bu dosya içindeki çevresel değişkenleri yüklemek için `python-dotenv` kütüphanesini yüklemeniz gerekebilir:

```bash
pip install python-dotenv
```

## Veritabanı Ayarları

Uygulama veritabanı işlemleri için `Database` sınıfını kullanır. `database.py` dosyasında veritabanı bağlantı detaylarını ayarladığınızdan emin olun. Eğer veritabanı tablolarının oluşturulması gerekiyorsa, SQL şemalarını inceleyip kurulum işlemlerini gerçekleştirmeniz gerekebilir.

## Dosya Yapısı

Projenin kök dizininde aşağıdaki dosyaların bulunduğundan emin olun:

```
project_directory/
│
├── app.py                 # Ana uygulama dosyası
├── prompt_template.py      # Soru oluşturma işlevlerini içerir
├── summarizer.py           # PDF özetleme işlevlerini içerir
├── pdf_reader.py           # PDF içeriği okuma işlevlerini içerir
├── database.py             # Veritabanı işlemleri için sınıflar ve işlevler
├── .env                    # API anahtarları ve diğer gizli bilgiler için
└── requirements.txt        # Gerekli Python paketleri listesi
```

## Uygulamanın Çalıştırılması

Uygulamayı başlatmak için şu komutu çalıştırın:

```bash
streamlit run app.py
```

Bu komut, tarayıcıda bir Streamlit arayüzü açacak ve uygulamayı kullanmaya başlayabileceksiniz.

---

Uygulama hakkında sorularınız veya karşılaştığınız sorunlar varsa, dökümantasyon ya da destek ekibinizle iletişime geçebilirsiniz.
```
