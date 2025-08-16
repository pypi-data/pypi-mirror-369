import pyphen


def spell_word(word, pause_duration=250):
    """Convierte una palabra en texto deletreado por sílabas con pausas."""
    dic = pyphen.Pyphen(lang="es_ES")

    silabas_texto = dic.inserted(word.lower())
    silabas = silabas_texto.split("-")

    if len(silabas) == 1 and "-" not in silabas_texto:
        return word.lower()

    deletreado = []

    for i, silaba in enumerate(silabas):
        if silaba.strip():
            deletreado.append(silaba)
            if i < len(silabas) - 1:
                pause_text = f'<break time="{pause_duration}ms"/>'
                deletreado.append(pause_text)

    return " ".join(deletreado)
