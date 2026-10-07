# ==========================================================
# SISTEM RENTAL MOBIL
#
#   PUBLIC     -> ditulis biasa:  self.nama
#                 siapa pun boleh baca dan ubah. Ibarat papan nama di depan toko.
#   PROTECTED  -> diawali satu garis bawah:  self._kondisi
#                 artinya "ini urusan dalam, jangan dipegang orang luar".
#                 Hanya class itu sendiri, anak-anaknya, dan "keluarga" sistem
#                 yang boleh sentuh. Ibarat ruang staf: tidak dikunci, tapi ada
#                 tulisan "khusus karyawan".
#   PRIVATE    -> diawali dua garis bawah:  self.__harga
#                 benar-benar disembunyikan. Bahkan anak class pun tidak bisa
#                 memanggilnya langsung. Ibarat brankas: mau lihat isinya harus
#                 lewat petugas (getter), mau ubah juga lewat petugas (setter).
#
#   ENCAPSULATION (enkapsulasi) = membungkus data penting (private) lalu
#                 membuka "pintu resmi" untuk mengaksesnya (getter & setter),
#                 supaya data tidak bisa diisi sembarangan.
#   ABSTRAKSI   = membuat cetak biru yang isinya baru "janji", belum "cara".
#                 Contoh: semua kendaraan PASTI punya biaya sewa, tapi cara
#                 menghitungnya diserahkan ke masing-masing jenis kendaraan.
#
# ==========================================================
import json
import os

FILE_JSON = "data_rental.json"


# ----------------------------------------------------------
# 1. KENDARAAN  (ini si "bos besar" untuk semua jenis kendaraan)
#
# Class ini ibarat formulir kosong yang berisi hal-hal yang dimiliki SEMUA
# kendaraan: nama, plat, harga, mesin, dll. Kita nggak pernah menyewakan
# "kendaraan" secara umum, yang disewakan itu Avanza, Brio, Tesla, dst.
# Makanya class ini disebu  t induk (parent): jadi dasar buat class lain.
# ----------------------------------------------------------
class Kendaraan:
    def __init__(self, nama, plat, harga, jenis_mesin):
        # __init__ itu "konstruktor": jalan otomatis saat objek baru dibuat,
        # tugasnya mengisi data awal.
        self.nama = nama                      # PUBLIC: nama mobil, siapa pun boleh baca, memang tidak rahasia
        self.plat = plat                      # PUBLIC: plat juga terlihat di jalan, jadi aman dibuka
        self._kondisi = 100                   # PROTECTED (satu garis bawah): persentase kondisi mobil, idealnya hanya
                                              #   diubah orang dalam sistem, contohnya montir saat servis
        self.__harga = harga                  # PRIVATE (dua garis bawah): harga sewa dikunci. Kalau ini PUBLIC,
                                              #   siapa pun bisa tulis harga = -500 dan sistem kacau
        self.tersedia = True                  # PUBLIC: status bisa disewa atau tidak, perlu dibaca banyak bagian program
        self.mesin = Mesin(jenis_mesin)       # COMPOSITION: Mesin dibuat DI DALAM kendaraan. Mesin tidak punya
                                              #   hidup sendiri; kendaraan hilang, mesinnya ikut hilang

    # --- ABSTRAKSI ---------------------------------------------------
    # Dua method di bawah sengaja KOSONG (pass). Maksudnya: "semua kendaraan
    # wajib punya cara menyebut bahan bakar dan menghitung biaya sewa, tapi
    # aku (Kendaraan) nggak tahu caranya, tanyakan ke anak-anakku."
    # Setiap anak (MobilBensin, Tesla, dll) wajib menulis isinya sendiri.
    # (Di Python ini abstraksi "secara konsep". Kalau mau dipaksa ketat
    #  ada fitur khusus bernama ABC, tapi untuk tugas ini konsepnya sudah cukup.)
    def bahan_bakar(self):
        pass  # kosong, diisi anak
    def biaya_sewa(self, hari):
        pass  # kosong, diisi anak

    # --- ENCAPSULATION -----------------------------------------------
    # Karena __harga itu private, orang luar tidak bisa pakai kendaraan.__harga.
    # Jadi kita sediakan dua "pintu resmi":
    def get_harga(self):                      # GETTER: pintu untuk MELIHAT harga
        return self.__harga
    def set_harga(self, h):                   # SETTER: pintu untuk MENGUBAH harga
        if h > 0: self.__harga = h            #   ada satpamnya: harga hanya diterima kalau lebih dari 0.
                                              #   Inilah gunanya enkapsulasi: data terlindungi dan selalu valid

    def info(self):
        # f"..." itu cara menyisipkan nilai variabel ke dalam teks.
        # Di sini self.mesin.info() memanggil method milik objek Mesin.
        return f"{self.nama} [{self.plat}] | {self.bahan_bakar()} | Rp{self.__harga:,.0f}/hari | {self.mesin.info()}"

    def to_dict(self):
        return {"tipe": type(self).__name__, "nama": self.nama, "plat": self.plat,
                "harga": self.__harga, "kondisi": self._kondisi,
                "tersedia": self.tersedia, "mesin": self.mesin.jenis}


