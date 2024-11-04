# Interactive Question Generation App

Deployed Project: https://7ed1-185-193-4-248.ngrok-free.app/

[questionappV1.webm](https://github.com/user-attachments/assets/d3ddc3e4-7baf-4280-a016-94fc82dbd134)



Bu proje üniversite öğrencileri başta olmak üzere tüm öğrencilerin ve self-learning öğrenmeye dayalı öğrenen kişilerin, çalıştıkları konular üzerinde kendilerini test edebilmesi için geliştirilmiş hızlı bir çözüm sunmaktadır. Bahsi geçen hedef kitle çalıştıkları konular hakkında kendilerini test edebileceği soru havuzu yok ise öğrenciler çalıştıkları konuları kavrayamamaktadır. Öğrencilerin çalıştıkları konular üzerinde kendilerini test edebilmesi tecrübe ile öğrenmenin ilk basamağıdır. Bu sebeple takımımızla "Interactive Question Generation App" ürününü geliştirdik. Bu ürün kullanıcıdan bir PDF dosyası almakta ve dosya üzerinden kullanıcıya, kullanıcının istediği miktarda soru sormaktadır. Ayrıca kullanıcının hatalı soruları analizlenmekte, hangi konularda eksik olduğu görselleştirilmektedir. Kullanıcının yanlış cevapladığı sorular Gemini API kullanılarak açıklanmaktadır. Bunlarla birlikte kullanıcı sorular hakkında aklına takılan, merak ettiği durumları sorup cevabını alabilmektedir.

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
ya da 

Anahtarlarınızı sisteminizde kurun:
- **Windows**:
  ```bash
  export API_KEY="anahtar"
  ```
- **MacOS/Linux**:
  ```bash
  set API_KEY="anahtar"
  ```


## Veritabanı Ayarları

Uygulama veritabanı işlemleri için `Database` sınıfını kullanır. `database.py` dosyasında veritabanı bağlantı detaylarını ayarladığınızdan emin olun. 


## Uygulamanın Çalıştırılması

Uygulamayı başlatmak için şu komutu çalıştırın:

```bash
streamlit run app.py
```

Bu komut, tarayıcıda bir Streamlit arayüzü açacak ve uygulamayı kullanmaya başlayabileceksiniz.

---
# Ayrıca
Üç kişiilik takımımızdaki Yazılım ve Bilgisayar Mühendisliği öğrencileri olarak çeşitli konuları pratik yaparak öğrenebiliyoruz ancak pratik yapılacak konu içeriği belirsiz olduğunda hangi senaryoya uygun davranmamız gerektiğini seçmek zaman alıcı olabiliyor. Bu senaryoları daha önceden tecrübe etmek daha nitelikli bir mühendis ağı oluşturacaktır. Örneğin "Algoritma ve Veri Yapıları" dersinde pratik yapılarak stack veri yapısı öğrenilebilir ancak hangi durumda stack kullanılması gerektiği bir öğrenciye göre zor bir seçim olabilir. Kullanılan eğitim materyali içerisinde geçen "stack web browserlarında kullanılır" cümlesi öğrenciye soru olarak geldiği vakit bu konu anlaşılma oranını yükseltecektir. Bununla birlikte; öğrenciler, yüksek lisans/araştırma görevlileri literatür taraması yapıp çeşitli makaleler okumaktadır. Okunan makalelerin anlaşılıp anlaşılmadığını test etmek yine bu uygulama sayesinde yapılabilmektedir.

Uygulama hakkında sorularınız veya karşılaştığınız sorunlar varsa, dökümantasyon ya da destek ekibinizle iletişime geçebilirsiniz.

```
