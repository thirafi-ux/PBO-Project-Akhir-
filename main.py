"""
SIAKAD - Sistem Informasi Akademik Kampus (versi ringkas)
Konsep OOP: Abstraksi, Inheritance, Polymorphism, Encapsulation,
            Association, Aggregation, Composition.
Jalankan: python main.py
"""
import json
import os
from abc import ABC, abstractmethod

FILE_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "siakad_data.json")


# ---------------------------------------------------------------- fungsi bantu
def garis(judul=""):
    print("\n" + "=" * 55)
    if judul:
        print(judul)
        print("=" * 55)


def tanya(teks):
    return input(teks + ": ").strip()


def tanya_angka(teks):
    while True:
        isi = tanya(teks)
        if isi.isdigit():
            return int(isi)
        print("Harus berupa angka.")


def pilih(daftar, judul):
    """Tampilkan daftar bernomor, kembalikan objek yang dipilih."""
    if not daftar:
        print("Data masih kosong.")
        return None
    for i, item in enumerate(daftar, 1):
        print(f"{i}. {item}")
    p = tanya(f"Pilih {judul} (0 = batal)")
    if p.isdigit() and 1 <= int(p) <= len(daftar):
        return daftar[int(p) - 1]
    return None


def jalankan_menu(judul, opsi):
    """Tampilkan menu berulang. opsi = [(label, fungsi), ...]"""
    while True:
        garis(judul)
        for i, (label, _) in enumerate(opsi, 1):
            print(f"{i}. {label}")
        print("0. Kembali / Logout")
        p = tanya("Pilih menu")
        if p == "0":
            return
        if p.isdigit() and 1 <= int(p) <= len(opsi):
            opsi[int(p) - 1][1]()
        else:
            print("Pilihan tidak valid.")


# ------------------------------------------------------------ class akademik
class MataKuliah:
    def __init__(self, kode, nama, sks, semester, prasyarat=None):
        self.kode = kode
        self.nama = nama
        self.sks = sks
        self.semester = semester
        self.prasyarat = prasyarat or []   # self-association: MK butuh MK lain

    def __str__(self):
        syarat = ", ".join(m.kode for m in self.prasyarat) or "-"
        return f"{self.kode} | {self.nama} | {self.sks} SKS | Smt {self.semester} | Prasyarat: {syarat}"


class Jadwal:
    def __init__(self, hari, jam, ruangan):
        self.hari = hari
        self.jam = jam
        self.ruangan = ruangan

    def __str__(self):
        return f"{self.hari} {self.jam} ({self.ruangan})"


class Presensi:
    """Catatan kehadiran satu kelas. Dibuat otomatis oleh Kelas (composition)."""
    STATUS = {"H": "Hadir", "I": "Izin", "S": "Sakit", "A": "Alpa"}

    def __init__(self):
        self.catatan = {}   # {pertemuan: {nim: status}}

    def isi(self, pertemuan, mahasiswa, status):
        self.catatan.setdefault(pertemuan, {})[mahasiswa.nim] = status

    def rekap(self, mahasiswa):
        """Kembalikan (jumlah hadir, total pertemuan)."""
        hadir = sum(1 for p in self.catatan.values() if p.get(mahasiswa.nim) == "Hadir")
        return hadir, len(self.catatan)


class Kelas:
    def __init__(self, matkul, nama, dosen, jadwal, kapasitas):
        self.matkul = matkul        # association ke MataKuliah
        self.nama = nama
        self.dosen = dosen          # association ke Dosen
        self.jadwal = jadwal        # association ke Jadwal
        self.kapasitas = kapasitas
        self.peserta = []           # aggregation: kumpulan Mahasiswa
        self.presensi = Presensi()  # composition: Presensi lahir & mati bersama Kelas

    def cek_kuota(self):
        return len(self.peserta) < self.kapasitas

    def __str__(self):
        return (f"{self.matkul.kode}-{self.nama} {self.matkul.nama} | {self.dosen.nama} | "
                f"{self.jadwal} | {len(self.peserta)}/{self.kapasitas}")


