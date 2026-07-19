# Prompt Examples — "Normal mi?" Akıllı Asistanı (v2 — İki Modlu)

---

## MOD 1 örnekleri (Semptom Çıkarımı)

### Örnek 1 — Preeklampsi paterni

**Kullanıcı girdisi (maskeleme sonrası):**
`32. haftadayım, iki gündür şiddetli baş ağrım var ve gözümde bulanıklık oluyor`

**Beklenen çıktı:**
```json
{
  "semptom_ozeti": "Şiddetli baş ağrısı ve bulanık görme",
  "gebelik_haftasi": 32,
  "kanama_var_mi": false, "kanama_miktari": null, "kanama_rengi": null,
  "siddetli_bas_agrisi": true,
  "gorme_bozuklugu": true,
  "el_yuz_sisligi_ani": false,
  "duzenli_kasilma_var_mi": false, "kasilma_sikligi_dakika": null,
  "su_gelmesi_var_mi": false,
  "bebek_hareketi_azaldi_mi": false,
  "ates_var_mi": false, "ates_derece": null,
  "karin_agrisi_var_mi": false, "karin_agrisi_siddeti": 0, "karin_agrisi_sure_saat": 0,
  "bulanti": false, "kusma": false,
  "anlasildi_mi": true, "kullanici_mesaji": null
}
```

### Örnek 2 — Kanama

**Kullanıcı girdisi:**
`az önce kırmızı renkli, adet gibi kanama başladı, karnım da kramp gibi ağrıyor`

**Beklenen çıktı (kısmi, ilgili alanlar):**
```json
{
  "semptom_ozeti": "Kırmızı renkli, yoğun kanama ve karın krampı",
  "kanama_var_mi": true,
  "kanama_miktari": "yogun",
  "kanama_rengi": "kirmizi",
  "karin_agrisi_var_mi": true,
  "karin_agrisi_siddeti": 6,
  "karin_agrisi_sure_saat": 0,
  "anlasildi_mi": true, "kullanici_mesaji": null
}
```

### Örnek 3 — Fallback (anlaşılamayan girdi)

**Kullanıcı girdisi:**
`bilmiyorum işte öyle bir hisim var`

**Beklenen çıktı:**
```json
{
  "semptom_ozeti": null, "gebelik_haftasi": null,
  "kanama_var_mi": false, "kanama_miktari": null, "kanama_rengi": null,
  "siddetli_bas_agrisi": false, "gorme_bozuklugu": false, "el_yuz_sisligi_ani": false,
  "duzenli_kasilma_var_mi": false, "kasilma_sikligi_dakika": null,
  "su_gelmesi_var_mi": false, "bebek_hareketi_azaldi_mi": false,
  "ates_var_mi": false, "ates_derece": null,
  "karin_agrisi_var_mi": false, "karin_agrisi_siddeti": 0, "karin_agrisi_sure_saat": 0,
  "bulanti": false, "kusma": false,
  "anlasildi_mi": false,
  "kullanici_mesaji": "Şikayetinizi biraz daha ayrıntılı tarif edebilir misiniz?"
}
```

### Örnek 4 — Halüsinasyon / varsayım testi (asistanın YAPMAMASI gereken)

**Kullanıcı girdisi:**
`karnım ağrıyor`

**Yanlış davranış:** `ates_var_mi: true` veya `kanama_var_mi: true` gibi kullanıcının söylemediği alanları doldurmak.

**Doğru davranış:** Sadece `karin_agrisi_var_mi: true` işaretlenir, diğer tüm ilişkisiz alanlar `false`/`null` kalır.

---

## MOD 2 örnekleri (Risk Açıklama)

### Örnek 5 — Kırmızı kod açıklaması

**Backend girdisi:**
```json
{ "risk_seviyesi": "kirmizi", "semptom_ozeti": "Şiddetli baş ağrısı ve bulanık görme, hafta 32" }
```

**Beklenen çıktı:**
```json
{
  "aciklama_metni": "Anlattığın şiddetli baş ağrısı ve bulanık görme birlikte değerlendirildiğinde acil bir durum olabilir. Lütfen hemen en yakın acil servise git ya da 112'yi ara. Bu bilgi bir teşhis değildir. Nihai değerlendirme backend Rule Engine tarafından yapılmıştır. Lütfen doktorunuzun önerilerini esas alınız."
}
```

### Örnek 6 — Yeşil kod açıklaması

**Backend girdisi:**
```json
{ "risk_seviyesi": "yesil", "semptom_ozeti": "Hafif mide bulantısı, 3 gündür, hafta 10" }
```

**Beklenen çıktı:**
```json
{
  "aciklama_metni": "Hamileliğin ilk dönemlerinde hafif mide bulantısı oldukça sık görülür ve genelde endişe verici değildir. Devam ederse bir sonraki kontrolünde bahsetmen yeterli olur. Bu bilgi bir teşhis değildir. Nihai değerlendirme backend Rule Engine tarafından yapılmıştır. Lütfen doktorunuzun önerilerini esas alınız."
}
```

### Örnek 7 — Belirsiz kod / File Search'te karşılığı olmayan durum

**Backend girdisi:**
```json
{ "risk_seviyesi": "belirsiz", "semptom_ozeti": "Sağ kolda karıncalanma, 1 gündür" }
```

**Beklenen çıktı:**
```json
{
  "aciklama_metni": "Bu konuda doğrulanmış bilgiye sahip değilim. Lütfen doktorunuza danışınız. Bu bilgi bir teşhis değildir. Nihai değerlendirme backend Rule Engine tarafından yapılmıştır. Lütfen doktorunuzun önerilerini esas alınız."
}
```

### Örnek 8 — İlaç sorusu (asistanın YAPMAMASI gereken)

**Kullanıcı MOD 1'de sorar:** `ne ilacı içmeliyim şu bulantı için?`

**Doğru davranış:** MOD 1 yalnızca semptomu çıkarır (`bulanti: true`), ilaç talebini JSON'a yansıtmaz, yorum yapmaz. İlaç önerisi hiçbir modda verilmez.
