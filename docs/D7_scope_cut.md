# D7 - Batas lingkup capstone

> Diisi sebelum defense. Dosen dapat mencoret dan menandatangani pada akhir ronde.

**Tim:** Kelompok 1
**Topik / slice:** T3 Cuaca Ekstrem per Desa / K1 Kota Bogor (32.71)
**Tanggal:** 30 September 2026

## AKAN DIBANGUN

| # | Artefak | Ukuran selesai | Deadline |
|---|---|---|---|
| 1 | fact: `fact_prakiraan_cuaca` | Grain unik desa-slot-snapshot; 1.156 baris snapshot awal; seluruh FK terisi atau `-1`; load ulang tidak menggandakan baris. | Sebelum Sesi 15 |
| 2 | conformed dim: `dim_wilayah` | 68 desa Kota Bogor + anggota Unknown; natural key kode desa; SCD Type 2 menyimpan versi historis. | Sebelum Sesi 15 |
| 3 | metrik di kamus: 3 dari 3 | Persentase Slot Hujan, Suhu Rata-rata, dan Kecepatan Angin Maksimum memiliki 12 field, SQL, owner, serta guard test. | Sebelum Sesi 15 |
| 4 | dashboard: 4 tile | KPI persentase slot hujan, peringkat kecamatan, tren suhu per slot, dan tabel desa dengan slot hujan; seluruh tile memakai snapshot/filter yang sama. | Sebelum Sesi 15 |

## TIDAK LAGI DIBANGUN

| # | Yang dicabut | Alasan |
|---|---|---|
| 1 | Ingest BMKG real-time dan refresh otomatis | Scope data dibatasi ke snapshot dosen; koneksi live menambah risiko reproducibility dan melanggar larangan memakai dataset lain. |
| 2 | Evaluasi akurasi prakiraan terhadap cuaca aktual | Dataset tidak memiliki observasi aktual; hasil tidak dapat divalidasi tanpa sumber dan pemetaan tambahan. |
| 3 | Peta GIS interaktif per poligon desa | Dataset tidak memuat geometri/batas desa; empat tile nonspasial sudah cukup menjawab keputusan operasional yang disepakati. |

## Tanda tangan

| Tim | Dosen |
|---|---|
| Nama perwakilan: ____________________ | Nama: ____________________ |
| Tanda tangan: _______________________ | Tanda tangan: ____________ |