# ----------------------------------------------------------
# 2-3. INHERITANCE (pewarisan) level 1: keluarga perantara
# ----------------------------------------------------------
class MobilBensin(Kendaraan):
    def bahan_bakar(self):                    # mengisi method abstrak dari induk
        return "Bensin"
    def biaya_sewa(self, hari):
        # Perhatikan: di sini kita TIDAK bisa tulis self.__harga karena harga itu
        # private (anak pun dilarang). Makanya harus lewat pintu resmi get_harga().
        # Ini contoh nyata kenapa enkapsulasi itu "memaksa" kita pakai jalur resmi.
        return self.get_harga() * hari

class MobilListrik(Kendaraan):
    def bahan_bakar(self):
        return "Listrik"
    def biaya_sewa(self, hari):               # POLYMORPHISM (override): nama method sama dengan MobilBensin,
        return self.get_harga() * hari + 50000   #   tapi rumusnya beda: ada tambahan biaya charging Rp50.000
    def isi_baterai(self):                    # method khusus mobil listrik, mobil bensin tidak punya ini
        return f"{self.nama} sedang di-charge"


# ----------------------------------------------------------
# 4-7. INHERITANCE level 2: kendaraan nyata yang benar-benar disewakan
#
# Ini cucu dari Kendaraan. super().__init__(...) artinya "panggil dulu
# konstruktor orang tuaku untuk mengisi data dasar", lalu kita tambah
# data khusus milik class ini.
# ----------------------------------------------------------
class Avanza(MobilBensin):
    def __init__(self, plat, harga=350000):   # harga=350000 artinya kalau tidak diisi, otomatis 350 ribu
        super().__init__("Avanza", plat, harga, "1.3L")
        self.kursi = 7                        # PUBLIC: atribut khusus Avanza, jumlah kursi

class Brio(MobilBensin):
    def __init__(self, plat, harga=300000):
        super().__init__("Brio", plat, harga, "1.2L")
    def biaya_sewa(self, hari):               # POLYMORPHISM: Brio punya aturan sendiri, sewa 7 hari ke atas diskon 10%
        total = self.get_harga() * hari
        return total * 0.9 if hari >= 7 else total

class Tesla(MobilListrik):
    def __init__(self, plat, harga=1200000):
        super().__init__("Tesla Model 3", plat, harga, "Dual Motor")
        self.autopilot = True                 # PUBLIC: fitur khusus Tesla

class Minibus(Kendaraan):                     # langsung anak Kendaraan, tanpa perantara bensin/listrik
    def bahan_bakar(self):
        return "Solar"
    def biaya_sewa(self, hari):               # POLYMORPHISM: tarif minibus sudah termasuk sopir Rp200.000 per hari
        return (self.get_harga() + 200000) * hari


