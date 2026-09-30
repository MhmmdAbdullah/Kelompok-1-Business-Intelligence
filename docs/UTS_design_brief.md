# Dokumen Desain UTS Business Intelligence

**Kelompok:** 1  
**Topik:** T3 - Cuaca Ekstrem per Desa (BMKG)  
**Slice:** K1 - Kota Bogor, Jawa Barat (kode 32.71)  
**Snapshot sumber:** 19 September 2026  
**Tanggal dokumen:** 30 September 2026

## Ringkasan keputusan

Warehouse dirancang untuk menjawab desa dan waktu yang diprakirakan hujan di Kota Bogor.
Snapshot K1 mempunyai 1.156 baris untuk 68 desa dalam 6 kecamatan. Grain fact adalah satu desa
pada satu slot waktu prakiraan dalam satu snapshot analisis BMKG. Desain mempertahankan kedua
timestamp UTC dan WIB, tetapi seluruh analitik harian memakai WIB.

Keputusan utama:

1. `adm4`/kode desa adalah natural key wilayah; `weather` adalah natural key cuaca.
2. `weather_desc` ditolak sebagai key karena kode 0 dan 1 sama-sama berlabel "Cerah".
3. `time_index` diperlakukan sebagai horizon, bukan jam, karena 625 nilai awalnya di atas 23.
4. `vs` dan `vs_text` tidak dimuat karena 1.156 dari 1.156 baris kosong.
5. Fact dipartisi menurut `analysis_date` dan dimuat ulang dengan delete-and-insert per snapshot.

## 1. Star schema

```text
dim_date (date_sk) ----------------------+
dim_wilayah (wilayah_sk, SCD Type 2) ----+
dim_slot (slot_sk, Type 0) --------------+--> fact_prakiraan_cuaca
dim_cuaca (cuaca_sk, Type 1) ------------+
```

### Grain

Satu baris `fact_prakiraan_cuaca` adalah satu desa pada satu slot waktu prakiraan dalam satu
snapshot analisis BMKG. Unique key-nya `(wilayah_sk, forecast_local_ts, analysis_ts)`.

### Dimensi dan surrogate key

| Tabel | Surrogate key | Natural key | Tipe perubahan | Alasan |
|---|---|---|---|---|
| `dim_date` | `date_sk` | `full_date` | Type 0 | atribut kalender tetap |
| `dim_wilayah` | `wilayah_sk` | `wilayah_nk` (`adm4`) | Type 2 | perubahan nama/hierarki harus mempertahankan histori fakta |
| `dim_slot` | `slot_sk` | `jam_lokal` | Type 0 | klasifikasi jam lokal tetap |
| `dim_cuaca` | `cuaca_sk` | `weather_code` | Type 1 | koreksi label ditimpa; kode bisnis tidak berubah |

`dim_wilayah` menyimpan `valid_from`, `valid_to`, dan `is_current`. Semua dimensi menyediakan
anggota Unknown dengan surrogate key `-1` untuk lookup yang gagal.

### Measure dan aditivitas

| Measure | Aditivitas | Aturan agregasi |
|---|---|---|
| `temperature_c` | Non-additive | `AVG`, `MIN`, atau `MAX`; tidak di-`SUM` |
| `humidity_pct` | Non-additive | rata-rata/ekstrem, bukan penjumlahan |
| `precipitation_mm` | Semi-additive | dapat dijumlah lintas waktu untuk satu desa; tidak lintas desa |
| `cloud_cover_pct` | Non-additive | rata-rata/ekstrem, bukan penjumlahan |
| `wind_speed` | Non-additive | `AVG` atau `MAX` |
| `wind_direction_deg` | Non-additive | memerlukan agregasi arah sirkular |

DDL lengkap terdapat pada `sql/10_dim_date.sql`, tiga berkas `sql/20_dim_*.sql`, dan
`sql/30_fact_prakiraan_cuaca.sql`.

## 2. Desain load

Alur lengkap adalah sumber CSV -> staging bertipe -> empat dimensi -> fact. `stg_desa` dan
`stg_prakiraan_cuaca` memakai full replace. `dim_wilayah` memakai SCD Type 2 compare-current,
`dim_slot` insert-only dengan anti-join, `dim_cuaca` upsert Type 1, dan fact memakai
delete-and-insert per partisi `analysis_date`.

Natural key utama:

- staging/fact source: `adm4 + local_datetime + analysis_date`;
- wilayah: `wilayah_nk = adm4`;
- slot: `jam_lokal`;
- cuaca: `weather_code`.

