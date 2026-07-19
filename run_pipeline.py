"""
rule_engine.py
---------------
Backend Rule Engine — "Normal mi?" Akıllı Asistanı

Bu modül LLM DEĞİLDİR. MOD 1'den (Semptom Çıkarımı) dönen yapılandırılmış
JSON'u alır, rag/pdfs/01-06 dosyalarındaki ACOG tabanlı eşiklere göre
deterministik bir risk_seviyesi üretir. Sistemdeki TEK risk karar vericisi
budur; LLM (MOD 1 veya MOD 2) hiçbir noktada bu kararı vermez ya da değiştirmez.

Girdi: assistant/JSON_API_Contract.md'deki normalmi_symptom_extraction şemasına
       uygun bir dict.
Çıktı: {
    "risk_seviyesi": "kirmizi" | "sari" | "yesil" | "belirsiz",
    "tetiklenen_kural": "<insan-okunabilir kısa gerekçe, iç log/denetim için>",
    "kaynak_dosya": "<hangi rag/pdfs dosyasına dayandığı>",
    "semptom_ozeti": "<MOD 2'ye aynen aktarılacak>"
}

Her eşiğin hangi rag/pdfs dosyasından geldiği yorum satırlarında belirtilmiştir;
dosyalar değişirse buradaki sabitler de güncellenmelidir (tek doğruluk kaynağı
rag/pdfs olmalı — bu dosya onun kod haline getirilmiş yansımasıdır).
"""

from dataclasses import dataclass
from typing import Optional


# Öncelik sırası: kirmizi > sari > yesil > belirsiz
RISK_ORDER = {"kirmizi": 3, "sari": 2, "yesil": 1, "belirsiz": 0}


@dataclass
class RiskSonucu:
    risk_seviyesi: str
    tetiklenen_kural: str
    kaynak_dosya: str


def _en_yuksek(sonuclar: list[RiskSonucu]) -> RiskSonucu:
    return max(sonuclar, key=lambda r: RISK_ORDER[r.risk_seviyesi])


# ---------------------------------------------------------------------------
# 01_Preeclampsia.md
# ---------------------------------------------------------------------------
def _preeklampsi(v: dict) -> Optional[RiskSonucu]:
    bas_agrisi = v.get("siddetli_bas_agrisi", False)
    gorme = v.get("gorme_bozuklugu", False)
    sislik = v.get("el_yuz_sisligi_ani", False)

    if not (bas_agrisi or gorme or sislik):
        return None

    # "Şiddetli baş ağrısı ve görme bozukluğunun aynı anda görülmesi
    #  acil tıbbi değerlendirme gerektirebilir." (01_Preeclampsia.md)
    if bas_agrisi and (gorme or sislik):
        return RiskSonucu("kirmizi", "Şiddetli baş ağrısı + görme bozukluğu/ani şişlik birlikte", "01_Preeclampsia.md")

    # "Görme bozukluğu veya ani şişliğin eşlik etmediği hafif/orta şiddetli
    #  izole baş ağrıları tansiyon takibi gerektirir." (01_Preeclampsia.md)
    if bas_agrisi or gorme or sislik:
        return RiskSonucu("sari", "İzole şiddetli baş ağrısı / görme bozukluğu / ani şişlik", "01_Preeclampsia.md")

    return None


# ---------------------------------------------------------------------------
# 02_Warning_Signs.md  (ateş, karın ağrısı)
# ---------------------------------------------------------------------------
ATES_KIRMIZI_ESIK = 38.5  # "Yüksek Ateş: belirgin şekilde yükselen ve düşmeyen ateş"
KARIN_AGRISI_KIRMIZI_ESIK = 8  # 0-10 skala, "şiddetli, bıçak saplanır tarzda"
KARIN_AGRISI_SARI_ESIK = 4     # "orta/hafif... dinlenmekle geçmeyen kramplar"
KARIN_AGRISI_SARI_SURE_SAAT = 6