# ----------------------------------------------------------
# 8. MESIN  (bagian dari kendaraan -> hubungan COMPOSITION)
#
# Composition itu hubungan "punya, dan tidak bisa hidup sendiri". Mesin selalu
# dibuat di dalam Kendaraan (lihat baris self.mesin = Mesin(...) di atas).
# Tidak ada cerita "mesin dibuat dulu, baru dicari mobilnya".
# ----------------------------------------------------------
class Mesin:
    def __init__(self, jenis):
        self.jenis = jenis                    # PUBLIC: jenis mesin, misalnya "1.3L"
    def info(self):
        return f"Mesin {self.jenis}"


# ----------------------------------------------------------
# 9. GARASI  (hubungan AGGREGATION)
#
# Aggregation itu "punya, tapi masih bisa hidup sendiri". Garasi menyimpan
# kendaraan, tapi kendaraannya dibuat di LUAR garasi. Kalau garasi ditutup,
# mobilnya tetap ada. Bedanya dengan Mesin tadi: mesin ikut hilang bersama
# mobil, mobil tidak ikut hilang bersama garasi.
# ----------------------------------------------------------
class Garasi:
    def __init__(self, nama):
        self.nama = nama                      # PUBLIC
        self.isi = []                         # PUBLIC: list kosong, nanti diisi kendaraan
    def tambah(self, k):
        self.isi.append(k)                    # mobil cuma "dititipkan", bukan dibuat di sini
    def to_dict(self):
        return {"nama": self.nama, "isi": [k.to_dict() for k in self.isi]}


# ----------------------------------------------------------
# 10. PELANGGAN  (data orang yang menyewa)
# ----------------------------------------------------------
class Pelanggan:
    def __init__(self, nama, no_ktp):
        self.nama = nama                      # PUBLIC
        self.no_ktp = no_ktp                  # PUBLIC di kode ini. Di dunia nyata no KTP itu data sensitif,
                                              #   idealnya dibuat private. Dibiarkan public supaya kode tetap sederhana
    def to_dict(self):
        return {"nama": self.nama, "no_ktp": self.no_ktp}


# ----------------------------------------------------------
# 11. TRANSAKSI  (hubungan ASSOCIATION)
#
# Association itu hubungan "saling kenal". Pelanggan dan Kendaraan sama-sama
# berdiri sendiri, mereka baru terhubung ketika ada transaksi. Class Transaksi
# inilah "jembatan" yang mencatat: siapa menyewa apa, berapa hari.
# ----------------------------------------------------------
class Transaksi:
    def __init__(self, pelanggan, kendaraan, hari):
        self.pelanggan = pelanggan            # PUBLIC: menunjuk ke objek Pelanggan
        self.kendaraan = kendaraan            # PUBLIC: menunjuk ke objek Kendaraan (bisa Avanza, Tesla, apa pun)
        self.hari = hari                      # PUBLIC: lama sewa
        self.aktif = True                     # PUBLIC: True = masih disewa, False = sudah dikembalikan
        kendaraan.tersedia = False            # begitu disewa, kendaraan otomatis berstatus tidak tersedia
    def total(self):
        # POLYMORPHISM yang paling keren ada di sini. Kita cuma menulis satu baris
        # biaya_sewa(), tapi hasilnya menyesuaikan jenis kendaraannya: kalau Brio,
        # kena diskon; kalau Tesla, kena biaya charging; kalau Minibus, termasuk sopir.
        # Transaksi tidak perlu tahu mobilnya jenis apa. Kendaraannya yang tahu.
        return self.kendaraan.biaya_sewa(self.hari)
    def struk(self):
        return f"{self.pelanggan.nama} menyewa {self.kendaraan.nama} {self.hari} hari = Rp{self.total():,.0f}"
    def selesai(self):                        #dipanggil saat mobil dikembalikan
        self.aktif = False
        self.kendaraan.tersedia = True        # mobil bisa disewa lagi
    def to_dict(self):                        # yang disimpan cukup no KTP dan plat sebagai "penunjuk"
        return {"no_ktp": self.pelanggan.no_ktp, "plat": self.kendaraan.plat,
                "hari": self.hari, "aktif": self.aktif}


