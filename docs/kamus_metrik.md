# D6 - Kamus metrik Kelompok 1

## Metrik 1 - Persentase Slot Hujan

| # | Field | Isi |
|---|---|---|
| 1 | Nama metrik | Persentase Slot Hujan |
| 2 | Definisi | Persentase slot prakiraan pada cakupan terpilih yang kode cuacanya menunjukkan hujan. |
| 3 | Rumus SQL | `100.0 * SUM(CASE WHEN c.is_hujan THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0)` |
| 4 | Grain | Hasil default satu tanggal kalender WIB per kecamatan; grain fact dasarnya satu desa per slot dalam satu snapshot. |
| 5 | Tabel sumber | `fact_prakiraan_cuaca`, `dim_cuaca`, `dim_date`, `dim_wilayah` |
| 6 | Owner | Kepala Pelaksana BPBD Kota Bogor |
| 7 | Time basis | Per hari kalender WIB, menggunakan snapshot dengan `analysis_ts` terbaru. |
| 8 | Satuan | Persen (%) dengan rentang 0-100. |
| 9 | Dimensi yang boleh dipotong | Tanggal, kecamatan, desa, dan slot waktu lokal. Tidak dipotong menurut kategori cuaca karena akan membuat metrik tautologis. |
| 10 | Filter default | `kabkot = 'Kota Bogor'`, snapshot terbaru, serta mengecualikan anggota wilayah/cuaca Unknown. |
| 11 | Arti nilai kosong | Tidak ada data pada kombinasi slice dan periode tersebut; bukan 0%. |
| 12 | Versi | v1, berlaku 30 September 2026. |

SQL kanonik ada di `sql/50_metrics/persentase_slot_hujan.sql`.

### Cara metrik ini di-gaming

Orang dapat membuang slot cerah dari penyebut atau hanya memilih jam/desa yang sedang hujan agar
persentase terlihat tinggi tanpa ada perubahan cuaca yang sebenarnya.

### Guard test

Untuk snapshot dan slice yang sama, pastikan penyebut metrik sama dengan jumlah seluruh baris fact
yang valid, pembilang tidak melebihi penyebut, dan tidak ada filter cuaca pada penyebut:

```sql
WITH kontrol AS (
    SELECT count(*) AS semua_slot,
           sum(CASE WHEN c.is_hujan THEN 1 ELSE 0 END) AS slot_hujan
    FROM fact_prakiraan_cuaca f
    JOIN dim_wilayah w USING (wilayah_sk)
    JOIN dim_cuaca c USING (cuaca_sk)
    WHERE w.kabkot = 'Kota Bogor'
      AND f.analysis_ts = (SELECT max(analysis_ts) FROM fact_prakiraan_cuaca)
      AND f.wilayah_sk <> -1 AND f.cuaca_sk <> -1
)
SELECT count(*)
FROM kontrol
WHERE slot_hujan > semua_slot OR semua_slot <> 1156;
```

Hasil yang benar untuk snapshot K1 adalah `0` pelanggaran; kontrol denominator-nya 1.156 slot.
