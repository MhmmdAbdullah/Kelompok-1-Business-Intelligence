-- Q02 - Peringkat kecamatan berdasarkan rata-rata curah hujan.
-- Kolom keluaran: kecamatan, rata_rata_curah_hujan_mm, peringkat.
-- Jawaban yang diharapkan: Bogor Utara berada di peringkat pertama dengan
-- rata-rata curah hujan sekitar 0,189 mm per slot pada snapshot K1.

WITH curah_hujan_kecamatan AS (
    SELECT w.kecamatan,
           avg(f.precipitation_mm) AS rata_rata_curah_hujan_mm
    FROM fact_prakiraan_cuaca f
    JOIN dim_wilayah w USING (wilayah_sk)
    WHERE w.kabkot = 'Kota Bogor'               -- slice Kelompok 1
      AND f.analysis_ts = (SELECT max(analysis_ts) FROM fact_prakiraan_cuaca)
    GROUP BY w.kecamatan
)
SELECT kecamatan,
       round(rata_rata_curah_hujan_mm, 3) AS rata_rata_curah_hujan_mm,
       dense_rank() OVER (
           ORDER BY rata_rata_curah_hujan_mm DESC
       ) AS peringkat
FROM curah_hujan_kecamatan
ORDER BY peringkat, kecamatan;
