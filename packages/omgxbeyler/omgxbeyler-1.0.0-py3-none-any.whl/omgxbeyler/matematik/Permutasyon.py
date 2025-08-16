import itertools

def hesapla(s: str, sonuc_liste=None):
    """
    s: permütasyonu alınacak string
    sonuc_liste: opsiyonel, eğer verilirse permütasyonlar buraya eklenir ve döndürülür
    """
    perms = [''.join(p) for p in itertools.permutations(s)]
    
    if sonuc_liste is not None:
        sonuc_liste.extend(perms)
        return sonuc_liste
    else:
        for p in perms:
            print(p)
