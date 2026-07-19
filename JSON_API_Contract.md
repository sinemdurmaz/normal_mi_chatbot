# JSON API Kontratı — "Normal mi?" Akıllı Asistanı (v2 — İki Modlu)

İki mod, iki ayrı Structured Output şeması kullanır. Her ikisi de
`strict: true` ile tanımlanır; bu yüzden model şema dışına çıkamaz (eksik alan,
hayali enum değeri, fazladan alan mümkün değildir).

---

## 1) MOD 1 — Semptom Çıkarımı: `normalmi_symptom_extraction`

```json
{
  "name": "normalmi_symptom_extraction",
  "strict": true,
  "schema": {
    "type": "object",
    "properties": {
      "semptom_ozeti": { "type": ["string", "null"] },
      "gebelik_haftasi": { "type": ["integer", "null"] },
      "kanama_var_mi": { "type": "boolean" },
      "kanama_miktari": { "type": ["string", "null"] },
      "kanama_rengi": { "type": ["string", "null"] },
      "siddetli_bas_agrisi": { "type": "boolean" },
      "gorme_bozuklugu": { "type": "boolean" },
      "el_yuz_sisligi_ani": { "type": "boolean" },
      "duzenli_kasilma_var_mi": { "type": "boolean" },
      "kasilma_sikligi_dakika": { "type": ["integer", "null"] },
      "su_gelmesi_var_mi": { "type": "boolean" },
      "bebek_hareketi_azaldi_mi": { "type": "boolean" },
      "ates_var_mi": { "type": "boolean" },
      "ates_derece": { "type": ["number", "null"] },
      "karin_agrisi_var_mi": { "type": "boolean" },
      "karin_agrisi_siddeti": { "type": "integer" },
      "karin_agrisi_sure_saat": { "type": "integer" },
      "bulanti": { "type": "boolean" },
      "kusma": { "type": "boolean" },
      "anlasildi_mi": { "type": "boolean" },
      "kullanici_mesaji": { "type": ["string", "null"] }
    },
    "required": [
      "semptom_ozeti", "gebelik_haftasi", "kanama_var_mi", "kanama_miktari",
      "kanama_rengi", "siddetli_bas_agrisi", "gorme_bozuklugu", "el_yuz_sisligi_ani",
      "duzenli_kasilma_var_mi", "kasilma_sikligi_dakika", "su_gelmesi_var_mi",
      "bebek_hareketi_azaldi_mi", "ates_var_mi", "ates_derece", "karin_agrisi_var_mi",
      "karin_agrisi_siddeti", "karin_agrisi_sure_saat", "bulanti", "kusma",
      "anlasildi_mi", "kullanici_mesaji"
    ],
    "additionalProperties": false
  }
}
```

### Alan → RAG dosyası eşlemesi (Rule Engine'in kullanacağı mantık)

| Alan(lar) | İlgili RAG dosyası |
|---|---|
| `siddetli_bas_agrisi`, `gorme_bozuklugu`, `el_yuz_sisligi_ani` | `01_Preeclampsia.md` |
| `ates_var_mi`, `ates_derece`, `karin_agrisi_*`, bayılma/nefes (serbest metinde) | `02_Warning_Signs.md` |
| `kanama_var_mi`, `kanama_miktari`, `kanama_rengi` | `03_Bleeding.md` |
| `bebek_hareketi_azaldi_mi` | `04_Fetal_Movement.md` |
| `duzenli_kasilma_var_mi`, `kasilma_sikligi_dakika`, `su_gelmesi_var_mi` | `05_Labor_Signs.md` |
| `bulanti`, `kusma` (ve hafif/yaygın semptomlar) | `06_Common_Symptoms.md` |

### Örnek çıktı