# ----------------------------------------------------------
# 12. MONTIR
# ----------------------------------------------------------
class Montir:
    def __init__(self, nama):
        self.nama = nama                      # PUBLIC
    def servis(self, k):
        # Montir mengubah k._kondisi yang PROTECTED. Secara aturan Python ini
        # diperbolehkan (cuma peringatan, bukan gembok), dan alasannya masuk akal:
        # montir memang "orang dalam" sistem rental, yang berhak memperbaiki kondisi.
        k._kondisi = 100
        return f"{self.nama} mengservis {k.nama}: kondisi prima!"
    def to_dict(self):
        return {"nama": self.nama}


# ----------------------------------------------------------
# 13. RENTALMOBIL  (pengelola semua, "kepala kantornya")
# ----------------------------------------------------------
class RentalMobil:
    def __init__(self, nama):
        self.nama = nama                      # PUBLIC
        self.garasi = []                      # AGGREGATION: menampung garasi-garasi yang dibuat di luar
        self.transaksi = []                   # menampung catatan transaksi
        self.pelanggan = []                   # daftar pelanggan yang terdaftar
        self.montir = []                      # daftar montir
    def tambah_garasi(self, g):
        self.garasi.append(g)
    def sewa(self, pelanggan, kendaraan, hari):
        t = Transaksi(pelanggan, kendaraan, hari)   # di sinilah ASSOCIATION tercipta: pelanggan dan kendaraan dipertemukan
        self.transaksi.append(t)
        return t
    def daftar_armada(self):                  # POLYMORPHISM: satu perintah (k.biaya_sewa(3)) dipakai ke semua jenis
        for g in self.garasi:                 #   kendaraan, tiap kendaraan menjawab dengan caranya sendiri
            for k in g.isi: print(f"{k.nama}: {k.bahan_bakar()} | 3 hari = Rp{k.biaya_sewa(3):,.0f}")

    # ----- TAMBAHAN: bantuan untuk menu -----
    def semua_kendaraan(self):
        # Mengumpulkan semua kendaraan dari semua garasi jadi satu daftar.
        # Hasilnya pasangan (garasi, kendaraan) supaya kita tahu mobil ada di garasi mana.
        return [(g, k) for g in self.garasi for k in g.isi]

    # ----- TAMBAHAN: simpan dan muat JSON -----
    def simpan(self, path=FILE_JSON):
        # JSON itu format teks untuk menyimpan data (mirip daftar berlabel).
        # Tiap class punya to_dict() yang tugasnya "menerjemahkan" objeknya jadi
        # data sederhana, lalu semuanya dikumpulkan di sini dan ditulis ke file.
        data = {"nama": self.nama,
                "garasi": [g.to_dict() for g in self.garasi],
                "pelanggan": [p.to_dict() for p in self.pelanggan],
                "montir": [m.to_dict() for m in self.montir],
                "transaksi": [t.to_dict() for t in self.transaksi]}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def muat(path=FILE_JSON):
        # Kebalikan dari simpan(): baca file JSON, lalu BUAT ULANG semua objeknya.
        # Urutannya penting: kendaraan dan pelanggan dibuat dulu, baru transaksi
        # (karena transaksi butuh menunjuk ke pelanggan dan kendaraan yang sudah ada).
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        r = RentalMobil(d["nama"])
        peta, status = {}, {}                 # peta: plat -> objek kendaraan (buat mencari lagi nanti)
        for gd in d["garasi"]:
            g = Garasi(gd["nama"])
            for kd in gd["isi"]:
                k = buat_kendaraan(kd["tipe"], kd["plat"], kd["harga"], kd["nama"], kd["mesin"])
                k._kondisi = kd["kondisi"]    # memulihkan kondisi tersimpan (ini "orang dalam" sistem, jadi wajar menyentuh protected)
                peta[k.plat], status[k.plat] = k, kd["tersedia"]
                g.tambah(k)
            r.tambah_garasi(g)
        r.pelanggan = [Pelanggan(p["nama"], p["no_ktp"]) for p in d["pelanggan"]]
        r.montir = [Montir(m["nama"]) for m in d["montir"]]
        kamus = {p.no_ktp: p for p in r.pelanggan}
        for td in d["transaksi"]:
            t = r.sewa(kamus[td["no_ktp"]], peta[td["plat"]], td["hari"])
            t.aktif = td["aktif"]
        for plat, k in peta.items():          # sewa() tadi membuat semua mobil jadi "tidak tersedia",
            k.tersedia = status[plat]         #   jadi di sini status aslinya dikembalikan sesuai isi file
        return r


