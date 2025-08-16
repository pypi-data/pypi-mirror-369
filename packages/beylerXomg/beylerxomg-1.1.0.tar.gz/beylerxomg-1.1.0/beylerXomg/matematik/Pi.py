from decimal import Decimal, getcontext
import math

def hesapla(basamak: int):
    """
    basamak: kaç basamak hassasiyet istiyorsan
    return: Decimal tipinde pi değeri
    """
    getcontext().prec = basamak + 2  # 2 ekstra basamak, yuvarlama için
    pi = Decimal(0)
    k = 0
    while k < basamak * 10:  # yeterli iterasyon, basamak sayısına göre artırılabilir
        pi += (Decimal(-1)**k) / (2*k + 1)
        k += 1
    pi *= Decimal(4)
    return +pi  # unary plus ile context hassasiyetine göre yuvarlar