def _uyari_bulgulari(v: dict) -> Optional[RiskSonucu]:
    ates_var = v.get("ates_var_mi", False)
    ates_derece = v.get("ates_derece")
    karin_var = v.get("karin_agrisi_var_mi", False)
    karin_siddet = v.get("karin_agrisi_siddeti", 0) or 0
    karin_sure = v.get("karin_agrisi_sure_saat", 0) or 0

    if ates_var and ates_derece is not None and ates_derece >= ATES_KIRMIZI_ESIK:
        return RiskSonucu("kirmizi", f"Yüksek ateş ({ates_derece}°C)", "02_Warning_Signs.md")

    if karin_var and karin_siddet >= KARIN_AGRISI_KIRMIZI_ESIK:
        return RiskSonucu("kirmizi", f"Şiddetli karın ağrısı (siddet={karin_siddet}/10)", "02_Warning_Signs.md")

    if ates_var:
        return RiskSonucu("sari", "Hafif ateş", "02_Warning_Signs.md")

    if karin_var and karin_siddet >= KARIN_AGRISI_SARI_ESIK and karin_sure >= KARIN_AGRISI_SARI_SURE_SAAT:
        return RiskSonucu("sari", f"Orta şiddette, uzun süreli karın ağrısı ({karin_sure} saat)", "02_Warning_Signs.md")

    if karin_var:
        return RiskSonucu("sari", "Hafif/orta karın ağrısı, yakın takip", "02_Warning_Signs.md")

    return None


# ---------------------------------------------------------------------------
# 03_Bleeding.md
# ---------------------------------------------------------------------------
KANAMA_YOGUN_DEGERLER = {"yogun", "bol", "adet gibi", "coklu"}
KANAMA_HAFIF_DEGERLER = {"hafif", "az", "lekelenme", "damla"}


def _kanama(v: dict) -> Optional[RiskSonucu]:
    kanama_var = v.get("kanama_var_mi", False)
    if not kanama_var:
        return None

    miktar = (v.get("kanama_miktari") or "").strip().lower()
    karin_var = v.get("karin_agrisi_var_mi", False)

    # "Belirgin miktarda yoğun kanamalar... veya kanamaya eşlik eden şiddetli
    #  karın ağrısı acil değerlendirme gerektirir." (03_Bleeding.md)
    if miktar in KANAMA_YOGUN_DEGERLER or karin_var:
        return RiskSonucu("kirmizi", f"Yoğun kanama ve/veya eşlik eden karın ağrısı (miktar={miktar or 'belirtilmemis'})", "03_Bleeding.md")

    if miktar in KANAMA_HAFIF_DEGERLER or miktar == "":
        return RiskSonucu("sari", "Hafif lekelenme, yakın takip", "03_Bleeding.md")

    # Tanınmayan bir miktar ifadesi geldiyse temkinli ol, sarı ver.
    return RiskSonucu("sari", f"Kanama bildirildi, miktar sınıflandırılamadı ({miktar})", "03_Bleeding.md")


# ---------------------------------------------------------------------------
# 04_Fetal_Movement.md
# ---------------------------------------------------------------------------
FETAL_KRITIK_HAFTA = 28  # "28. gebelik haftasından itibaren..."


def _fetal_hareket(v: dict) -> Optional[RiskSonucu]:
    azaldi = v.get("bebek_hareketi_azaldi_mi", False)
    if not azaldi:
        return None

    hafta = v.get("gebelik_haftasi")
    if hafta is None or hafta >= FETAL_KRITIK_HAFTA:
        return RiskSonucu("kirmizi", f"Bebek hareketlerinde azalma (hafta={hafta})", "04_Fetal_Movement.md")

    return RiskSonucu("sari", f"Bebek hareketlerinde azalma, {FETAL_KRITIK_HAFTA}. haftadan erken", "04_Fetal_Movement.md")


# ---------------------------------------------------------------------------
# 05_Labor_Signs.md
# ---------------------------------------------------------------------------
PRETERM_HAFTA_SINIRI = 37
KASILMA_SIK_ESIK_DAKIKA = 10  # "düzenli ve giderek sıklaşan aralıklarla"


def _dogum_belirtileri(v: dict) -> Optional[RiskSonucu]:
    su_geldi = v.get("su_gelmesi_var_mi", False)
    kasilma = v.get("duzenli_kasilma_var_mi", False)
    siklik = v.get("kasilma_sikligi_dakika")
    hafta = v.get("gebelik_haftasi")

    # "Amniyon zarının yırtılması... gebelik haftasına bakılmaksızın
    #  enfeksiyon riski ve doğumun başlaması açısından önemlidir." (05_Labor_Signs.md)
    if su_geldi:
        return RiskSonucu("kirmizi", "Su gelmesi / amniyon sıvısı", "05_Labor_Signs.md")

    if kasilma:
        preterm = hafta is not None and hafta < PRETERM_HAFTA_SINIRI
        sik = siklik is not None and siklik <= KASILMA_SIK_ESIK_DAKIKA
        if preterm and sik:
            return RiskSonucu("kirmizi", f"Düzenli, sık kasılma (hafta={hafta}, siklik={siklik} dk) — erken doğum şüphesi", "05_Labor_Signs.md")
        return RiskSonucu("sari", f"Düzenli kasılma (hafta={hafta}, siklik={siklik} dk)", "05_Labor_Signs.md")

    return None