# ==========================================================
# fungsi bantu, data awal, dan menu input
# (semuanya fungsi biasa, BUKAN class baru)
# ==========================================================
TIPE = {"Avanza": Avanza, "Brio": Brio, "Tesla": Tesla}
HARGA_STANDAR = {"Avanza": 350000, "Brio": 300000, "Tesla": 1200000, "Minibus": 800000}

def buat_kendaraan(tipe, plat, harga, nama=None, mesin=None):
    # "Pabrik kendaraan": diberi nama tipe (teks), mengembalikan objek yang sesuai.
    # Dipakai saat memuat JSON dan saat menambah kendaraan lewat menu.
    if tipe == "Minibus":
        return Minibus(nama, plat, harga, mesin)   # Minibus tidak punya konstruktor sendiri, jadi butuh 4 data
    return TIPE[tipe](plat, harga)


def input_angka(pesan, minimal, maksimal):
    """Minta angka dalam rentang tertentu. Mengetik 0 berarti batal (hasilnya None)."""
    while True:                               # ulangi terus sampai pengguna mengetik yang benar
        s = input(pesan).strip()
        if s.isdigit() and (int(s) == 0 or minimal <= int(s) <= maksimal):
            return int(s) if int(s) != 0 else None
        print(f"  Masukkan angka {minimal}-{maksimal} (0 = batal).")


def pilih(daftar, judul, tampil):
    """Tampilkan daftar bernomor, lalu kembalikan item yang dipilih pengguna (atau None kalau batal)."""
    if not daftar:
        print("  (daftar kosong)")
        return None
    print(judul)
    for i, item in enumerate(daftar, 1):      # enumerate(..., 1) = memberi nomor urut mulai dari 1
        print(f"  {i}. {tampil(item)}")
    n = input_angka("Pilih nomor (0 = batal): ", 1, len(daftar))
    return daftar[n - 1] if n else None


def data_awal():
    # Data contoh kalau belum ada file JSON, sama seperti bagian demo di kode aslimu.
    rental = RentalMobil("Maju Jaya")
    g1, g2 = Garasi("Garasi Pusat"), Garasi("Garasi Premium")
    g1.tambah(Avanza("L 1234 AB")); g1.tambah(Brio("L 5678 CD"))
    g2.tambah(Tesla("L 9999 EV")); g2.tambah(Minibus("Hiace", "L 7777 XY", 800000, "2.8L Diesel"))
    rental.tambah_garasi(g1); rental.tambah_garasi(g2)
    rental.pelanggan.append(Pelanggan("Budi", "3501xxxx"))
    rental.montir.append(Montir("Pak Joko"))
    return rental


def status(k):
    return "Tersedia" if k.tersedia else "Disewa"