class Nilai:
    BATAS = [(85, "A", 4.0), (80, "A-", 3.7), (75, "B+", 3.3), (70, "B", 3.0), (65, "B-", 2.7),
             (60, "C+", 2.3), (55, "C", 2.0), (40, "D", 1.0), (0, "E", 0.0)]

    def __init__(self, matkul, angka):
        self.matkul = matkul
        self.angka = angka

    def _cari(self):
        return next(b for b in self.BATAS if self.angka >= b[0])

    @property
    def huruf(self):
        return self._cari()[1]

    @property
    def bobot(self):
        return self._cari()[2]

    def lulus(self):
        return self.bobot >= 2.0


class KHS:
    """Kartu Hasil Studi: menghitung IPS & IPK dari daftar Nilai mahasiswa."""

    def __init__(self, mahasiswa):
        self.mahasiswa = mahasiswa

    @staticmethod
    def hitung(daftar_nilai):
        sks = sum(n.matkul.sks for n in daftar_nilai)
        if sks == 0:
            return 0.0
        return sum(n.matkul.sks * n.bobot for n in daftar_nilai) / sks

    def tampilkan(self):
        semua = self.mahasiswa.nilai
        if not semua:
            print("Belum ada nilai.")
            return
        for smt in sorted({n.matkul.semester for n in semua}):
            per_smt = [n for n in semua if n.matkul.semester == smt]
            print(f"\nSemester {smt}")
            for n in per_smt:
                print(f"  {n.matkul.kode} {n.matkul.nama:<32} {n.matkul.sks} SKS  {n.angka:>3}  {n.huruf}")
            print(f"  IPS: {self.hitung(per_smt):.2f}")
        print(f"\nIPK: {self.hitung(semua):.2f}")


class KRS:
    """Kartu Rencana Studi. Use case 'Isi KRS' meng-include 4 proses di bawah."""

    def __init__(self, mahasiswa):
        self.mahasiswa = mahasiswa
        self.daftar_kelas = []

    def cek_prasyarat(self, kelas):
        belum = [m.kode for m in kelas.matkul.prasyarat if not self.mahasiswa.sudah_lulus(m)]
        return not belum, "Prasyarat belum lulus: " + ", ".join(belum)

    def cek_kuota(self, kelas):
        return kelas.cek_kuota(), "Kuota kelas sudah penuh"

    def pilih_mata_kuliah(self, kelas):
        if any(k.matkul is kelas.matkul for k in self.daftar_kelas):
            return "GAGAL: mata kuliah sudah ada di KRS"
        for cek in (self.cek_prasyarat, self.cek_kuota):
            ok, pesan = cek(kelas)
            if not ok:
                return "GAGAL: " + pesan
        self.daftar_kelas.append(kelas)
        return "Berhasil dipilih (jangan lupa Simpan KRS)"

    def total_sks(self):
        return sum(k.matkul.sks for k in self.daftar_kelas)

    def simpan(self):
        for kelas in list(self.daftar_kelas):
            if self.mahasiswa in kelas.peserta:
                continue
            if kelas.cek_kuota():
                kelas.peserta.append(self.mahasiswa)
            else:
                self.daftar_kelas.remove(kelas)
                print(f"Kelas {kelas.matkul.nama} penuh, dikeluarkan dari KRS.")
        print(f"KRS tersimpan. Total {self.total_sks()} SKS.")

    def tampilkan(self):
        if not self.daftar_kelas:
            print("KRS masih kosong.")
        for k in self.daftar_kelas:
            print(f"- {k}")
        print(f"Total SKS: {self.total_sks()}")


# ------------------------------------------------------------------- pengguna
class Pengguna(ABC):
    """Class abstrak: induk dari Mahasiswa, Dosen, dan Admin."""

    def __init__(self, nama, username, password):
        self.nama = nama
        self.username = username
        self.__password = password     # encapsulation: atribut private

    def login(self, username, password):
        return self.username == username and self.__password == password

    def ambil_password(self):
        return self.__password         # dipakai Database saat menyimpan

    @abstractmethod
    def menu(self, sistem):
        """Setiap turunan wajib punya menu sendiri (polymorphism)."""


