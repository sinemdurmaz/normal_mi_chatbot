# Assistant Info — "Normal mi?" Akıllı Asistanı

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

## Yazılım ekibine teslim edilecekler (görev tanımı madde 5)

1. **Canlı Assistant ID** — yukarıdaki tablo
2. **Akış diyagramı** — `rag/docs/System_Architecture.md` içindeki flowchart
3. **JSON API Kontratı** — `assistant/JSON_API_Contract.md`
