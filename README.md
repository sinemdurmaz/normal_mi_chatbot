# "Normal mi?" Akıllı Asistanı

Mother &amp; Child Platform projesi "Normal mi?" Akıllı Asistanı için gelişmiş bir hibrit yapay zeka prototipi (Open Ai Assistant Platform için uygun şekilde tasarlanmıştır.)

## Kimlik bilgileri (kurulum sonrası doldurulacak)

| Alan | Değer |
|---|---|
| Assistant ID | `asst_RpWD8gMh2X3PTHpPYyivPXUO` *(setup script çıktısından yapıştır)* |
| Vector Store ID | `vs_6a59fd15b8c0819198904a3a97e5a234` *(setup script çıktısından yapıştır)* |
| Model | `gpt-4.1` (File Search + Structured Outputs destekler) |
| Oluşturulma tarihi | *(doldurulacak)* |
| Ortam | OpenAI Assistants Platform (v2) |

# NORMALMI-AI — README

**Proje:** "Normal mi?" Akıllı Asistanı — Karalabs Mother & Child Platform
**Görev tanımı:** Hibrit (Karma) yapay zeka mimarisi — OpenAI Assistants Platform
**Hazırlayan:** Sinem

Bu belge, görev tanımındaki her madde için **ne yapıldığını**, **hangi
teknolojinin/yaklaşımın seçildiğini** ve **neden** seçildiğini açıklar.
Amaç, mentörlerin ve yazılım ekibinin projeyi kod satırlarına girmeden
kavramsal olarak anlayabilmesi.

---

## 0. Genel Mimari Kararı: Neden "Hibrit"?

Görev tanımı, yapay zekayı serbest bırakmak yerine hibrit bir sistem
istiyordu: **LLM anlıyor, kural motoru karar veriyor.** Bunu API seviyesinde
zorunlu kılmak için asistanı **tek modlu değil, iki modlu** kurguladık:

| Mod | Görev | Risk kararı verir mi? |
|---|---|---|
| **MOD 1** — Semptom Çıkarımı | Serbest metni yapılandırılmış JSON'a çevirir | **Hayır** |
| **Backend Rule Engine** | ACOG eşiklerine göre risk seviyesi belirler (Python, LLM değil) | **Evet — tek karar verici** |
| **MOD 2** — Risk Açıklama | Backend kararını File Search referanslarıyla empatik dille anlatır | **Hayır (sadece iletir)** |

**Neden tek bir LLM çağrısı yeterli değildi:** Tek çağrıda hem çıkarım hem
açıklama yaptırmak, modelin aynı anda örtük şekilde risk değerlendirmesi
yapmasına ("bu ciddi görünüyor" gibi sızıntılara) yol açabilirdi. İki ayrı
çağrı + iki ayrı JSON şeması, "LLM sadece anlıyor, karar motoru karar
veriyor" ayrımını modelin iyi niyetine değil, API'nin yapısına bağlı hale
getiriyor. Detaylı akış → `rag/docs/System_Architecture.md`.

---

## 1. Veri Maskeleme (KVKK Güvenlik Katmanı) — `masking/`

### Ne yapıldı
Kullanıcı metni OpenAI'ye gitmeden önce iki katmanlı bir temizlikten geçiyor:

1. **Regex katmanı** (`regex_mask.py`) — telefon, e-posta, TC kimlik no gibi
   sabit **kalıplı** verileri yakalar.
2. **NER katmanı** (`ner_mask.py`) — isim ve lokasyon gibi **kalıpsız, bağlama
   bağlı** verileri yakalar.

`masker.py` bu ikisini sırayla uygulayan tek giriş noktasıdır; backend bu
fonksiyonu OpenAI'ye hiçbir istek göndermeden, tamamen yerelde çağırır.

### Hangi teknoloji, neden
- **Regex neden yeterli değil tek başına:** İsim ve şehir adları sabit bir
  kalıba uymaz ("Ayşe", "Adana" gibi kelimeleri regex ile yakalamanın tek
  yolu elle liste tutmaktır — ölçeklenmez, yeni isim/şehirde kaçırır).