class Mahasiswa(Pengguna):
    def __init__(self, nim, nama, prodi, semester, email, password="12345"):
        super().__init__(nama, nim, password)
        self.nim = nim
        self.prodi = prodi
        self.semester = semester
        self.email = email
        self.nilai = []              # aggregation: daftar Nilai
        self.krs = KRS(self)         # composition: KRS milik mahasiswa
        self.khs = KHS(self)         # composition

    def sudah_lulus(self, matkul):
        return any(n.matkul is matkul and n.lulus() for n in self.nilai)

    def terima_nilai(self, matkul, angka):
        self.nilai = [n for n in self.nilai if n.matkul is not matkul]
        self.nilai.append(Nilai(matkul, angka))

    def lihat_profil(self):
        garis("PROFIL MAHASISWA")
        print(f"NIM      : {self.nim}\nNama     : {self.nama}\nProdi    : {self.prodi}")
        print(f"Semester : {self.semester}\nEmail    : {self.email}")

    def isi_krs(self, sistem):
        def pilih_kelas():
            tersedia = [k for k in sistem.kelas if k not in self.krs.daftar_kelas]
            kelas = pilih(tersedia, "kelas")
            if kelas:
                print(self.krs.pilih_mata_kuliah(kelas))
        jalankan_menu("ISI KRS", [
            ("Pilih mata kuliah (cek prasyarat & kuota)", pilih_kelas),
            ("Lihat KRS saya", self.krs.tampilkan),
            ("Simpan KRS", self.krs.simpan),
        ])

    def lihat_jadwal(self, sistem):
        garis("JADWAL KULIAH")
        for k in sorted(sistem.kelas_mahasiswa(self), key=lambda x: x.jadwal.hari):
            print(f"{k.jadwal} | {k.matkul.nama} | {k.dosen.nama}")

    def lihat_khs(self, sistem):
        garis("NILAI / KHS")
        self.khs.tampilkan()

    def lihat_presensi(self, sistem):
        garis("PRESENSI")
        for k in sistem.kelas_mahasiswa(self):
            hadir, total = k.presensi.rekap(self)
            persen = hadir / total * 100 if total else 0
            print(f"{k.matkul.nama:<32} Hadir {hadir}/{total} ({persen:.0f}%)")

    def menu(self, sistem):
        jalankan_menu(f"MENU MAHASISWA - {self.nama}", [
            ("Lihat Profil", self.lihat_profil),
            ("Isi KRS", lambda: self.isi_krs(sistem)),
            ("Lihat Jadwal Kuliah", lambda: self.lihat_jadwal(sistem)),
            ("Lihat Nilai/KHS", lambda: self.lihat_khs(sistem)),
            ("Lihat Presensi", lambda: self.lihat_presensi(sistem)),
        ])


class Dosen(Pengguna):
    def __init__(self, nidn, nama, username, prodi, password="12345"):
        super().__init__(nama, username, password)
        self.nidn = nidn
        self.prodi = prodi

    def lihat_jadwal_mengajar(self, sistem):
        garis("JADWAL MENGAJAR")
        for k in sistem.kelas_dosen(self):
            print(f"{k.jadwal} | {k.matkul.nama} ({k.nama}) | {len(k.peserta)} mhs")

    def kelola_presensi(self, sistem):
        kelas = pilih(sistem.kelas_dosen(self), "kelas")
        if not kelas:
            return
        pertemuan = tanya_angka("Pertemuan ke")
        print("Isi: H=Hadir, I=Izin, S=Sakit, A=Alpa (kosong = Hadir)")
        for mhs in kelas.peserta:
            kode = tanya(f"  {mhs.nim} {mhs.nama}").upper()
            kelas.presensi.isi(pertemuan, mhs, Presensi.STATUS.get(kode, "Hadir"))
        print("Presensi tersimpan.")

    def input_nilai(self, sistem):
        kelas = pilih(sistem.kelas_dosen(self), "kelas")
        if not kelas:
            return
        for mhs in kelas.peserta:
            angka = tanya(f"  Nilai {mhs.nim} {mhs.nama} (0-100, kosong = lewati)")
            if angka.isdigit() and 0 <= int(angka) <= 100:
                mhs.terima_nilai(kelas.matkul, int(angka))
        print("Nilai tersimpan.")

    def menu(self, sistem):
        jalankan_menu(f"MENU DOSEN - {self.nama}", [
            ("Lihat Jadwal Mengajar", lambda: self.lihat_jadwal_mengajar(sistem)),
            ("Kelola Presensi", lambda: self.kelola_presensi(sistem)),
            ("Input Nilai", lambda: self.input_nilai(sistem)),
        ])