# ----- fungsi-fungsi menu: satu fungsi untuk satu pilihan di layar -----
# Catatan: fungsi menu ini kadang membaca k._kondisi (protected). Itu masih
# diperbolehkan karena menu dianggap bagian dari "sistem rental" itu sendiri.
def menu_armada(r):
    print("\n=== DAFTAR ARMADA ===")
    for g in r.garasi:
        print(f"[{g.nama}]")
        for k in g.isi:
            # k.get_harga() dipakai karena harga private: lewat pintu resmi (getter)
            print(f"  - {k.nama:<14} {k.plat:<11} {k.bahan_bakar():<8} "
                  f"Rp{k.get_harga():>10,.0f}/hari  kondisi {k._kondisi}%  {status(k)}")


def menu_detail(r):
    item = pilih(r.semua_kendaraan(), "\nPilih kendaraan:", lambda gk: f"{gk[1].nama} [{gk[1].plat}]")
    if item:
        k = item[1]
        print(k.info())
        # Dua baris ini memanggil method yang sama (biaya_sewa) dengan hasil beda-beda
        # tergantung jenis mobil. Itulah polymorphism yang bisa kamu tunjukkan ke dosen.
        print(f"Biaya sewa 3 hari: Rp{k.biaya_sewa(3):,.0f} | 7 hari: Rp{k.biaya_sewa(7):,.0f}")
        if isinstance(k, MobilListrik):       # isinstance = "apakah objek ini termasuk keluarga MobilListrik?"
            print(k.isi_baterai())


def menu_pelanggan(r):
    print("\n=== DAFTAR PELANGGAN ===")
    if not r.pelanggan: print("  (belum ada)")
    for i, p in enumerate(r.pelanggan, 1):
        print(f"  {i}. {p.nama} (KTP {p.no_ktp})")


def menu_transaksi(r):
    print("\n=== RIWAYAT TRANSAKSI ===")
    if not r.transaksi: print("  (belum ada)")
    for i, t in enumerate(r.transaksi, 1):
        print(f"  {i}. {t.struk()} [{'Berjalan' if t.aktif else 'Selesai'}]")


def menu_tambah_kendaraan(r):
    if not r.garasi:
        print("Belum ada garasi."); return
    tipe = pilih(["Avanza", "Brio", "Tesla", "Minibus"], "\nTipe kendaraan:", lambda x: x)
    if not tipe: return
    plat = input("Plat nomor: ").strip().upper()
    if not plat or any(k.plat == plat for _, k in r.semua_kendaraan()):
        print("Plat kosong atau sudah terdaftar."); return   # plat harus unik, seperti di dunia nyata
    nama = mesin = None
    if tipe == "Minibus":
        nama = input("Nama minibus: ").strip() or "Minibus"
        mesin = input("Jenis mesin: ").strip() or "Diesel"
    h = input("Harga sewa/hari (Enter = harga standar): ").strip()
    if h and not h.isdigit():
        print("Harga harus angka."); return
    k = buat_kendaraan(tipe, plat, int(h or HARGA_STANDAR[tipe]), nama, mesin)
    g = pilih(r.garasi, "\nSimpan di garasi:", lambda x: x.nama)
    if g:
        g.tambah(k)                           # AGGREGATION: mobil dibuat di luar, lalu dititipkan ke garasi
        print(f"{k.nama} [{k.plat}] ditambahkan ke {g.nama}.")


def menu_tambah_pelanggan(r):
    nama = input("\nNama pelanggan: ").strip()
    ktp = input("No. KTP: ").strip()
    if not nama or not ktp or any(p.no_ktp == ktp for p in r.pelanggan):
        print("Data kosong atau No. KTP sudah terdaftar."); return
    r.pelanggan.append(Pelanggan(nama, ktp))
    print(f"Pelanggan {nama} didaftarkan.")