# ---------------------------------------------------------------------------
# 06_Common_Symptoms.md
# ---------------------------------------------------------------------------
KUSMA_SARI_SURE_SAAT = 24  # "sıvı tutamama, 24 saatten uzun" örnek eşiği


def _yaygin_semptomlar(v: dict) -> Optional[RiskSonucu]:
    bulanti = v.get("bulanti", False)
    kusma = v.get("kusma", False)
    if not (bulanti or kusma):
        return None
    # Şema şu an kusmanın süresini/şiddetini ayrı bir alanla tutmuyor;
    # bu yüzden bulantı/kusma varlığı tek başına yeşil kabul edilir.
    # (bkz. Bilinen Sınırlamalar — Technical_Documentation.md)
    return RiskSonucu("yesil", "Bulantı/kusma, yaygın gebelik semptomu", "06_Common_Symptoms.md")


# ---------------------------------------------------------------------------
# Ana fonksiyon
# ---------------------------------------------------------------------------

_MODULLER = [_preeklampsi, _uyari_bulgulari, _kanama, _fetal_hareket, _dogum_belirtileri, _yaygin_semptomlar]

_TUM_BOOLEAN_ALANLAR = [
    "kanama_var_mi", "siddetli_bas_agrisi", "gorme_bozuklugu", "el_yuz_sisligi_ani",
    "duzenli_kasilma_var_mi", "su_gelmesi_var_mi", "bebek_hareketi_azaldi_mi",
    "ates_var_mi", "karin_agrisi_var_mi", "bulanti", "kusma",
]


def evaluate_risk(mod1_ciktisi: dict) -> dict:
    """
    MOD 1'den dönen normalmi_symptom_extraction JSON'unu değerlendirir.
    Bu fonksiyon LLM çağırmaz; tamamen deterministiktir.
    """
    if not mod1_ciktisi.get("anlasildi_mi", False):
        # anlasildi_mi false ise Rule Engine hiç çağrılmamalı; bu bir güvenlik ağı.
        return {
            "risk_seviyesi": "belirsiz",
            "tetiklenen_kural": "anlasildi_mi=false — Rule Engine çağrılmamalıydı",
            "kaynak_dosya": None,
            "semptom_ozeti": mod1_ciktisi.get("semptom_ozeti"),
        }

    sonuclar = [modul(mod1_ciktisi) for modul in _MODULLER]
    sonuclar = [s for s in sonuclar if s is not None]

    if sonuclar:
        en_yuksek = _en_yuksek(sonuclar)
        return {
            "risk_seviyesi": en_yuksek.risk_seviyesi,
            "tetiklenen_kural": en_yuksek.tetiklenen_kural,
            "kaynak_dosya": en_yuksek.kaynak_dosya,
            "semptom_ozeti": mod1_ciktisi.get("semptom_ozeti"),
        }

    # Hiçbir boolean alan True değil ama anlasildi_mi=true ve bir semptom_ozeti var:
    # MOD 1 bir şikayet algıladı ama bu, yapılandırılmış (rag/pdfs'e karşılık gelen)
    # bir kategoriye düşmedi. Halüsinasyon riskini önlemek için "belirsiz" dönülür.
    herhangi_alan_true = any(mod1_ciktisi.get(alan, False) for alan in _TUM_BOOLEAN_ALANLAR)
    if not herhangi_alan_true and mod1_ciktisi.get("semptom_ozeti"):
        return {
            "risk_seviyesi": "belirsiz",
            "tetiklenen_kural": "Semptom tanımlandı ama bilinen kategorilerden hiçbirine uymuyor",
            "kaynak_dosya": None,
            "semptom_ozeti": mod1_ciktisi.get("semptom_ozeti"),
        }

    return {
        "risk_seviyesi": "belirsiz",
        "tetiklenen_kural": "Hiçbir semptom alanı işaretlenmedi",
        "kaynak_dosya": None,
        "semptom_ozeti": mod1_ciktisi.get("semptom_ozeti"),
    }
