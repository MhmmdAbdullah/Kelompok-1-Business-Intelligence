# Profil sumber — T3 Cuaca Ekstrem per Desa (BMKG) / k1

## prakiraan_cuaca

`SELECT count(*) AS baris, count(DISTINCT adm4) AS desa FROM read_csv_auto('{D}/prakiraan_cuaca.csv', all_varchar=true)`

| baris | desa |
|---|---|
| 1156 | 68 |

## prakiraan_cuaca

`SELECT count(*) FILTER (WHERE vs IS NULL OR vs = '') AS vs_kosong FROM read_csv_auto('{D}/prakiraan_cuaca.csv', all_varchar=true)`

| vs_kosong |
|---|
| 1156 |

## prakiraan_cuaca

`SELECT count(*) FILTER (WHERE TRY_CAST(tp AS DOUBLE) = 0) AS tp_nol, count(*) AS baris FROM read_csv_auto('{D}/prakiraan_cuaca.csv', all_varchar=true)`

| tp_nol | baris |
|---|---|
| 812 | 1156 |

## prakiraan_cuaca

`SELECT weather AS kode, weather_desc AS deskripsi, count(*) AS baris FROM read_csv_auto('{D}/prakiraan_cuaca.csv', all_varchar=true) GROUP BY 1,2 ORDER BY 3 DESC`

| kode | deskripsi | baris |
|---|---|---|
| 1 | Cerah | 966 |
| 0 | Cerah | 70 |
| 2 | Cerah Berawan | 57 |
| 61 | Hujan Ringan | 53 |
| 3 | Berawan | 10 |

## prakiraan_cuaca

`SELECT min(TRY_CAST(time_index AS VARCHAR)) AS time_index_contoh, count(DISTINCT analysis_date) AS analysis_date_unik FROM read_csv_auto('{D}/prakiraan_cuaca.csv', all_varchar=true)`

| time_index_contoh | analysis_date_unik |
|---|---|
| 11-12 | 1 |

## prakiraan_cuaca

`SELECT count(*) FILTER (WHERE epoch(strptime(local_datetime, '%Y-%m-%d %H:%M:%S')) - epoch(strptime(utc_datetime, '%Y-%m-%d %H:%M:%S')) = 25200) AS baris_selisih_7jam, count(*) AS baris FROM read_csv_auto('{D}/prakiraan_cuaca.csv', all_varchar=true)`

| baris_selisih_7jam | baris |
|---|---|
| 1156 | 1156 |

## desa

`SELECT count(*) AS desa, count(DISTINCT kecamatan) AS kecamatan FROM read_csv_auto('{D}/desa.csv', all_varchar=true)`

| desa | kecamatan |
|---|---|
| 68 | 6 |

## Profil tambahan untuk enam test UTS

Profil berikut dijalankan read-only terhadap CSV K1 agar seluruh `perkiraan_baris` dapat ditelusuri.

| Pemeriksaan | Ringkasan SQL | Hasil |
|---|---|---:|
| Duplikat grain | kelompok `adm4, local_datetime, analysis_date` dengan `count(*) > 1` | 0 |
| Curah hujan negatif | `TRY_CAST(tp AS DOUBLE) < 0` | 0 |
| Kode desa orphan | `adm4` yang tidak ditemukan pada `desa.kode` | 0 |
| Visibilitas kosong | `vs IS NULL OR vs = ''` | 1.156 |
| Deskripsi dipakai banyak kode | `weather_desc` dengan lebih dari satu `weather` | 1 |
| `time_index` awal di atas 23 | `split_part(time_index, '-', 1) > 23` | 625 |

## Profil untuk jawaban analitik

| Fakta profil | Hasil |
|---|---:|
| Tanggal lokal unik | 3 |
| Jam lokal unik | 16 |
| Desa dengan sedikitnya satu kode hujan 60-99 | 46 |
| Slot berkode hujan 60-99 | 53 dari 1.156 |
| Kecamatan dengan rata-rata `tp` tertinggi | Bogor Utara (0,189 mm/slot) |
| Kenaikan suhu terbesar antar-slot berurutan | 6 °C |
