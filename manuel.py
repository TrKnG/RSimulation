### manuel.py

import threading
import time
import tkinter as tk

start = 0
ara = 0
gec = 0
end = 0

update_queue = []  # Güncelleme sırasını tutacak liste

# Tkinter penceresi oluşturma
root = tk.Tk()
root.title("Restoran Simülasyonu")

# Canvas oluşturma
canvas = tk.Canvas(root, width=1280, height=720)
canvas.pack()

# Güncelleme aralığı (ms)
UPDATE_INTERVAL = 100  # 100 ms = 0.1 s

# Restoran değişkenleri
bos_masalar = set(range(1, 7))
masa_renkleri = {i: "white" for i in range(1, 7)}  # Masa renkleri dict
musteri_sayaci = 1
musteriler = []
bekleyen_musteriler = []
kalan_musteriler = []
giden_musteriler = []
siparis_bekleyen_musteriler = []
siparis_bekleyen_musteriler_onay = []
yemek_bekleyen_musteriler = []
yemek_bekleyen_musteriler_onay = []
yemek_yiyen_musteriler = []
kasa_bekleyen_musteriler = []
kasa_bekleyen_musteriler_onay = []

# Masaların durumu
masa_durumu = {}

# Garson ve aşçıların konumları
garson1_pos = (1150, 50)
garson2_pos = (1150, 100)
garson3_pos = (1150, 150)
asci1_pos = (50, 600)
asci2_pos = (100, 600)
kasa_pos = (1150, 600)
bekleyen_musteri_pos = (600, 50)

garsonlar = [
    {"aktif": False, "obje": None, "isim": "Garson_1", "pozisyon": garson1_pos},
    {"aktif": False, "obje": None, "isim": "Garson_2", "pozisyon": garson2_pos},
    {"aktif": False, "obje": None, "isim": "Garson_3", "pozisyon": garson3_pos}
]

ascilar = [{"aktif": False, "obje": None, "isim": "Aşçı_1", "pozisyon": asci1_pos},
           {"aktif": False, "obje": None, "isim": "Aşçı_2", "pozisyon": asci2_pos}]

kasa = {"aktif": False, "obje": None, "pozisyon": kasa_pos, "isim": "Kasa_1"}

# Semaforlar
garson_sem = threading.Semaphore(value=3)  # Aynı anda 3 garsona izin verir
asci_sem = threading.Semaphore(value=2)  # Aynı anda 2 aşçıya izin verir
bekleyen_sem = threading.Semaphore(value=3)  # Bekleyen müşterilere güvenli erişim için semafor

bekleyen_musteri_text = None  # Bekleyen müşteri sayısını gösteren etiket

# Döngü durumu kontrolü için değişken
running = False

# Geçen zamanı tutacak global değişken
gecen_zaman = 0.0

# Etiket (label) oluşturma
gecen_zaman_label = tk.Label(root, text="Geçen Zaman: 0 saniye", font=("Helvetica", 12))
gecen_zaman_label.place(x=1100, y=10)


def dosyaya_yaz(veri, dosya_yolu='log.txt'):
    with open(dosya_yolu, 'a') as dosya:
        dosya.write(veri + '\n')


def update_gui_elements():
    for update in update_queue:
        func, args = update
        func(*args)
    update_queue.clear()  # Güncelleme listesini temizle


def update_gui():
    update_gui_elements()  # GUI elemanlarını güncelle
    draw_bekleyen_musteri()  # Bekleyen müşteri sayısını güncelle
    root.after(UPDATE_INTERVAL, update_gui)


def draw_masa(masa_numarasi, renk):
    x = 50 + (masa_numarasi - 1) * 150
    y = 70
    masa_durumu[masa_numarasi] = canvas.create_rectangle(x, y, x + 100, y + 100, fill=renk)
    canvas.create_text(x + 50, y + 50, text=str(masa_numarasi))


def draw_bekleyen_musteri():
    global bekleyen_musteri_text
    text = f"Bekleyen Müşteriler: {len(bekleyen_musteriler)}"
    if bekleyen_musteri_text:
        canvas.itemconfig(bekleyen_musteri_text, text=text)
    else:
        bekleyen_musteri_text = canvas.create_text(bekleyen_musteri_pos[0], bekleyen_musteri_pos[1], text=text,
                                                   anchor=tk.W)


