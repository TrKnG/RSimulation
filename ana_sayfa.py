import tkinter as tk
from subprocess import Popen

garson1_pos = (1150, 50)
asci1_pos = (50, 600)
kasa_pos = (1150, 600)

masa_durumu = {}


def draw_masa(masa_numarasi, renk):
    x = 50 + (masa_numarasi - 1) * 150
    y = 100
    masa_durumu[masa_numarasi] = canvas.create_rectangle(x, y, x + 100, y + 100, fill=renk)

    if masa_numarasi % 2 == 0:
        masa_dolu = "DOLU"
    else:
        masa_dolu = "BOŞ"

    canvas.create_text(x + 50, y + 50, text=str(masa_dolu))
    # canvas.create_text(x + 50, y + 120, text=f"Garson {masa_numarasi}", fill="red")


def draw_person(renk, is_active, position, person_text):
    if is_active:
        x, y = position
        obj = canvas.create_oval(x, y, x + 50, y + 50, fill=renk)
        canvas.create_text(x + 25, y + 70, text=person_text, fill=renk)
        return obj
    else:
        return None  # Eğer kişi aktif değilse None döndür


def create_ana_sayfa():
    ana_sayfa = tk.Tk()
    ana_sayfa.title("Restoran Simulasyonu")
    ana_sayfa.geometry("1280x720")

    global canvas
    canvas = tk.Canvas(ana_sayfa, bg="white", width=1280, height=720)
    canvas.pack()

    # Masa çizimleri
    draw_masa(1, "white")
    draw_masa(2, "green")
    draw_masa(3, "white")
    draw_masa(4, "green")
    draw_masa(5, "white")
    draw_masa(6, "green")

    # Personel çizimleri
    draw_person("red", True, garson1_pos, "Garson")
    draw_person("blue", True, asci1_pos, "Aşçı")
    draw_person("black", True, kasa_pos, "Kasa")

    # RESTORANTE SIMULATE yazısı
    simulate_dikdortgen = canvas.create_rectangle(50, 10, 1050, 70, fill="white")
    canvas.create_text(550, 40, text="RESTORANTE SIMULATE", fill="black", font=("Arial", 12))

    # Simulasyonu başlatan buton
    start_button = tk.Button(ana_sayfa, text="Simulasyonu Başlat", command=otomatik)
    start_button.pack(pady=50)

    # Otomatik ve Manuel butonlar
    oto_button = tk.Button(ana_sayfa, text="Otomatik Simülasyon", command=otomatik, bg="green", fg="white")
    oto_button.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

    man_button = tk.Button(ana_sayfa, text="Manuel Simülasyon", command=manuel, bg="red", fg="white")
    man_button.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

    return ana_sayfa


def otomatik():
    Popen(["python", "otomatik.py"])


def manuel():
    Popen(["python", "manuel.py"])


if __name__ == "__main__":
    ana_sayfa = create_ana_sayfa()
    ana_sayfa.mainloop()
