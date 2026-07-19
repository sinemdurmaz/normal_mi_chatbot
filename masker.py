import re
from regex_mask import PHONE_PATTERN, EMAIL_PATTERN, TC_PATTERN
from ner_mask import mask_entities


def mask_text(text: str) -> str:

    # Regex ile maskele
    text = re.sub(PHONE_PATTERN, "[PHONE]", text)
    text = re.sub(EMAIL_PATTERN, "[EMAIL]", text)
    text = re.sub(TC_PATTERN, "[TC_ID]", text)

    # NER ile isim ve lokasyon
    text = mask_entities(text)

    return text