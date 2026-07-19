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

## Yapılandırma özeti

- **Tools:** `file_search`
- **Tool Resources:** `{"file_search": {"vector_store_ids": ["<VECTOR_STORE_ID>"]}}`
- **Instructions:** `assistant/System_Instructions.md` içindeki tam metin
- **Response Format:** Assistant seviyesinde SABİT bir şema seçilmez. İki
  farklı şema (`normalmi_symptom_extraction`, `normalmi_risk_explanation`)
  her `Run` çağrısında ayrı ayrı verilir (bkz. `JSON_API_Contract.md`).
- **Tool choice:** MOD 1 run'larında `"none"`, MOD 2 run'larında `"auto"`.

## Vector Store içeriği (`rag/pdfs/`)

| Dosya | İçerik | Kullanıldığı mod |
|---|---|---|
| `01_Preeclampsia.md` | Preeklampsi belirtileri (baş ağrısı, görme bozukluğu, ani ödem, tansiyon) | MOD 2 |
| `02_Warning_Signs.md` | Ateş, karın ağrısı, bayılma, nefes darlığı | MOD 2 |
| `03_Bleeding.md` | Gebelikte kanama (trimester bazlı) | MOD 2 |
| `04_Fetal_Movement.md` | Bebek hareketlerinde azalma | MOD 2 |
| `05_Labor_Signs.md` | Erken doğum belirtileri, kasılma, su gelmesi | MOD 2 |
| `06_Common_Symptoms.md` | Normal/beklenen gebelik rahatsızlıkları | MOD 2 |
| `07_Glossary.md` | TR↔EN tıbbi terim eşleştirmeleri | MOD 2 (retrieval optimizasyonu) |
| `08_System_Policies.md` | Davranışsal güvenlik politikaları (İngilizce) | Referans / instructions ile birebir örtüşür |

> Not: `08_System_Policies.md` benzerlik tabanlı File Search ile her zaman
> tetiklenmeyebilir (kullanıcı sorguları politika diliyle örtüşmez). Bu
> yüzden kritik kurallar zaten `System_Instructions.md`'de doğrudan yer
> alıyor — bu dosya ek bir güvence katmanı, tek kaynak değil.

## Kurulum ve test

Adım adım kurulum ve test komutları için → `rag/docs/Installation.md`
Mimari şeması için → `rag/docs/System_Architecture.md`

# Kurulum — "Normal mi?" Akıllı Asistanı

## Gereksinimler
- Python 3.10+
- OpenAI API key (Assistants Platform erişimi olan)
- `pip install openai python-dotenv`
- Maskeleme katmanı için: `pip install transformers torch` (BERT NER modeli için)

## Adımlar

1. **Vector Store ve Assistant'ı oluştur**
   - `rag/pdfs/` klasöründeki 8 dosyayı bir Vector Store'a yükle.
   - `assistant/System_Instructions.md` içindeki metni Assistant'ın
     `instructions` alanına ver.
   - `tools: [{"type": "file_search"}]`, `tool_resources` ile vector store'u bağla.
   - Assistant seviyesinde sabit bir `response_format` **verme** — bu iki
     modlu mimaride şema her Run'da ayrı verilecek (bkz. `Assistant_Info.md`).
   - Oluşan Assistant ID ve Vector Store ID'yi `assistant/Assistant_Info.md`'ye yaz.

2. **Veri Maskeleme katmanını test et**
   ```bash
   cd masking
   python test.py
   ```
   İlk çalıştırmada `ner_mask.py` içindeki `savasy/bert-base-turkish-ner-cased`
   modeli indirilecektir (birkaç yüz MB, internet gerektirir).

3. **MOD 1'i test et (Semptom Çıkarımı)**
   - Maskelenmiş metni Thread'e mesaj olarak ekle.
   - Run'ı `response_format=normalmi_symptom_extraction`, `tool_choice="none"` ile başlat.
   - Dönen JSON'u `assistant/JSON_API_Contract.md`'deki şemayla doğrula.

4. **Backend Rule Engine'i bağla**
   - MOD 1'den dönen boolean/sayısal alanları (`siddetli_bas_agrisi`,
     `kanama_var_mi`, vb.) ACOG tabanlı kural motorunuza girdi olarak ver.
   - Rule Engine `risk_seviyesi` (kirmizi/sari/yesil/belirsiz) üretsin.

5. **MOD 2'yi test et (Risk Açıklama)**
   - Rule Engine çıktısını (`risk_seviyesi`, `semptom_ozeti`) yeni bir mesaj
     olarak aynı ya da yeni bir Thread'e gönder.
   - Run'ı `response_format=normalmi_risk_explanation`, `tool_choice="auto"` ile başlat.
   - Dönen `aciklama_metni`'ni mobil uygulamada uyarı kartı olarak göster.

## Sorun giderme
- **File Search hiçbir sonuç döndürmüyor:** Vector Store ID'nin Assistant'a
  doğru bağlandığından ve dosyaların "completed" durumunda olduğundan emin ol.
- **JSON şema hatası / eksik alan:** `strict: true` kullanıldığından ve
  `required` listesinin şemadaki TÜM alanları içerdiğinden emin ol.
- **NER modeli çok yavaş:** İlk çalıştırmadan sonra model yerelde
  cache'lenir; sonraki çalıştırmalar hızlanır.