def draw_person(renk, is_active, position):
    if is_active:
        # print("renk, is_active, position", renk, is_active, position)
        x, y = position
        obj = canvas.create_oval(x, y, x + 50, y + 50, fill=renk)
        return obj
    else:
        return None  # Eğer kişi aktif değilse None döndür


def update_person(obj, is_active, new_pos=None):
    if obj is not None:  # Eğer obje varsa devam et
        if not is_active:
            canvas.delete(obj)
            return None
        if new_pos:
            canvas.coords(obj, new_pos[0], new_pos[1], new_pos[0] + 50, new_pos[1] + 50)
        return obj
    else:
        if is_active:  # Eğer obje None ve kişi aktifse yeni bir obje oluştur
            x, y = new_pos
            return canvas.create_oval(x, y, x + 50, y + 50, fill=renk)
        else:
            return None  # Eğer obje None ise None döndür


def gecen_zaman_takip():
    while running:
        global gecen_zaman, gec
        gec = time.time()
        gecen_zaman = gec - start
        gecen_zaman_label.config(text=f"Geçen Zaman: {gecen_zaman:.1f} saniye")
        # print(f"Gecen zaman {gecen_zaman}")
        time.sleep(1)


def garson_thread(garson):
    while running:
        with garson_sem:
            if siparis_bekleyen_musteriler_onay:
                musteri, masa_numarasi = siparis_bekleyen_musteriler_onay.pop(0)
                if musteri not in yemek_bekleyen_musteriler:
                    print(f"Masa {masa_numarasi}'deki Müşteri {musteri}'nin siparişini {garson['isim']} alınıyor.")
                    dosyaya_yaz(
                        f"Masa {masa_numarasi}'deki Müşteri {musteri}'nin siparişini {garson['isim']} alınıyor.")
                    garson_obje = draw_person("red", True, garson["pozisyon"])
                    garson["obje"] = garson_obje
                    update_queue.append((update_person, (garson_obje, True)))
                    time.sleep(2)
                    print(f"Masa {masa_numarasi}'deki Müşteri {musteri}'nin siparişini {garson['isim']} aldı.")
                    dosyaya_yaz(f"Masa {masa_numarasi}'deki Müşteri {musteri}'nin siparişini {garson['isim']} aldı.")
                    update_queue.append((update_person, (garson_obje, False)))
                    yemek_bekleyen_musteriler.append((musteri, masa_numarasi))
                else:
                    print("Garson çakışma problemi")


def asci_thread(asci):
    while running:
        with asci_sem:
            if yemek_bekleyen_musteriler_onay:
                musteri, masa_numarasi = yemek_bekleyen_musteriler_onay.pop(0)
                if musteri not in kasa_bekleyen_musteriler:
                    print(f"Masa {masa_numarasi}'deki Müşteri {musteri}'nin yemeğini {asci['isim']} hazırlanıyor.")
                    dosyaya_yaz(
                        f"Masa {masa_numarasi}'deki Müşteri {musteri}'nin yemeğini {asci['isim']} hazırlanıyor.")
                    asci_obje = draw_person("blue", True, asci["pozisyon"])
                    asci["obje"] = asci_obje
                    update_queue.append((update_person, (asci_obje, True)))
                    time.sleep(3)
                    print(f"Masa {masa_numarasi}'deki Müşteri {musteri}'nin yemeği hazır.")
                    dosyaya_yaz(f"Masa {masa_numarasi}'deki Müşteri {musteri}'nin yemeği hazır.")
                    update_queue.append((update_person, (asci_obje, False)))
                    yemek_yiyen_musteriler.append((musteri, masa_numarasi))
                else:
                    print("Aşçı çakışma problemi")


def kasa_thread(kasa):
    while running:
        if kasa_bekleyen_musteriler_onay:
            musteri, masa_numarasi = kasa_bekleyen_musteriler_onay.pop(0)
            print(f"Masa {masa_numarasi}'deki Müşteri {musteri} {kasa['isim']}'de")
            dosyaya_yaz(f"Masa {masa_numarasi}'deki Müşteri {musteri} {kasa['isim']}'de")
            kasa["aktif"] = True
            kasa["obje"] = draw_person("black", True, kasa["pozisyon"])  # Siyah renk ve aktif
            update_queue.append((update_person, (kasa["obje"], True)))
            time.sleep(1)
            update_queue.append((update_person, (kasa["obje"], False)))
            masa_bosalt(masa_numarasi)
            kalan_musteriler.append(musteri)
            print(f"Masa {masa_numarasi}'deki Müşteri {musteri} {kasa['isim']}'de ödemesini yaptı")
            dosyaya_yaz(f"Masa {masa_numarasi}'deki Müşteri {musteri} {kasa['isim']}'de ödemesini yaptı")


