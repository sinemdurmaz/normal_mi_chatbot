# Teknik Dokümantasyon — "Normal mi?" Akıllı Asistanı

## Proje özeti

"Normal mi?", KaraLabs Mother & Child Platform içinde çalışan, hamile
kullanıcıların şikayetlerini ön-analiz eden hibrit bir yapay zeka modülüdür.
Yapay zeka yalnızca dili anlar; tıbbi karar backend'deki ACOG tabanlı kural
motoruna aittir.

## Klasör yapısı

```
NORMALMI-AI/
├── assistant/
│   ├── Assistant_Info.md        → Assistant/Vector Store kimlik bilgileri, kurulum özeti
│   ├── JSON_API_Contract.md     → MOD 1 ve MOD 2 JSON şemaları + örnekler
│   ├── Prompt_Examples.md       → Few-shot test örnekleri (her iki mod)
│   └── System_Instructions.md   → Assistant'a verilecek tam sistem talimatı
├── masking/
│   ├── regex_mask.py            → Telefon, e-posta, TC no regex'leri
│   ├── ner_mask.py               → BERT tabanlı Türkçe NER (isim, lokasyon)
│   ├── gliner_mask.py            → Alternatif/yedek NER modeli (GLiNER, opsiyonel)
│   ├── masker.py                  → regex + NER'i birleştiren ana fonksiyon
│   └── test.py                    → Komut satırından hızlı test
└── rag/
    ├── docs/
    │   ├── Installation.md           → Kurulum adımları
    │   ├── System_Architecture.md    → Mimari + flowchart
    │   └── Technical_Documentation.md → (bu dosya)
    └── pdfs/                          → File Search'e yüklenecek 8 referans doküman
        ├── 01_Preeclampsia.md
        ├── 02_Warning_Signs.md
        ├── 03_Bleeding.md
        ├── 04_Fetal_Movement.md
        ├── 05_Labor_Signs.md
        ├── 06_Common_Symptoms.md
        ├── 07_Glossary.md
        └── 08_System_Policies.md
```

## Teknoloji seçimleri

| Katman | Teknoloji | Neden |
|---|---|---|
| Veri maskeleme | Regex + `savasy/bert-base-turkish-ner-cased` | Türkçe'ye özel eğitilmiş NER modeli, isim/lokasyon tespiti için regex'ten daha güvenilir |
| LLM orkestrasyon | OpenAI Assistants Platform | Görev tanımının doğrudan istediği platform; File Search ve Structured Outputs yerleşik olarak destekleniyor |
| Bilgi tabanı (RAG) | OpenAI Vector Store + File Search | Yönetilen embedding/arama altyapısı, ayrı bir vektör veritabanı kurmaya gerek bırakmıyor |
| Çıktı garantisi | Structured Outputs (`json_schema`, `strict: true`) | Backend'in JSON parse hatası almasını API seviyesinde engelliyor |
| Risk kararı | Backend Rule Engine (LLM dışı, deterministik kod) | Tıbbi kararın modelin "halüsinasyonuna" bağlı olmamasını garanti ediyor |

## Veri akışı — kısa özet

1. Kullanıcı şikayetini yazar.
2. `masking/masker.py` kişisel verileri temizler (bu adım OpenAI'ye hiç gitmez).
3. MOD 1 (LLM) temizlenmiş metni `normalmi_symptom_extraction` şemasında JSON'a çevirir.
4. Backend Rule Engine bu JSON'daki boolean/sayısal alanları ACOG eşikleriyle karşılaştırıp `risk_seviyesi` üretir.
5. MOD 2 (LLM), File Search ile `rag/pdfs/` içindeki ilgili dosyayı bulup kararı empatik bir dille açıklar (`normalmi_risk_explanation` şeması).
6. Mobil uygulama `aciklama_metni`'ni uyarı kartı olarak gösterir.

Detaylı akış diyagramı için → `System_Architecture.md`.

## Bilinen sınırlamalar / gelecek işler

- `gliner_mask.py` şu an `masker.py` tarafından çağrılmıyor; NER için tek
  kaynak `ner_mask.py` (BERT). GLiNER, çok-dilli senaryolar için ileride
  alternatif/yedek olarak değerlendirilebilir.
- `rag/pdfs/08_System_Policies.md` İngilizce ve benzerlik tabanlı aramada
  her zaman tetiklenmeyebilir; kritik güvenlik kuralları zaten
  `System_Instructions.md`'de birebir yer alıyor, bu dosya ek referans
  niteliğindedir.
- OpenAI Assistants API 26 Ağustos 2026'da kullanımdan kaldırılacak; teslim
  tarihinden (20.07.2026) sonraki bakım için Responses API'ye geçiş
  planlanmalı.