```json
{
  "semptom_ozeti": "Şiddetli baş ağrısı ve bulanık görme",
  "gebelik_haftasi": 32,
  "kanama_var_mi": false,
  "kanama_miktari": null,
  "kanama_rengi": null,
  "siddetli_bas_agrisi": true,
  "gorme_bozuklugu": true,
  "el_yuz_sisligi_ani": false,
  "duzenli_kasilma_var_mi": false,
  "kasilma_sikligi_dakika": null,
  "su_gelmesi_var_mi": false,
  "bebek_hareketi_azaldi_mi": false,
  "ates_var_mi": false,
  "ates_derece": null,
  "karin_agrisi_var_mi": false,
  "karin_agrisi_siddeti": 0,
  "karin_agrisi_sure_saat": 0,
  "bulanti": false,
  "kusma": false,
  "anlasildi_mi": true,
  "kullanici_mesaji": null
}
```

### Fallback (anlaşılamayan girdi)

```json
{
  "semptom_ozeti": null,
  "gebelik_haftasi": null,
  "kanama_var_mi": false,
  "kanama_miktari": null,
  "kanama_rengi": null,
  "siddetli_bas_agrisi": false,
  "gorme_bozuklugu": false,
  "el_yuz_sisligi_ani": false,
  "duzenli_kasilma_var_mi": false,
  "kasilma_sikligi_dakika": null,
  "su_gelmesi_var_mi": false,
  "bebek_hareketi_azaldi_mi": false,
  "ates_var_mi": false,
  "ates_derece": null,
  "karin_agrisi_var_mi": false,
  "karin_agrisi_siddeti": 0,
  "karin_agrisi_sure_saat": 0,
  "bulanti": false,
  "kusma": false,
  "anlasildi_mi": false,
  "kullanici_mesaji": "Şikayetinizi biraz daha ayrıntılı tarif edebilir misiniz?"
}
```

---

## 2) MOD 2 — Risk Açıklama: `normalmi_risk_explanation` (yeni eklendi)

MOD 1 şemasında risk kararı yoktu — bu doğru, çünkü karar backend Rule
Engine'e ait. Ama MOD 2'nin de programatik işlenebilmesi için ayrı, minimal
bir şema gerekiyor. Zorunlu uyarı cümlesi dahil, kullanıcıya gösterilecek
**tüm** metin `aciklama_metni` içinde olmalı.

```json
{
  "name": "normalmi_risk_explanation",
  "strict": true,
  "schema": {
    "type": "object",
    "properties": {
      "aciklama_metni": { "type": "string" }
    },
    "required": ["aciklama_metni"],
    "additionalProperties": false
  }
}
```

### MOD 2 girişi (backend → Assistant)

Backend, Rule Engine kararını MOD 2 run'ının kullanıcı mesajı olarak gönderir, örnek:

```json
{
  "risk_seviyesi": "kirmizi",
  "semptom_ozeti": "Şiddetli baş ağrısı ve bulanık görme, hafta 32"
}
```

### MOD 2 örnek çıktı

```json
{
  "aciklama_metni": "Anlattığın şiddetli baş ağrısı ve bulanık görme birlikte değerlendirildiğinde acil bir durum olabilir. Lütfen hemen en yakın acil servise git ya da 112'yi ara. Bu bilgi bir teşhis değildir. Nihai değerlendirme backend Rule Engine tarafından yapılmıştır. Lütfen doktorunuzun önerilerini esas alınız."
}
```

---

## Assistants Platform'da uygulama

Her iki şema de aynı Assistant'a, **Run seviyesinde** `response_format` olarak
verilir (Assistant oluşturulurken sabit bir `response_format` seçilmez):

```python
# MOD 1
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=ASSISTANT_ID,
    response_format={"type": "json_schema", "json_schema": MOD1_SCHEMA},
    tool_choice="none",  # File Search'i bu modda tetikleme
)

# MOD 2
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=ASSISTANT_ID,
    response_format={"type": "json_schema", "json_schema": MOD2_SCHEMA},
    tool_choice="auto",  # File Search kullanılabilir
)
```
