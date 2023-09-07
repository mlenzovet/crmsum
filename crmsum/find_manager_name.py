from natasha import (
    Segmenter,

    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,

    PER,

    Doc
)


def find_manager_name(text, managers_list):
    """
    Находит имя менеджера в тексте и сопоставляет его со списком менеджеров.

    Аргументы:
    text (str): Текст в свободной форме, в котором нужно найти имя менеджера. Например: "расскажи, что Ева делала сегодня по Трансхренмаш."
    managers_list (list): Список имен менеджеров, с которыми нужно сопоставить найденное имя.

    Возвращает:
    manager_name (str): Найденное имя менеджера или "Ева", если имя менеджера не найдено.
    """

    emb = NewsEmbedding()
    ner_tagger = NewsNERTagger(emb)
    morph_tagger = NewsMorphTagger(emb)
    segmenter = Segmenter()

    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_ner(ner_tagger)

    list_person = []
    for span in doc.spans:
        if span.type == PER:
            list_person.append(span.tokens[0].text)

    return [name if name in managers_list else 'Ева' for name in list_person]
