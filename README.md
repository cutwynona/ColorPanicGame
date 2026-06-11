anggota kelompok
Arsha Alifa Mahmud 2408107010097
Cut Wynona Andromeda 2408107010098
Khalisa Humaira 2408107010099


# 🌈 COLOR PANIC!

Color Panic adalah game multiplayer berbasis TCP/UDP yang menguji kecepatan refleks, fokus, dan ketepatan pemain dalam mengenali warna. Pemain harus memilih warna yang sesuai secepat mungkin sebelum waktu habis, sambil menghadapi berbagai serangan (power-up) dari lawan.

## 🎮 Fitur Utama

✓ Sistem permainan terdiri dari 5 ronde.

✓ Setiap ronde berlangsung selama 7 detik.

✓ Warna diacak dari daftar:
`MERAH, BIRU, HIJAU, KUNING, ORANGE, UNGU, PINK, PUTIH`

✓ Live Chat untuk komunikasi antar pemain.

✓ Live Score untuk menampilkan skor secara real-time.

✓ Leaderboard yang menampilkan Juara 1, 2, dan 3 setelah permainan selesai.

## ⚡ Power-Up

Setiap power-up hanya dapat digunakan satu kali selama permainan.

### ❄️ Bom Es

Membekukan kontrol atau input lawan untuk sementara waktu.

### 🐙 Tinta Gurita

Menutupi tampilan lawan dengan layar hitam sehingga warna sulit terlihat.

### 🌪️ Badai Acak

Mengacak posisi tombol warna milik lawan dan mengganggu refleks pemain.

### 🛡️ Perisai

Melindungi pemain dari serangan lawan pada ronde tersebut.

## 🖥️ Cara Bermain (Versi Web)

1. Tunggu ronde dimulai.
2. Perhatikan warna yang muncul pada layar.
3. Klik tombol warna yang sesuai secepat mungkin.
4. Kumpulkan skor sebanyak mungkin dalam 5 ronde.
5. Gunakan power-up secara strategis untuk mengalahkan lawan.

## 💻 Cara Bermain (Versi CLI)

1. Jalankan program client.
2. Masukkan nama pemain.
3. Sistem akan terhubung ke server melalui socket.
4. Warna akan ditampilkan pada terminal menggunakan ANSI Escape Codes.
5. Setiap warna memiliki nomor indeks tertentu.
6. Pemain cukup mengetik nomor warna yang sesuai lalu menekan ENTER.
7. Jika terkena Badai Acak, nomor warna akan berubah secara otomatis.
8. Jika terkena Tinta Gurita, tampilan warna pada terminal akan disamarkan.

## 🏆 Sistem Penilaian

✓ Jawaban benar menambah skor pemain.

✓ Jawaban salah atau terlambat tidak mendapatkan poin.

✓ Pemenang ditentukan berdasarkan total skor tertinggi setelah ronde ke-5 selesai.

## 🛠️ Teknologi yang Digunakan

* Python
* Socket Programming (TCP/UDP)
* Threading
* ANSI Escape Codes
* HTML, CSS, dan JavaScript (versi web)

## 👥 Tim Pengembang

Proyek ini dibuat sebagai implementasi pemrograman jaringan untuk membangun game multiplayer real-time yang interaktif dan kompetitif.
