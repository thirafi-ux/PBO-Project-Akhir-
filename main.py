# ==========================================================
# SISTEM RENTAL MOBIL - contoh lengkap konsep OOP (13 class)
# Konsep: Abstraksi, Inheritance, Polymorphism, Encapsulation,
#         Composition, Aggregation, Association, Access Modifier
# ==========================================================

# 1. ABSTRAKSI + PARENT
# Kendaraan = cetak biru semua kendaraan. Method bahan_bakar() & biaya_sewa()
# sengaja dikosongkan: anak WAJIB mengisi sendiri (inilah ABSTRAKSI).
class Kendaraan:
    def __init__(self, nama, plat, harga, jenis_mesin):
        self.nama = nama                      # ACCESS MODIFIER public: bebas dibaca
        self.plat = plat                      # public
        self._kondisi = 100                   # ACCESS MODIFIER protected: milik dalam sistem rental saja
        self.__harga = harga                  # ACCESS MODIFIER private: disembunyikan (name mangling)
        self.tersedia = True                  # public: status bisa disewa atau tidak
        self.mesin = Mesin(jenis_mesin)       # COMPOSITION: Mesin dibuat DI DALAM Kendaraan,
                                              # mesin tidak ada tanpa kendaraannya
    def bahan_bakar(self):
        pass  # kosong (abstrak), anak wajib isi sendiri
    def biaya_sewa(self, hari):
        pass  # kosong (abstrak), anak wajib isi sendiri
    # ENCAPSULATION: data private diakses lewat getter & setter
    def get_harga(self):                      # getter
        return self.__harga
    def set_harga(self, h):                   # setter + validasi
        if h > 0: self.__harga = h
    def info(self):
        return f"{self.nama} [{self.plat}] | {self.bahan_bakar()} | Rp{self.__harga}/hari | {self.mesin.info()}"


# 2-3. INHERITANCE level 1: keluarga perantara
class MobilBensin(Kendaraan):
    def bahan_bakar(self):
        return "Bensin"                       # sifat umum mobil bensin
    def biaya_sewa(self, hari):
        # self.__harga TIDAK bisa dipakai di anak (private), jadi pakai getter
        return self.get_harga() * hari

class MobilListrik(Kendaraan):
    def bahan_bakar(self):
        return "Listrik"                      # sifat umum mobil listrik
    def biaya_sewa(self, hari):               # POLYMORPHISM (override): rumus beda dari MobilBensin
        return self.get_harga() * hari + 50000   # + biaya charging
    def isi_baterai(self):
        return f"{self.nama} sedang di-charge"


# 4-7. INHERITANCE level 2: kendaraan nyata (perilaku beda-beda)
class Avanza(MobilBensin):
    def __init__(self, plat, harga=350000):   # konstruktor + super()
        super().__init__("Avanza", plat, harga, "1.3L")
        self.kursi = 7

class Brio(MobilBensin):
    def __init__(self, plat, harga=300000):
        super().__init__("Brio", plat, harga, "1.2L")
    def biaya_sewa(self, hari):               # POLYMORPHISM: diskon 10% jika sewa >= 7 hari
        total = self.get_harga() * hari
        return total * 0.9 if hari >= 7 else total

class Tesla(MobilListrik):
    def __init__(self, plat, harga=1200000):
        super().__init__("Tesla Model 3", plat, harga, "Dual Motor")
        self.autopilot = True

class Minibus(Kendaraan):                     # langsung dari Kendaraan, tanpa perantara
    def bahan_bakar(self):
        return "Solar"
    def biaya_sewa(self, hari):               # POLYMORPHISM: sudah termasuk sopir Rp200.000/hari
        return (self.get_harga() + 200000) * hari


# 8. COMPOSITION: bagian yang hidup-matinya bergantung pada Kendaraan
class Mesin:
    def __init__(self, jenis):
        self.jenis = jenis
    def info(self):
        return f"Mesin {self.jenis}"


# 9. AGGREGATION: Garasi MEMILIKI kendaraan, tapi kendaraan dibuat di luar
# dan tetap ada walau garasinya dibubarkan (hubungan longgar)
class Garasi:
    def __init__(self, nama):
        self.nama = nama
        self.isi = []
    def tambah(self, k):
        self.isi.append(k)                    # objek dari luar, hanya "dititipkan"


# 10. Pelanggan (dipakai untuk ASSOCIATION di Transaksi)
class Pelanggan:
    def __init__(self, nama, no_ktp):
        self.nama = nama
        self.no_ktp = no_ktp


# 11. ASSOCIATION: Transaksi menghubungkan Pelanggan dan Kendaraan.
# Keduanya berdiri sendiri, hanya "berelasi" saat transaksi terjadi
class Transaksi:
    def __init__(self, pelanggan, kendaraan, hari):
        self.pelanggan = pelanggan
        self.kendaraan = kendaraan
        self.hari = hari
        kendaraan.tersedia = False
    def total(self):
        return self.kendaraan.biaya_sewa(self.hari)   # POLYMORPHISM: rumus ikut tipe kendaraan
    def struk(self):
        return f"{self.pelanggan.nama} menyewa {self.kendaraan.nama} {self.hari} hari = Rp{self.total():,.0f}"


# 12. Teman kendaraan
class Montir:
    def __init__(self, nama):
        self.nama = nama
    def servis(self, k):
        k._kondisi = 100   # boleh sentuh yang protected karena masih "keluarga" rental
        return f"{self.nama} mengservis {k.nama}: kondisi prima!"


# 13. Pengelola semua
class RentalMobil:
    def __init__(self, nama):
        self.nama = nama
        self.garasi = []                      # AGGREGATION: menampung garasi
        self.transaksi = []
    def tambah_garasi(self, g):
        self.garasi.append(g)
    def sewa(self, pelanggan, kendaraan, hari):   # ASSOCIATION dibuat di sini
        t = Transaksi(pelanggan, kendaraan, hari)
        self.transaksi.append(t)
        return t
    def daftar_armada(self):  # POLYMORPHISM: satu perintah, banyak gaya
        for g in self.garasi:
            for k in g.isi: print(f"{k.nama}: {k.bahan_bakar()} | 3 hari = Rp{k.biaya_sewa(3):,.0f}")


if __name__ == "__main__":
    # INSTANCE: mencetak objek nyata dari cetakan class (lewat konstruktor)
    avanza = Avanza("L 1234 AB")
    brio = Brio("L 5678 CD")
    tesla = Tesla("L 9999 EV")
    bus = Minibus("Hiace", "L 7777 XY", 800000, "2.8L Diesel")

    g1 = Garasi("Garasi Pusat"); g1.tambah(avanza); g1.tambah(brio)
    g2 = Garasi("Garasi Premium"); g2.tambah(tesla); g2.tambah(bus)

    rental = RentalMobil("Maju Jaya")
    rental.tambah_garasi(g1); rental.tambah_garasi(g2)
    budi = Pelanggan("Budi", "3501xxxx")
    montir = Montir("Pak Joko")

    print(avanza.info())
    print(montir.servis(avanza))
    print(tesla.isi_baterai())
    print("Harga Brio:", brio.get_harga()); brio.set_harga(320000)
    print("Harga baru:", brio.get_harga())
    print(rental.sewa(budi, brio, 7).struk())
    print(rental.sewa(budi, tesla, 2).struk())
    print("--- Daftar Armada ---"); rental.daftar_armada()