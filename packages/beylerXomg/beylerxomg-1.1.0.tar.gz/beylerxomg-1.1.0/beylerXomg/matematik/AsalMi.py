def hesapla(sayi: int) -> bool:
    if sayi <= 1:
        return False
    if sayi == 2:
        return True
    if sayi % 2 == 0:
        return False
    for i in range(3, int(sayi**0.5)+1, 2):
        if sayi % i == 0:
            return False
    return True
