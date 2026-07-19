"""
test_rule_engine.py
---------------------
Prompt_Examples.md'deki MOD 1 örnekleriyle tutarlılığı doğrular.
Çalıştırma: python test_rule_engine.py
"""

from rule_engine import evaluate_risk

BOS_SABLON = {
    "semptom_ozeti": None, "gebelik_haftasi": None,
    "kanama_var_mi": False, "kanama_miktari": None, "kanama_rengi": None,
    "siddetli_bas_agrisi": False, "gorme_bozuklugu": False, "el_yuz_sisligi_ani": False,
    "duzenli_kasilma_var_mi": False, "kasilma_sikligi_dakika": None,
    "su_gelmesi_var_mi": False, "bebek_hareketi_azaldi_mi": False,
    "ates_var_mi": False, "ates_derece": None,
    "karin_agrisi_var_mi": False, "karin_agrisi_siddeti": 0, "karin_agrisi_sure_saat": 0,
    "bulanti": False, "kusma": False,
    "anlasildi_mi": True, "kullanici_mesaji": None,
}


def senaryo(**degisiklikler):
    d = dict(BOS_SABLON)
    d.update(degisiklikler)
    return d


TESTLER = [
    (
        "Preeklampsi paterni (Prompt_Examples #1) -> kirmizi",
        senaryo(semptom_ozeti="Şiddetli baş ağrısı ve bulanık görme", gebelik_haftasi=32,
                siddetli_bas_agrisi=True, gorme_bozuklugu=True),
        "kirmizi",
    ),
    (
        "İzole şiddetli baş ağrısı -> sari",
        senaryo(semptom_ozeti="Şiddetli baş ağrısı", siddetli_bas_agrisi=True),
        "sari",
    ),
    (
        "Yoğun kanama + karın ağrısı (Prompt_Examples #2) -> kirmizi",
        senaryo(semptom_ozeti="Kırmızı renkli, yoğun kanama ve karın krampı",
                kanama_var_mi=True, kanama_miktari="yogun", kanama_rengi="kirmizi",
                karin_agrisi_var_mi=True, karin_agrisi_siddeti=6),
        "kirmizi",
    ),
    (
        "Hafif lekelenme -> sari",
        senaryo(semptom_ozeti="Hafif lekelenme", kanama_var_mi=True, kanama_miktari="hafif"),
        "sari",
    ),
    (
        "Bebek hareketi azalması, hafta 32 (JSON_API_Contract örnek 3) -> kirmizi",
        senaryo(semptom_ozeti="Bebek hareketlerinde azalma", gebelik_haftasi=32, bebek_hareketi_azaldi_mi=True),
        "kirmizi",
    ),
    (
        "Bebek hareketi azalması, hafta 20 -> sari",
        senaryo(semptom_ozeti="Bebek hareketlerinde azalma", gebelik_haftasi=20, bebek_hareketi_azaldi_mi=True),
        "sari",
    ),
    (
        "Su gelmesi -> kirmizi",
        senaryo(semptom_ozeti="Su geldi", gebelik_haftasi=30, su_gelmesi_var_mi=True),
        "kirmizi",
    ),
    (
        "Preterm sık kasılma (hafta 30, 8 dk) -> kirmizi",
        senaryo(semptom_ozeti="Sık kasılma", gebelik_haftasi=30, duzenli_kasilma_var_mi=True, kasilma_sikligi_dakika=8),
        "kirmizi",
    ),
    (
        "Term kasılma (hafta 39, 15 dk) -> sari",
        senaryo(semptom_ozeti="Kasılma", gebelik_haftasi=39, duzenli_kasilma_var_mi=True, kasilma_sikligi_dakika=15),
        "sari",
    ),
    (
        "Yüksek ateş -> kirmizi",
        senaryo(semptom_ozeti="Ateşim çok yüksek", ates_var_mi=True, ates_derece=39.0),
        "kirmizi",
    ),
    (
        "Hafif ateş -> sari",
        senaryo(semptom_ozeti="Hafif ateşim var", ates_var_mi=True, ates_derece=37.6),
        "sari",
    ),
    (
        "Hafif mide bulantısı (JSON_API_Contract senaryo 1) -> yesil",
        senaryo(semptom_ozeti="mide bulantisi", bulanti=True),
        "yesil",
    ),
    (
        "Bilinmeyen/kategorize edilemeyen semptom (kol karıncalanması) -> belirsiz",
        senaryo(semptom_ozeti="sirt agrisi sag tarafta batici"),
        "belirsiz",
    ),
    (
        "anlasildi_mi=false -> belirsiz",
        senaryo(anlasildi_mi=False, semptom_ozeti=None, kullanici_mesaji="Biraz daha anlatır mısın?"),
        "belirsiz",
    ),
]


def main():
    basarili, basarisiz = 0, 0
    for isim, girdi, beklenen in TESTLER:
        sonuc = evaluate_risk(girdi)
        ok = sonuc["risk_seviyesi"] == beklenen
        basarili += ok
        basarisiz += not ok
        durum = "OK  " if ok else "FAIL"
        print(f"[{durum}] {isim}\n       beklenen={beklenen}  bulunan={sonuc['risk_seviyesi']}  ({sonuc['tetiklenen_kural']})")
    print(f"\n{basarili} basarili, {basarisiz} basarisiz / {len(TESTLER)} test")


if __name__ == "__main__":
    main()