- **Neden `savasy/bert-base-turkish-ner-cased`:** Türkçe'ye özel
  fine-tune edilmiş bir BERT modeli olduğu için, İngilizce NER modellerine
  göre Türkçe isim/yer varlıklarını çok daha güvenilir tanıyor. Hugging Face
  `transformers` pipeline'ı üzerinden `aggregation_strategy="simple"` ile
  çalıştırılıyor — bu, alt-kelime (subword) parçalarını tek bir varlığa
  otomatik birleştiriyor (ör. "İsken" + "##derun" → "İskenderun").
- **`gliner_mask.py` neden ayrı/opsiyonel bırakıldı:** GLiNER, sıfır-atış
  (zero-shot) çok dilli bir varlık tanıma modeli — herhangi bir etiket
  kümesiyle (ör. "hastalık", "ilaç") esnek çalışabiliyor. Şu an ana akışta
  kullanılmıyor çünkü BERT-NER (isim/lokasyon için) bu iş için zaten yeterli
  ve daha hafif; GLiNER ileride daha zengin varlık türleri (ör. ilaç adı
  maskeleme) gerekirse yedek/genişletme seçeneği olarak bırakıldı.
- **Sıralama önemli:** `ner_mask.py` içinde varlıklar metnin **sonundan
  başına doğru** (ters sırayla) değiştiriliyor — aksi halde bir önceki
  değişiklik, bir sonraki varlığın karakter indekslerini kaydırıp yanlış
  yerden kesim yapılmasına neden olur.

---

## 2. Sistem Talimatı (System Instructions) — `assistant/System_Instructions.md`

### Ne yapıldı
OpenAI Assistant'ın "Instructions" alanına birebir yapıştırılacak, iki modu
(MOD 1 / MOD 2) ayrı ayrı tanımlayan, katı kurallarla sınırlandırılmış bir
sistem promptu.

### Hangi teknoloji/yaklaşım, neden
- **Rol + kesin sınır + üslup + akış + fallback + güvenlik + çıktı kuralları**
  şeklinde ayrı bölümlere ayrıldı. Tek bir uzun paragraf yerine başlıklı
  yapı kullanılmasının nedeni: LLM'ler bölümlenmiş, tekrarlanan
  vurgulara (ör. "asla teşhis koyma" hem GÜVENLİK hem MOD 1 açıklamasında
  geçiyor) daha tutarlı uyuyor; tek bir cümleye gömülü kural kolayca
  atlanabiliyor.
- **MOD 1'de File Search'in kapalı olması (`tool_choice: "none"`):** Semptom
  çıkarımı sırf dil anlama işi; File Search'in burada tetiklenmesi hem
  gereksiz gecikme hem de modelin çıkarım yerine RAG içeriğinden esinlenerek
  alan doldurmasına (yani örtük halüsinasyon) yol açabilirdi.
- **MOD 2'de File Search zorunlu değil ama açık (`tool_choice: "auto"`):**
  Açıklama üretirken modelin referans dokümanlara **dayanması** isteniyor
  ama teknik olarak zorunlu kılmak (`required`) her senaryoda mantıklı
  olmayabilir (ör. çok net bir kırmızı kod açıklaması ekstra arama
  gerektirmeyebilir); `auto` modelin ihtiyaç duyduğunda arama yapmasına izin
  veriyor.
- **Run-seviyesinde `response_format` override:** Assistants API,
  Assistant oluşturulurken sabit tek bir `response_format` seçmeye izin
  veriyor, ama bizim iki modumuz var. Bu yüzden Assistant'a sabit şema
  **verilmedi**; her `Run` çağrısında (`client.beta.threads.runs.create`)
  ilgili moda uygun şema ayrıca gönderiliyor. Bu, tek Assistant ID ile iki
  farklı çıktı sözleşmesini aynı anda desteklemenin OpenAI API'sindeki tek
  yolu.

---

## 3. Tıbbi Bilgi Tabanı / File Search (RAG) — `rag/pdfs/`