class Admin(Pengguna):
    def __init__(self):
        super().__init__("Administrator", "admin", "admin123")

    def kelola_mahasiswa(self, sistem):
        def tambah():
            nim = tanya("NIM")
            if sistem.cari_pengguna(nim):
                print("NIM sudah dipakai.")
                return
            sistem.pengguna.append(Mahasiswa(nim, tanya("Nama"), tanya("Prodi"),
                                             tanya_angka("Semester"), tanya("Email")))
            print("Mahasiswa ditambahkan (password awal: 12345).")

        def hapus():
            mhs = pilih(sistem.daftar(Mahasiswa), "mahasiswa")
            if mhs:
                for k in sistem.kelas:
                    if mhs in k.peserta:
                        k.peserta.remove(mhs)
                sistem.pengguna.remove(mhs)
                print("Mahasiswa dihapus.")

        jalankan_menu("KELOLA DATA MAHASISWA", [
            ("Lihat data", lambda: [print(f"{m.nim} | {m.nama} | {m.prodi} | Smt {m.semester}")
                                    for m in sistem.daftar(Mahasiswa)]),
            ("Tambah mahasiswa", tambah), ("Hapus mahasiswa", hapus)])

    def kelola_dosen(self, sistem):
        def tambah():
            nidn = tanya("NIDN")
            if sistem.cari_pengguna(nidn):
                print("NIDN sudah dipakai.")
                return
            sistem.pengguna.append(Dosen(nidn, tanya("Nama"), nidn, tanya("Prodi")))
            print("Dosen ditambahkan (username = NIDN, password: 12345).")

        jalankan_menu("KELOLA DATA DOSEN", [
            ("Lihat data", lambda: [print(f"{d.nidn} | {d.nama} | {d.prodi}")
                                    for d in sistem.daftar(Dosen)]),
            ("Tambah dosen", tambah)])

    def kelola_mata_kuliah(self, sistem):
        def tambah():
            kode = tanya("Kode MK").upper()
            if any(m.kode == kode for m in sistem.matkul):
                print("Kode sudah ada.")
                return
            mk = MataKuliah(kode, tanya("Nama"), tanya_angka("SKS"), tanya_angka("Semester"))
            while tanya("Tambah prasyarat? (y/n)").lower() == "y":
                syarat = pilih(sistem.matkul, "prasyarat")
                if syarat and syarat not in mk.prasyarat:
                    mk.prasyarat.append(syarat)
            sistem.matkul.append(mk)
            print("Mata kuliah ditambahkan.")

        jalankan_menu("KELOLA MATA KULIAH", [
            ("Lihat data", lambda: [print(m) for m in sistem.matkul]),
            ("Tambah mata kuliah", tambah)])

    def kelola_kelas(self, sistem):
        def tambah():
            mk = pilih(sistem.matkul, "mata kuliah")
            dosen = pilih(sistem.daftar(Dosen), "dosen") if mk else None
            if not (mk and dosen):
                return
            sistem.kelas.append(Kelas(mk, tanya("Nama kelas (mis. A)"), dosen,
                                      self.buat_jadwal(), tanya_angka("Kapasitas")))
            print("Kelas ditambahkan.")

        jalankan_menu("KELOLA KELAS", [
            ("Lihat data", lambda: [print(k) for k in sistem.kelas]),
            ("Tambah kelas", tambah)])

    def kelola_jadwal(self, sistem):
        kelas = pilih(sistem.kelas, "kelas yang jadwalnya diubah")
        if kelas:
            kelas.jadwal = self.buat_jadwal()
            print("Jadwal diperbarui.")

    @staticmethod
    def buat_jadwal():
        return Jadwal(tanya("Hari"), tanya("Jam (mis. 08:00-10:30)"), tanya("Ruangan"))

    def menu(self, sistem):
        jalankan_menu("MENU ADMIN", [
            ("Kelola Data Mahasiswa", lambda: self.kelola_mahasiswa(sistem)),
            ("Kelola Data Dosen", lambda: self.kelola_dosen(sistem)),
            ("Kelola Mata Kuliah", lambda: self.kelola_mata_kuliah(sistem)),
            ("Kelola Kelas", lambda: self.kelola_kelas(sistem)),
            ("Kelola Jadwal", lambda: self.kelola_jadwal(sistem)),
            ("Lihat Laporan Akademik", lambda: LaporanAkademik(sistem).tampilkan()),
        ])


