# DESIGN_load - Kelompok 1 / T3 Kota Bogor

Desain ini memuat snapshot beku BMKG dari `data/raw/t3_publik/k1/`. Semua timestamp analitik
menggunakan waktu lokal WIB; `utc_datetime` dipertahankan untuk audit. Kolom `vs` dan `vs_text`
tidak dimuat karena profiling membuktikan keduanya kosong pada seluruh 1.156 baris.

## Alur sumber -> staging -> dim -> fact

```text
desa.csv -----------------> stg_desa -----------------> dim_wilayah (SCD Type 2) ----+
prakiraan_cuaca.csv ------> stg_prakiraan_cuaca -----> dim_slot (Type 0) ------------+--> fact_prakiraan_cuaca
generator tanggal ------------------------------------> dim_date (Type 0) -----------+
stg_prakiraan_cuaca ----------------------------------> dim_cuaca (Type 1) ----------+
```

Staging menormalkan spasi, tipe angka, tanggal, dan timestamp, tetapi tidak memperbaiki data
diam-diam. Baris invalid dipertahankan untuk diuji atau diarahkan ke anggota dimensi `-1`.

## Strategi per tabel

| # | Tabel | Sumber | Grain / natural key | Strategi | Partisi / window | Kapan dapat menggandakan baris |
|---|---|---|---|---|---|---|
| 1 | `stg_desa` | `desa.csv` | satu desa; `kode` | `CREATE OR REPLACE` dari snapshot | seluruh file | Tidak pada strategi ini; duplikat hanya berasal dari source dan ditangkap test. |
| 2 | `stg_prakiraan_cuaca` | `prakiraan_cuaca.csv` | `adm4 + local_datetime + analysis_date` | `CREATE OR REPLACE`, trim dan `TRY_CAST` | `analysis_date` | Tidak pada strategi ini; baris source dengan natural key sama tetap terlihat dan memblokir load. |
| 3 | `dim_date` | generator yang diberikan | `full_date` | full rebuild `CREATE OR REPLACE` | 2024-01-01 s.d. 2027-12-31 | Tidak; rentang dibuat ulang dan bukan di-append. |
| 4 | `dim_wilayah` | `stg_desa` | `wilayah_nk = kode/adm4` | incremental SCD Type 2: compare-current, close, insert | `valid_from = 2026-09-19` untuk snapshot K1 | Jika versi baru di-insert tanpa menutup current lama, atau rerun tidak mencocokkan `wilayah_nk + hash atribut`. |
| 5 | `dim_slot` | distinct waktu lokal dari staging cuaca | `jam_lokal` | insert-only idempoten dengan anti-join natural key | 16 nilai waktu lokal pada snapshot | Jika setiap rerun memberi key baru tanpa anti-join pada `jam_lokal`. |
| 6 | `dim_cuaca` | distinct kode cuaca dari staging cuaca | `weather_code` | upsert Type 1; label dikoreksi dengan overwrite | 5 kode pada snapshot | Jika `weather_desc` dipakai sebagai key atau upsert tidak mencocokkan `weather_code`; kode 0 dan 1 sama-sama "Cerah". |
| 7 | `fact_prakiraan_cuaca` | staging cuaca + lookup empat dimensi | `wilayah_sk + forecast_local_ts + analysis_ts` | delete-and-insert per snapshot | `analysis_date` | Jika rerun memakai append polos tanpa menghapus partisi snapshot atau tanpa unique key grain. |

## Normalisasi staging

- `analysis_date`, `utc_datetime`, dan `local_datetime` diparse sebagai timestamp.
- `t`, `hu`, `tp`, `tcc`, `ws`, dan `wd_deg` memakai `TRY_CAST`; kegagalan cast tetap `NULL`
  dan dihitung test, bukan diubah menjadi nol.
- `time_index` dipecah menjadi `horizon_start_hour` dan `horizon_end_hour`; nilai ini bukan jam
  dinding karena 625 baris mempunyai angka awal lebih dari 23.
- `weather` diubah ke integer dan menjadi natural key `dim_cuaca`; deskripsi tidak menjadi key.
- `local_datetime` menjadi dasar `date_sk` dan `slot_sk`; selisih UTC->WIB yang benar adalah 7 jam.

## Algoritme SCD Type 2 `dim_wilayah`

1. Cocokkan `stg_desa.kode` ke baris `dim_wilayah` dengan `is_current = TRUE`.
2. Hitung hash atribut `desa, kecamatan_nk, kecamatan, kabkot_nk, kabkot, provinsi_nk, provinsi`.
3. Jika natural key baru, insert versi dengan `valid_from = tanggal snapshot`,
   `valid_to = 9999-12-31`, dan `is_current = TRUE`.
4. Jika natural key sama tetapi hash berubah, tutup versi lama dengan
   `valid_to = tanggal snapshot` dan `is_current = FALSE`, lalu insert versi baru.
5. Jika natural key dan hash sama, jangan melakukan apa pun. Langkah ini membuat rerun idempoten.

Surrogate key versi baru dialokasikan secara deterministik dalam batch:
`max(wilayah_sk) + row_number() over (order by wilayah_nk)`.

## Natural key upsert

- `dim_wilayah`: `wilayah_nk` untuk mencari versi current; histori unik pada
  `(wilayah_nk, valid_from)`.
- `dim_slot`: `jam_lokal`.
- `dim_cuaca`: `weather_code`.
- fact: `(wilayah_sk, forecast_local_ts, analysis_ts)`.

## Urutan dependency

1. Buat `stg_desa` dan `stg_prakiraan_cuaca` agar semua langkah berikut membaca hasil cast yang sama.
2. Muat `dim_date`, lalu `dim_wilayah`, `dim_slot`, dan `dim_cuaca`; keempatnya independen setelah staging.
3. Jalankan enam test source/staging; pelanggaran `blocking` menghentikan pemuatan fact.
4. Muat `fact_prakiraan_cuaca` terakhir karena setiap baris membutuhkan empat surrogate key.
5. Jalankan rekonsiliasi: jumlah fact untuk snapshot harus 1.156 dan tidak ada FK `NULL`.

## Kebijakan baris tidak cocok

Lookup dimensi yang gagal memakai anggota Unknown (`*_sk = -1`) supaya jumlah source tetap dapat
direkonsiliasi. Baris tidak pernah dibuang tanpa catatan. Akan tetapi, duplikat grain, curah hujan
negatif, atau natural key kosong adalah `blocking` dan menghentikan partisi sebelum fact ditulis.