def menu_sewa(r):
    p = pilih(r.pelanggan, "\nPilih pelanggan:", lambda x: f"{x.nama} ({x.no_ktp})")
    if not p: return
    bebas = [k for _, k in r.semua_kendaraan() if k.tersedia]   # hanya mobil yang belum disewa yang ditampilkan
    k = pilih(bebas, "\nKendaraan tersedia:", lambda x: f"{x.nama} [{x.plat}] Rp{x.get_harga():,.0f}/hari")
    if not k: return
    hari = input_angka("Lama sewa (hari, 1-365): ", 1, 365)
    if hari:
        print("Berhasil:", r.sewa(p, k, hari).struk())   # ASSOCIATION dibuat lewat method sewa()


def menu_kembali(r):
    aktif = [t for t in r.transaksi if t.aktif]
    t = pilih(aktif, "\nTransaksi berjalan:", lambda x: x.struk())
    if t:
        t.selesai()
        print(f"{t.kendaraan.nama} sudah dikembalikan.")


def menu_servis(r):
    m = pilih(r.montir, "\nPilih montir:", lambda x: x.nama)
    if not m: return
    item = pilih(r.semua_kendaraan(), "\nKendaraan yang diservis:",
                 lambda gk: f"{gk[1].nama} [{gk[1].plat}] kondisi {gk[1]._kondisi}%")
    if item:
        print(m.servis(item[1]))


def menu_ubah_harga(r):
    item = pilih(r.semua_kendaraan(), "\nPilih kendaraan:",
                 lambda gk: f"{gk[1].nama} [{gk[1].plat}] Rp{gk[1].get_harga():,.0f}")
    if not item: return
    h = input("Harga baru: ").strip()
    if h.isdigit() and int(h) > 0:
        item[1].set_harga(int(h))             # ENCAPSULATION: ubah harga lewat setter (pintu resmi), bukan langsung
        print("Harga diperbarui:", f"Rp{item[1].get_harga():,.0f}")
    else:
        print("Harga tidak valid, tidak diubah.")


def menu_simpan(r):
    r.simpan()
    print(f"Data tersimpan ke {FILE_JSON}")


# Daftar menu: nomor -> (tulisan di layar, fungsi yang dijalankan).
# Jadi kalau mau menambah menu baru, cukup tambah satu baris di sini.
MENU = {
    1: ("Lihat daftar armada", menu_armada),
    2: ("Detail & biaya sewa kendaraan", menu_detail),
    3: ("Lihat daftar pelanggan", menu_pelanggan),
    4: ("Lihat riwayat transaksi", menu_transaksi),
    5: ("Tambah kendaraan", menu_tambah_kendaraan),
    6: ("Tambah pelanggan", menu_tambah_pelanggan),
    7: ("Sewa kendaraan", menu_sewa),
    8: ("Kembalikan kendaraan", menu_kembali),
    9: ("Servis kendaraan", menu_servis),
    10: ("Ubah harga sewa", menu_ubah_harga),
    11: ("Simpan data ke JSON", menu_simpan),
}


def main():
    # Langkah awal: coba muat data lama. Kalau filenya belum ada atau rusak, pakai data contoh.
    try:
        rental = RentalMobil.muat()
        print(f"Data dimuat dari {FILE_JSON}")
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        rental = data_awal()
        print("Memakai data awal (belum ada file JSON yang valid).")

    while True:                               # loop menu: terus tampil sampai pengguna memilih 0
        print(f"\n===== RENTAL {rental.nama.upper()} =====")
        for no, (label, _) in MENU.items():
            print(f"{no:>2}. {label}")
        print(" 0. Keluar")
        pilihan = input("Pilih menu: ").strip()
        if pilihan == "0":
            if input("Simpan data sebelum keluar? (y/n): ").strip().lower() == "y":
                menu_simpan(rental)
            print("Sampai jumpa!")
            break
        if pilihan.isdigit() and int(pilihan) in MENU:
            MENU[int(pilihan)][1](rental)     # jalankan fungsi yang cocok dengan nomor yang dipilih
        else:
            print("Menu tidak dikenal.")


if __name__ == "__main__":
    main()
