

__all__=["sifre","desifre"]
def sifre(metin, kaydirma):
    ALFABE_BUYUK = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ"
    ALFABE_KUCUK = "abcçdefgğhıijklmnoöprsştuüvyz"
    sonuc = ""
    for char in metin:
        if char in ALFABE_BUYUK:
            index = ALFABE_BUYUK.index(char)
            yeni_index = (index + kaydirma) % len(ALFABE_BUYUK)
            sonuc += ALFABE_BUYUK[yeni_index]
        elif char in ALFABE_KUCUK:
            index = ALFABE_KUCUK.index(char)
            yeni_index = (index + kaydirma) % len(ALFABE_KUCUK)
            sonuc += ALFABE_KUCUK[yeni_index]
        else:
            sonuc += char
    return sonuc

def desifre(metin, kaydirma):
    return sifre(metin, -kaydirma)  # Negatif kaydırma ile çözme