### Ne yapıldı
8 adet Markdown dosyası, OpenAI'nin **Vector Store** özelliğine yüklenip
File Search aracına bağlanacak şekilde hazırlandı: Preeklampsi, Uyarı
Bulguları, Kanama, Fetal Hareket, Doğum Belirtileri, Yaygın Semptomlar,
Terim Sözlüğü, Sistem Politikaları.

### Hangi teknoloji, neden
- **Neden OpenAI Vector Store (kendi vektör veritabanımız yerine):** Görev
  tanımı zaten OpenAI Assistants Platform'u zorunlu kılıyordu; Vector Store
  + File Search, embedding üretme, indeksleme ve benzerlik aramasını
  yönetilen bir servis olarak sunduğu için ayrı bir vektör veritabanı
  (Pinecone, Chroma vb.) kurmaya gerek bırakmıyor — kapsam ve bakım
  yükü açısından en basit çözüm.
- **Neden dosyalar Markdown + YAML front-matter (`title`, `category`,
  `version`, `language`) ile yapılandırıldı:** Front-matter, dosyaların
  insan tarafından hızlı taranabilmesini sağlıyor; asıl retrieval kalitesini
  artıran ise her dosyanın sonundaki **Keywords** bölümü — Türkçe ve
  İngilizce eş anlamlıları (ör. "baş ağrısı" / "headache") aynı dosyada
  tutarak, kullanıcının hangi dilde/ifadeyle yazarsa yazsın doğru dosyanın
  bulunma olasılığını artırıyor.
- **`07_Glossary.md`'nin ayrı bir dosya olarak var olmasının nedeni:**
  File Search benzerlik tabanlı çalıştığı için, kullanıcı "ışık çakması"
  yazdığında bunun "preeklampsi" ile ilişkisi doğrudan görünür olmayabilir.
  Sözlük dosyası, TR↔EN ve günlük dil↔tıbbi terim eşleştirmelerini tek yerde
  toplayarak retrieval'in daha isabetli çalışmasına yardımcı oluyor.
- **`08_System_Policies.md`'nin İngilizce ve ayrı tutulmasının nedeni:**
  Bu dosya, System Instructions'taki güvenlik kurallarının bir RAG-erişilebilir
  yedeği. Ana kaynak her zaman System Instructions'tır (dosya benzerlik
  aramasıyla her zaman tetiklenmeyebilir); bu doğrudan `Technical_Documentation.md`'de
  bilinen sınırlama olarak not edildi.
- **02 ve 03 numaralı dosyaların içerik/isim uyumu düzeltmesi:** İlk
  taslakta `02_Warning_Signs.md` kanama içeriği, `03_Bleeding.md` ise ateş/
  karın ağrısı içeriği taşıyordu (isim-içerik uyuşmazlığı). File Search
  içerik bazlı aradığı için işlevi bozmuyordu, ama insan denetimini
  zorlaştırdığı ve `Rule_Engine_Policy.md` gibi çapraz-referans veren
  dokümanlarda kafa karıştıracağı için içerikler dosya adlarıyla eşleşecek
  şekilde düzeltildi.

---

## 4. Yapılandırılmış Çıktı (JSON API Kontratı) — `assistant/`

### Ne yapıldı
İki ayrı JSON şeması: `mod1_schema.json` (semptom çıkarımı — 20 alan) ve
`mod2_schema.json` (risk açıklama — tek alan: `aciklama_metni`). İkisi de
`assistant/JSON_API_Contract.md` içinde örneklerle belgelendi.

### Hangi teknoloji, neden
- **Neden "JSON mode" değil, Structured Outputs (`json_schema`,
  `strict: true`):** Eski/gevşek "JSON mode" sadece çıktının *geçerli bir
  JSON* olmasını garanti eder, alan adlarını veya tiplerini garanti etmez —
  model bir alanı unutabilir ya da fazladan alan üretebilir. `strict: true`
  ile OpenAI, çıktının **birebir şemaya uymasını** API seviyesinde zorluyor;
  backend'in JSON parse hatası veya eksik-alan hatası alma riski ortadan
  kalkıyor. Bu, yazılım ekibinin "temiz, işlenebilir veri" talebini
  doğrudan karşılıyor.
