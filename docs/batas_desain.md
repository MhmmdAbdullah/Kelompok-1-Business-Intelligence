# Batas desain - pertanyaan yang belum terjawab

## Pertanyaan

Seberapa akurat prakiraan hujan BMKG untuk setiap desa di Kota Bogor dibandingkan cuaca yang
benar-benar terjadi pada slot waktu yang sama?

## Mengapa belum dapat dijawab

Dataset K1 hanya berisi satu snapshot **prakiraan** BMKG. Tidak ada observasi aktual, stasiun
pengukur, radar hujan, maupun label apakah hujan benar-benar terjadi. Karena itu desain ini dapat
menjawab lokasi dan waktu yang diprakirakan hujan, tetapi tidak dapat menghitung akurasi,
precision, recall, bias, atau error prakiraan.

## Data yang dibutuhkan

- Observasi aktual hujan per desa atau titik stasiun dengan timestamp WIB yang sama.
- Pemetaan titik observasi/stasiun ke desa dan aturan interpolasi untuk desa tanpa stasiun.
- Snapshot prakiraan dari beberapa `analysis_ts`, bukan hanya satu snapshot beku.
- Definisi toleransi waktu dan ambang hujan yang disepakati BPBD/BMKG.

Alternatif yang ditolak adalah menganggap nilai prakiraan sebagai kejadian aktual, karena itu akan
menghasilkan evaluasi akurasi yang melingkar dan tidak dapat dipertanggungjawabkan.