Append polos pada fact akan menggandakan 1.156 baris ketika snapshot yang sama dimuat dua kali.
SCD wilayah juga dapat menggandakan versi current bila loader tidak mencocokkan natural key dan
hash atribut serta tidak menutup versi lama. Strategi dan urutan dependency lengkap terdapat pada
`pipeline/DESIGN_load.md`.

## 3. Enam test kualitas

| Test | Severity | Expected | Perkiraan pelanggaran | Keputusan desain |
|---|---|---|---:|---|
| duplikat grain desa-slot-snapshot | blocking | pass | 0 | menjaga grain fact |
| curah hujan negatif | blocking | pass | 0 | menjaga validitas measure |
| kode desa tidak ada di master | blocking | pass | 0 | menjamin lookup wilayah |
| visibilitas kosong | warning | fail | 1.156 | `vs` tidak dimuat |
| deskripsi cuaca bukan key unik | warning | fail | 1 | gunakan kode cuaca sebagai key |
| `time_index` bukan jam dinding | warning | fail | 625 | parse sebagai horizon |

Expected `fail` berarti test memang diharapkan menemukan masalah nyata pada snapshot, bukan bahwa
desain gagal. SQL dan justifikasi lengkap terdapat pada `tests/test_definitions.yml`.

## 4. Tiga kueri analitik

1. **Desa dengan slot hujan.** Menghasilkan 46 desa dengan total 53 slot hujan dari 1.156 slot.
2. **Peringkat kecamatan.** CTE dan `DENSE_RANK()` menempatkan Bogor Utara di peringkat pertama
   dengan rata-rata curah hujan sekitar 0,189 mm per slot.
3. **Perubahan suhu antar-slot.** `LAG()` menunjukkan kenaikan terbesar sebesar 6 °C pada beberapa
   desa Kota Bogor.

Seluruh kueri memfilter `kabkot = 'Kota Bogor'` dan snapshot terbaru. SQL lengkap berada pada
`sql/40_analytics/q01.sql` sampai `q03.sql`.

## 5. Kamus metrik

Metrik UTS adalah **Persentase Slot Hujan**: persentase baris fact pada cakupan terpilih yang
`dim_cuaca.is_hujan = TRUE`. Rumusnya:

```sql
100.0 * SUM(CASE WHEN c.is_hujan THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0)
```

Owner metrik adalah Kepala Pelaksana BPBD Kota Bogor, time basis-nya per hari kalender WIB, dan
default filter menggunakan Kota Bogor serta snapshot terbaru. Cara gaming utamanya adalah membuang
slot cerah dari denominator. Guard test mengharuskan denominator snapshot awal tetap 1.156 dan
pembilang tidak pernah melebihi denominator. Dua belas field lengkap terdapat pada
`docs/kamus_metrik.md` dan SQL kanonik pada `sql/50_metrics/persentase_slot_hujan.sql`.

## 6. Batas desain

Pertanyaan yang belum terjawab adalah: **seberapa akurat prakiraan hujan BMKG dibandingkan cuaca
yang benar-benar terjadi pada desa dan slot yang sama?** Dataset hanya berisi prakiraan, bukan
observasi aktual. Untuk menjawabnya dibutuhkan observasi hujan bertimestamp, pemetaan stasiun ke
desa, beberapa snapshot prakiraan, serta definisi toleransi dan ambang hujan. Rinciannya terdapat
pada `docs/batas_desain.md`.

## 7. D7 scope cut

Kelompok akan membangun satu fact (`fact_prakiraan_cuaca`), satu conformed dimension SCD Type 2
(`dim_wilayah`), tiga metrik, dan empat tile dashboard. Kelompok secara eksplisit mencabut ingest
real-time, evaluasi akurasi terhadap cuaca aktual, serta peta GIS poligon desa. Form siap dicoret
dan ditandatangani dosen pada `docs/D7_scope_cut.md`.

## Catatan defense

- **Grain:** jelaskan mengapa snapshot (`analysis_ts`) termasuk unique key; desa-slot yang sama
  dapat muncul lagi pada snapshot berikutnya.
- **SCD:** perubahan nama/hierarki wilayah membuat versi lama ditutup, bukan ditimpa.
- **Load:** delete-and-insert per snapshot membuat rerun idempoten; append polos menggandakan fact.
- **Test:** expected fail adalah bukti test menangkap kondisi sumber dan memengaruhi keputusan.
- **Alternatif ditolak:** deskripsi cuaca sebagai key, `time_index` sebagai jam, dan menganggap
  prakiraan sebagai observasi aktual.
