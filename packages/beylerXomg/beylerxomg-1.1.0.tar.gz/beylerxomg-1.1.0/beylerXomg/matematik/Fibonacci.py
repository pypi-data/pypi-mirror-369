def hesapla(n, sonuc_liste=None):
    """
    n: üretilmesini istediğin Fibonacci sayısı adedi
    sonuc_liste: opsiyonel, eğer verilirse Fibonacci sayıları buraya eklenir ve döndürülür
    """
    a, b = 0, 1
    fibs = []
    
    for _ in range(n):
        fibs.append(a)
        a, b = b, a + b
    
    if sonuc_liste is not None:
        sonuc_liste.extend(fibs)
        return sonuc_liste
    else:
        for f in fibs:
            print(f)

