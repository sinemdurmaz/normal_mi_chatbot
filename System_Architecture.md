# Sistem Mimarisi — "Normal mi?" Akıllı Asistanı

## Genel Bakış

Sistem, LLM'in tıbbi risk kararı vermesini engelleyen, iki modlu bir hibrit
mimari kullanır:

- **MOD 1 (LLM):** Serbest metni yapılandırılmış semptom verisine çevirir. Risk kararı vermez.
- **Backend Rule Engine (kod, LLM değil):** ACOG tabanlı kurallara göre risk seviyesini (kırmızı/sarı/yeşil/belirsiz) belirler.
- **MOD 2 (LLM):** Backend kararını, File Search'teki referans dokümanlarla birlikte, empatik bir dille kullanıcıya açıklar. Kararı değiştiremez.

## Akış Diyagramı

```mermaid
flowchart TD
    A["Anne / Kullanıcı<br/>Doğal dilde şikayet yazar"] --> B["Veri Maskeleme Katmanı (KVKK)<br/>masking/masker.py<br/>regex + NER (isim, telefon, e-posta, TC no, lokasyon)"]
    B --> C["MOD 1 — Semptom Çıkarımı (LLM)<br/>tool_choice: none<br/>response_format: normalmi_symptom_extraction"]
    C --> D{"anlasildi_mi?"}
    D -- "false" --> E["Netleştirme sorusu<br/>(kullanici_mesaji)"]
    E --> A
    D -- "true" --> F["Backend Rule Engine<br/>(kod — ACOG tabanlı eşik kuralları)<br/>booleans + sayısal alanlar → risk_seviyesi"]
    F --> G["risk_seviyesi:<br/>kirmizi / sari / yesil / belirsiz"]
    G --> H["MOD 2 — Risk Açıklama (LLM)<br/>tool_choice: auto<br/>File Search → rag/pdfs/01-08<br/>response_format: normalmi_risk_explanation"]
    H --> I["aciklama_metni<br/>(+ zorunlu uyarı cümlesi)"]
    I --> J["Mobil Uygulama<br/>Uyarı kartı / sonuç ekranı"]

    style A fill:#eaf2fb,stroke:#2b6cb0
    style B fill:#fbefe3,stroke:#c05621
    style C fill:#e6f4ea,stroke:#2f855a
    style F fill:#fdf6e3,stroke:#b7791f
    style H fill:#e6f4ea,stroke:#2f855a
    style J fill:#eaf2fb,stroke:#2b6cb0
    style D fill:#fef3d6,stroke:#b7791f
```

## Bileşen sorumlulukları

| Bileşen | Sorumluluk | Risk kararı verir mi? |
|---|---|---|
| `masking/` | Kişisel veriyi LLM'e ulaşmadan temizler | Hayır |
| MOD 1 (LLM) | Serbest metni yapılandırılmış veriye çevirir | **Hayır** |
| Backend Rule Engine | ACOG kurallarına göre risk seviyesi belirler | **Evet — tek karar verici** |
| MOD 2 (LLM) | Kararı File Search referanslarıyla açıklar | Hayır (sadece iletir) |
| Mobil uygulama | Sonucu kullanıcıya gösterir | Hayır |

Bu ayrım, görev tanımındaki "yapay zekayı tamamen serbest bırakmak yerine
hibrit sistem" gereksinimini karşılar: LLM hiçbir noktada tek başına tıbbi
karar vermez.

## Neden iki ayrı LLM çağrısı (MOD 1 / MOD 2) ve tek çağrı değil?

Tek çağrıda hem çıkarım hem açıklama yaptırmak, modelin aynı anda hem veri
çıkarıp hem de örtük şekilde risk değerlendirmesi yapmasına (ör. "bu ciddi
görünüyor" gibi sızıntılara) yol açabilir. İki ayrı çağrı ve iki ayrı şema,
"LLM sadece anlıyor, karar motoru karar veriyor" ayrımını API seviyesinde
zorunlu kılar.

## İlgili dosyalar
- Kurulum adımları → `Installation.md`
- Genel teknik özet → `Technical_Documentation.md`
- JSON şemaları → `../../assistant/JSON_API_Contract.md`