class LaporanAkademik:
    def __init__(self, sistem):
        self.sistem = sistem

    def tampilkan(self):
        s = self.sistem
        mahasiswa = s.daftar(Mahasiswa)
        garis("LAPORAN AKADEMIK")
        print(f"Mahasiswa: {len(mahasiswa)} | Dosen: {len(s.daftar(Dosen))} | "
              f"Mata Kuliah: {len(s.matkul)} | Kelas: {len(s.kelas)}")
        print("\nIPK mahasiswa:")
        for m in mahasiswa:
            print(f"  {m.nim} {m.nama:<20} IPK {KHS.hitung(m.nilai):.2f}")
        print("\nIsi kelas:")
        for k in s.kelas:
            print(f"  {k.matkul.kode}-{k.nama:<3} {k.matkul.nama:<32} {len(k.peserta)}/{k.kapasitas}")


# --------------------------------------------------------- penyimpanan & sistem
class Database:
    """Menyimpan & membaca seluruh data sistem dalam file JSON."""

    @staticmethod
    def simpan(sistem):
        data = {
            "mata_kuliah": [
                {"kode": m.kode, "nama": m.nama, "sks": m.sks, "semester": m.semester,
                 "prasyarat": [p.kode for p in m.prasyarat]} for m in sistem.matkul],
            "mahasiswa": [
                {"nim": m.nim, "nama": m.nama, "prodi": m.prodi, "semester": m.semester,
                 "email": m.email, "password": m.ambil_password(),
                 "nilai": [{"kode_mk": n.matkul.kode, "angka": n.angka} for n in m.nilai],
                 "krs": [Database.id_kelas(k) for k in m.krs.daftar_kelas]}
                for m in sistem.daftar(Mahasiswa)],
            "dosen": [
                {"nidn": d.nidn, "nama": d.nama, "username": d.username, "prodi": d.prodi,
                 "password": d.ambil_password()} for d in sistem.daftar(Dosen)],
            "kelas": [
                {"id": Database.id_kelas(k), "kode_mk": k.matkul.kode, "nama": k.nama,
                 "dosen": k.dosen.username, "kapasitas": k.kapasitas,
                 "jadwal": {"hari": k.jadwal.hari, "jam": k.jadwal.jam, "ruangan": k.jadwal.ruangan},
                 "peserta": [m.nim for m in k.peserta], "presensi": k.presensi.catatan}
                for k in sistem.kelas],
        }
        os.makedirs(os.path.dirname(FILE_DATA), exist_ok=True)
        with open(FILE_DATA, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def muat():
        """Baca JSON lalu susun kembali menjadi objek. None jika file belum ada/rusak."""
        try:
            with open(FILE_DATA, encoding="utf-8") as f:
                data = json.load(f)
            return Database.susun(data)
        except Exception:
            return None

    @staticmethod
    def id_kelas(k):
        return f"{k.matkul.kode}-{k.nama}"

    @staticmethod
    def susun(data):
        s = SIAKAD(data_awal=False)
        mk = {}
        for d in data["mata_kuliah"]:
            mk[d["kode"]] = MataKuliah(d["kode"], d["nama"], d["sks"], d["semester"])
        for d in data["mata_kuliah"]:
            mk[d["kode"]].prasyarat = [mk[k] for k in d["prasyarat"]]
        s.matkul = list(mk.values())

        dosen = {}
        for d in data["dosen"]:
            dosen[d["username"]] = Dosen(d["nidn"], d["nama"], d["username"], d["prodi"], d["password"])
        mhs = {}
        for d in data["mahasiswa"]:
            m = Mahasiswa(d["nim"], d["nama"], d["prodi"], d["semester"], d["email"], d["password"])
            m.nilai = [Nilai(mk[n["kode_mk"]], n["angka"]) for n in d["nilai"]]
            mhs[m.nim] = m
        s.pengguna += list(dosen.values()) + list(mhs.values())

        kelas = {}
        for d in data["kelas"]:
            j = d["jadwal"]
            k = Kelas(mk[d["kode_mk"]], d["nama"], dosen[d["dosen"]],
                      Jadwal(j["hari"], j["jam"], j["ruangan"]), d["kapasitas"])
            k.peserta = [mhs[nim] for nim in d["peserta"]]
            k.presensi.catatan = {int(p): v for p, v in d["presensi"].items()}
            kelas[d["id"]] = k
        s.kelas = list(kelas.values())
        for d in data["mahasiswa"]:
            mhs[d["nim"]].krs.daftar_kelas = [kelas[i] for i in d["krs"]]
        return s


class SIAKAD:
    """Class pengendali: menyimpan semua data dan menghubungkan seluruh class."""

    def __init__(self, data_awal=True):
        self.pengguna = [Admin()]
        self.matkul = []
        self.kelas = []
        if data_awal:
            self.isi_data_awal()

    def daftar(self, tipe):
        return [p for p in self.pengguna if isinstance(p, tipe)]

    def cari_pengguna(self, username):
        return next((p for p in self.pengguna if p.username == username), None)

    def kelas_mahasiswa(self, mhs):
        return [k for k in self.kelas if mhs in k.peserta]

    def kelas_dosen(self, dosen):
        return [k for k in self.kelas if k.dosen is dosen]

    def login(self):
        garis("LOGIN SIAKAD")
        akun = self.cari_pengguna(tanya("Username"))
        if akun and akun.login(akun.username, tanya("Password")):
            return akun
        print("Username atau password salah.")
        return None

    def run(self):
        while True:
            garis("SIAKAD - SISTEM INFORMASI AKADEMIK KAMPUS")
            print("1. Login\n0. Keluar")
            if tanya("Pilih") == "0":
                Database.simpan(self)
                print("Data disimpan. Sampai jumpa!")
                return
            akun = self.login()
            if akun:
                akun.menu(self)      # polymorphism: menu menyesuaikan jenis akun
                Database.simpan(self)

    def isi_data_awal(self):
        if1 = MataKuliah("IF101", "Dasar Pemrograman", 3, 1)
        if2 = MataKuliah("IF201", "Struktur Data", 3, 2, [if1])
        pbo = MataKuliah("IF202", "Pemrograman Berorientasi Objek", 3, 3, [if1])
        basdat = MataKuliah("IF203", "Basis Data", 3, 3, [if1])
        jarkom = MataKuliah("IF204", "Jaringan Komputer", 3, 3)
        rpl = MataKuliah("IF205", "Rekayasa Perangkat Lunak", 3, 3)
        pbo2 = MataKuliah("IF301", "PBO Lanjut", 3, 4, [pbo])
        self.matkul = [if1, if2, pbo, basdat, jarkom, rpl, pbo2]

        budi = Dosen("0012345678", "Dr. Budi Santoso", "D001", "Teknik Informatika")
        siti = Dosen("0012345679", "Siti Rahma, M.Kom.", "D002", "Teknik Informatika")
        fabian = Mahasiswa("230001", "Fabian Thirafi", "Teknik Informatika", 3, "fabian@example.com")
        rizky = Mahasiswa("230002", "Rizky Pratama", "Teknik Informatika", 3, "rizky@example.com")
        self.pengguna += [budi, siti, fabian, rizky]

        k_pbo = Kelas(pbo, "A", budi, Jadwal("Senin", "08:00-10:30", "RKBF-201"), 30)
        k_bd = Kelas(basdat, "A", siti, Jadwal("Selasa", "08:00-10:30", "RKBF-202"), 30)
        k_jar = Kelas(jarkom, "A", budi, Jadwal("Rabu", "10:00-12:30", "Lab Jaringan"), 25)
        k_rpl = Kelas(rpl, "A", siti, Jadwal("Kamis", "13:00-15:30", "RKBF-203"), 1)   # kuota 1 (untuk demo)
        k_pbo2 = Kelas(pbo2, "A", budi, Jadwal("Jumat", "08:00-10:30", "RKBF-204"), 30)
        self.kelas = [k_pbo, k_bd, k_jar, k_rpl, k_pbo2]

        fabian.terima_nilai(if1, 85)
        fabian.terima_nilai(if2, 82)
        rizky.terima_nilai(if1, 75)

        for kelas in (k_pbo, k_bd, k_jar):          # KRS Fabian sudah terisi
            fabian.krs.daftar_kelas.append(kelas)
            kelas.peserta.append(fabian)
        rizky.krs.daftar_kelas.append(k_rpl)          # Rizky mengisi kuota RPL
        k_rpl.peserta.append(rizky)
        k_pbo.presensi.isi(1, fabian, "Hadir")


if __name__ == "__main__":
    (Database.muat() or SIAKAD()).run()