def yemek_yeme_thread(musteri, masa_numarasi):
    print(f"Masa {masa_numarasi}'deki Müşteri {musteri} yemek yiyor.")
    dosyaya_yaz(f"Masa {masa_numarasi}'deki Müşteri {musteri} yemek yiyor.")
    time.sleep(3)
    kasa_bekleyen_musteriler.append((musteri, masa_numarasi))
    print(f"Masa {masa_numarasi}'deki Müşteri {musteri} yemek yedi.")
    dosyaya_yaz(f"Masa {masa_numarasi}'deki Müşteri {musteri} yemek yedi.")


def yemek_yeme():
    while running:
        if yemek_yiyen_musteriler:
            musteri, masa_numarasi = yemek_yiyen_musteriler.pop(0)
            threading.Thread(target=yemek_yeme_thread, args=(musteri, masa_numarasi,)).start()


def masa_bosalt(masa_numarasi):
    print(f"Masa {masa_numarasi} boşaldı.")
    dosyaya_yaz(f"Masa {masa_numarasi} boşaldı.")
    bos_masalar.add(masa_numarasi)
    update_queue.append((draw_masa, (masa_numarasi, "white")))  # Masa çizimi güncelle


def masa_ata():
    global bekleyen_musteriler, bos_masalar, siparis_bekleyen_musteriler, update_queue
    while running:
        with bekleyen_sem:
            if bekleyen_musteriler:
                # musteri, baslangic_zamani = bekleyen_musteriler[0]  # İlk müşteriyi kontrol et
                if bos_masalar:
                    musteri, baslangic_zamani = bekleyen_musteriler.pop(0)  # Boş masa varsa pop işlemi yap
                    masa_numarasi = bos_masalar.pop()
                    print(f"Müşteri {musteri} masaya oturdu: {masa_numarasi}")
                    dosyaya_yaz(f"Müşteri {musteri} masaya oturdu: {masa_numarasi}")
                    siparis_bekleyen_musteriler.append((musteri, masa_numarasi))
                    update_queue.append((draw_masa, (masa_numarasi, "green")))
                else:
                    pass
                    # print(f"Bos masa yok Bekleyenler: {[musteri for musteri, _ in bekleyen_musteriler]}")


def kontrol_et_ve_guncelle():
    global giden_musteriler
    while running:
        current_time = time.time()
        with bekleyen_sem:
            for musteri, baslangic_zamani in bekleyen_musteriler:
                gecen_sure = current_time - baslangic_zamani
                # print("gecen_sure ", gecen_sure)
                if gecen_sure >= 20 and musteri not in giden_musteriler:
                    print(f"Müşteri {musteri} beklerken ayrıldı. Geçen Süre: {gecen_sure:.2f} saniye")
                    dosyaya_yaz(f"Müşteri {musteri} beklerken ayrıldı. Geçen Süre: {gecen_sure:.2f} saniye")
                    giden_musteriler.append(musteri)
                    bekleyen_musteriler.remove((musteri, baslangic_zamani))
                    print(f"Giden Müşteriler: {giden_musteriler}")
            # time.sleep(1)  # Belirli aralıklarla kontrol etmek için bekleyin

def siparis_onayla():
    if siparis_bekleyen_musteriler:
        musteri, masa_numarasi = siparis_bekleyen_musteriler.pop(0)
        siparis_bekleyen_musteriler_onay.append((musteri, masa_numarasi))
        print(f"Sipariş Onaylandı: Müşteri {musteri}, Masa {masa_numarasi}")
    else:
        print("Sipariş bekleyen müşteri yok")
def yemek_onayla():
    if yemek_bekleyen_musteriler:
        musteri, masa_numarasi = yemek_bekleyen_musteriler.pop(0)
        yemek_bekleyen_musteriler_onay.append((musteri, masa_numarasi))
        print(f"Yemek Onaylandı: Müşteri {musteri}, Masa {masa_numarasi}")
    else:
        print("Yemek bekleyen müşteri yok")
