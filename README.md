# Normal Mi Akıllı Asistanı
Mother &amp; Child Platform projesi "Normal mi?" Akıllı Asistanı için gelişmiş bir hibrit yapay zeka prototipi (Open Ai Assistant Platform için uygun şekilde tasarlanmıştır.)

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

