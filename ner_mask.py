from transformers import pipeline

# Model ilk çalıştırmada indirilecektir.
ner = pipeline(
    "ner",
    model="savasy/bert-base-turkish-ner-cased",
    aggregation_strategy="simple"
)


def mask_entities(text: str) -> str:
    """
    Metindeki kişi ve lokasyon bilgilerini maskeler.
    """

    entities = ner(text)
    print(entities)
    
    # Sağdan sola değiştiriyoruz ki indeksler bozulmasın
    for entity in sorted(entities, key=lambda x: x["start"], reverse=True):

        label = entity["entity_group"]

        if label == "PER":
            replacement = "[NAME]"

        elif label == "LOC":
            replacement = "[LOCATION]"

        else:
            continue

        text = (
            text[:entity["start"]]
            + replacement
            + text[entity["end"]:]
        )

    return text