def kasa_onayla():
    if kasa_bekleyen_musteriler:
        musteri, masa_numarasi = kasa_bekleyen_musteriler.pop(0)
        kasa_bekleyen_musteriler_onay.append((musteri, masa_numarasi))
        print(f"Kasa Onaylandı: Müşteri {musteri}, Masa {masa_numarasi}")
    else:
        print("Kasa bekleyen müşteri yok")

def musteri_ekle():
    global musteri_sayaci, bekleyen_musteriler, ara
    max_musteri_sayisi = 100
    gelen_musteri = 5
    toplam_zaman = 0

    while musteri_sayaci < max_musteri_sayisi and running:
        baslangic_zamani = time.time()

        for i in range(gelen_musteri):
            musteri = musteri_sayaci
            musteriler.append(musteri)
            with bekleyen_sem:
                bekleyen_musteriler.append((musteri, baslangic_zamani))
            musteri_sayaci += 1

        gecen_sure = time.time() - baslangic_zamani
        toplam_zaman += gecen_sure
        bekleme_suresi = max(20 - gecen_sure, 0)  # En az 0 saniye bekle
        time.sleep(bekleme_suresi)
    ara = time.time()
    print("Toplam Zaman:", ara - start)  # Kontrol için eklendi
    print("Toplam Müşteri Sayısı:", musteri_sayaci)
    durdur()


# Masaları bir kere çizelim
for masa_numarasi, renk in masa_renkleri.items():
    draw_masa(masa_numarasi, renk)


def baslat():
    global running, start
    start = time.time()
    running = True
    baslat_button.config(state=tk.DISABLED)  # Başlat butonunu devre dışı bırak
    durdur_button.config(state=tk.NORMAL)  # Durdur butonunu etkinleştir
    threadler_basla()


def durdur():
    global running, start, end
    print("DURDU")
    while running:
        if bekleyen_musteriler or siparis_bekleyen_musteriler or kasa_bekleyen_musteriler or yemek_bekleyen_musteriler or yemek_yiyen_musteriler or len(
                bos_masalar) != 6:
            pass
            # print("DEVAM")
        else:
            end = time.time()
            print("Toplam müşteri ", len(musteriler), musteriler)
            print("Giden müşteriler ", len(giden_musteriler), giden_musteriler)
            print("Kalan müşteriler ", len(kalan_musteriler), kalan_musteriler)
            print("BİTTİ ", gecen_zaman, end - start)
            running = False
            baslat_button.config(state=tk.NORMAL)  # Başlat butonunu etkinleştir
            durdur_button.config(state=tk.DISABLED)  # Durdur butonunu devre dışı bırak


def threadler_basla():
    threading.Thread(target=gecen_zaman_takip).start()
    threading.Thread(target=musteri_ekle).start()
    threading.Thread(target=kontrol_et_ve_guncelle).start()
    threading.Thread(target=masa_ata).start()
    # Garson thread'lerini başlat
    for garson in garsonlar:
        threading.Thread(target=garson_thread, args=(garson,)).start()

    # Aşçı thread'lerini başlat
    for asci in ascilar:
        threading.Thread(target=asci_thread, args=(asci,)).start()

    # Kasa thread'ini başlat
    threading.Thread(target=kasa_thread, args=(kasa,)).start()

    # Yemek yeme thread'ini başlat
    threading.Thread(target=yemek_yeme).start()


# Başlat ve Durdur butonları
baslat_button = tk.Button(root, text="Başlat", command=baslat)
baslat_button.pack()

durdur_button = tk.Button(root, text="Durdur", command=durdur, state=tk.DISABLED)
durdur_button.pack()

# Sipariş Onay Butonu
siparis_onay_button = tk.Button(root, text="Siparişi Onayla", command=siparis_onayla)
siparis_onay_button.pack()
# Yemek Onay Butonu
yemek_onay_button = tk.Button(root, text="Yemek Onayla", command=yemek_onayla)
yemek_onay_button.pack()
# Kasa Onay Butonu
kasa_onay_button = tk.Button(root, text="Kasa Onayla", command=kasa_onayla)
kasa_onay_button.pack()

# Tkinter penceresini çalıştırın
root.after(UPDATE_INTERVAL, update_gui)

root.mainloop()