- **Neden nullable alanlar `["string","null"]` biçiminde:** JSON Schema'da
  strict modda `required` listesi şemadaki TÜM alanları içermek zorunda
  (alan "opsiyonel" olamaz), ama alanın **değeri** null olabilir. Bu yüzden
  "bilinmiyor/belirtilmedi" durumu, alanı required listesinden çıkararak
  değil, tipine `null`'ı ekleyerek ifade ediliyor.
- **Neden MOD 2 için ayrı, minimal bir şema:** İlk taslakta yalnızca MOD 1
  şeması vardı; MOD 2'nin (risk açıklama) çıktısı tanımsızdı. Backend'in bunu
  da programatik işleyebilmesi için tek alanlı (`aciklama_metni`) ama yine
  `strict: true` bir şema eklendi — böylece MOD 2 çıktısı da serbest metin
  değil, garantili JSON.

---

## 5. Backend Rule Engine — `backend/rule_engine.py` (ek, görev tanımında zorunlu değil)

### Ne yapıldı
MOD 1'in ürettiği yapılandırılmış veriyi (boolean/sayısal alanlar) alıp,
`rag/pdfs/01-06` dosyalarındaki ACOG tabanlı eşiklere göre deterministik bir
`risk_seviyesi` (kırmızı/sarı/yeşil/belirsiz) üreten saf Python kodu.

### Hangi teknoloji, neden
- **Neden LLM değil, düz Python:** Görev tanımının temel önermesi zaten
  buydu — "nihai tıbbi karar kural motoru tarafından verilecek." Bunu bir
  LLM çağrısıyla değil, test edilebilir, deterministik, versiyon
  kontrollü saf fonksiyonlarla yaptık; aynı girdi her zaman aynı çıktıyı
  üretir ve bu davranış birim testleriyle (`test_rule_engine.py`, 14/14
  geçiyor) doğrulanabilir.
- **Her eşiğin kaynağının yorum satırlarında belirtilmesi:** Kod ile
  `rag/pdfs` dosyaları arasındaki bağı görünür kılmak için her fonksiyonun
  üstünde ilgili dosyadan alıntı var. Bu bağlantının tam tablosu
  `rag/docs/Rule_Engine_Policy.md`'de.
- **Neden dahil edildi (zorunlu olmamasına rağmen):** Görev tanımı Rule
  Engine'in "zaten var" olduğunu varsayıyordu; ama sistemin gerçekten uçtan
  uca çalıştığını göstermek ve MOD 2'ye gönderilecek `risk_seviyesi`'nin
  nereden geldiğini somutlaştırmak için hazırlandı. `run_pipeline.py`,
  maskeleme → MOD 1 → Rule Engine → MOD 2 zincirinin tamamını gösteren bir
  referans entegrasyon script'idir.

---

## Klasör Yapısı

```
NORMALMI-AI/
├── assistant/              → Panel'e yapıştırılacak metinler + JSON şemaları
│   ├── System_Instructions.md
│   ├── JSON_API_Contract.md
│   ├── Prompt_Examples.md
│   ├── Assistant_Info.md
│   ├── mod1_schema.json
│   └── mod2_schema.json
├── masking/                → KVKK veri maskeleme (regex + NER)
├── rag/
│   ├── pdfs/                → File Search'e yüklenecek 8 referans doküman
│   └── docs/                 → Kurulum, mimari, politika dokümantasyonu
└── backend/                 → Rule Engine + uçtan uca entegrasyon örneği
```

## Teslimat kriterleriyle eşleşme (görev tanımı madde 5)

| Kriter | Karşılığı |
|---|---|
| 1. Canlı Assistant ID | `assistant/System_Instructions.md` + `rag/pdfs/*` panelde kurulduktan sonra elde edilir; kayıt yeri `assistant/Assistant_Info.md` |
| 2. Akış Diyagramı | `rag/docs/flow_diagram_v2.png` + `rag/docs/System_Architecture.md` |
| 3. JSON API Kontratı | `assistant/JSON_API_Contract.md` + `mod1_schema.json` / `mod2_schema.json` |
