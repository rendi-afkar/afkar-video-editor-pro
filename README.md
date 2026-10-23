# AFKAR VIDEO EDITOR PRO

**TERMUX EDITION | BY AFKAR**

Video editor CLI untuk Android Termux menggunakan Python dan FFmpeg.

## Fitur
1. Split video berdasarkan durasi atau jumlah bagian
2. Flip horizontal / vertikal
3. Rotate 90° kanan/kiri atau 180°
4. Crop/resize rasio 9:16, 16:9, 1:1 atau crop custom
5. Atur speed 0.25x sampai 4x (video dan audio)
6. Reverse video dan audio
7. Merge beberapa video (dinormalisasi ke MP4 720p agar codec/dimensi seragam)
8. Ekstrak audio MP3
9. Atur brightness, contrast, saturation
10. Kompres video dengan preset kualitas dan resolusi
11. Daftar file input/output
12. Cek FFmpeg

## Instalasi
Buka Termux, lalu jalankan:

```sh
pkg update
pkg upgrade -y
pkg install -y git python python-cryptography ffmpeg clang make
termux-setup-storage
git clone https://github.com/rendi-afkar/afkar-video-editor-pro.git
cd ~/afkar-video-editor-pro
```

Bangun aplikasi dari source code:

```sh
cd ~/afkar-video-editor-pro
make
```

Jalankan:

```sh
./main
```

## Folder video
- Input: `~/afkar-video-editor-pro/input/`
- Output: `~/afkar-video-editor-pro/output/`

Salin video dari Download ke folder input. Contoh jika file ada di Download:

```sh
cp ~/storage/downloads/NAMA_VIDEO.mp4 ~/afkar-video-editor-pro/input/
```

Lalu pilih fitur dari menu. Hasil edit berada di folder `output/`.

## Efek animasi
Untuk mematikan jeda visual terminal (menu tetap berfungsi):

```sh
NO_EFFECTS=1 ./main
```

## Catatan penting
- Split menggunakan stream copy agar cepat; batas potongan dapat bergeser sedikit mengikuti keyframe video.
- Reverse, crop, flip, rotate, speed, color, dan compress biasanya melakukan encoding ulang, sehingga memerlukan waktu dan ruang kosong.
- Reverse pada video panjang dapat menggunakan banyak RAM/penyimpanan.
- Merge melakukan normalisasi setiap klip ke MP4 720p, H.264/AAC untuk meningkatkan kompatibilitas; file sementara dibuat di output lalu dihapus setelah selesai.
- Jika proses gagal, periksa pesan error dan ruang penyimpanan.
- Jangan menutup Termux ketika FFmpeg sedang memproses.
