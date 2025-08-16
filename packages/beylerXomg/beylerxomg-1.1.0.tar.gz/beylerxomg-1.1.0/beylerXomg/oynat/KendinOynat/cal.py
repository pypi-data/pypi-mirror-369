__all__ = ["sesfile"]  # yine güvenlik için ekledik

def sesfile(dosya_yolu, sure=None):
    import pygame
    import time
    import os

    pygame.mixer.init()

    if not os.path.exists(dosya_yolu):
        raise FileNotFoundError(f"Ses dosyası bulunamadı: {dosya_yolu}")

    pygame.mixer.music.load(dosya_yolu)
    pygame.mixer.music.play()

    if sure is not None:
        time.sleep(sure)
        pygame.mixer.music.stop()
    else:
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)




