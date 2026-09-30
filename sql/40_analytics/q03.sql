-- Q03 - Perubahan suhu terbesar antar-slot berurutan untuk setiap desa.
-- Kolom keluaran: kecamatan, desa, waktu, suhu, suhu_sebelumnya, perubahan_suhu_c.
-- Jawaban yang diharapkan: kenaikan suhu antar-slot terbesar pada snapshot K1
-- adalah 6 derajat Celsius dan terjadi pada beberapa desa Kota Bogor.

WITH suhu_berurutan AS (
    SELECT w.kecamatan,
           w.desa,
           f.forecast_local_ts,
           f.temperature_c,
           lag(f.temperature_c) OVER (
               PARTITION BY f.wilayah_sk
               ORDER BY f.forecast_local_ts
           ) AS suhu_sebelumnya
    FROM fact_prakiraan_cuaca f
    JOIN dim_wilayah w USING (wilayah_sk)
    WHERE w.kabkot = 'Kota Bogor'               -- slice Kelompok 1
      AND f.analysis_ts = (SELECT max(analysis_ts) FROM fact_prakiraan_cuaca)
)
SELECT kecamatan,
       desa,
       forecast_local_ts,
       temperature_c,
       suhu_sebelumnya,
       temperature_c - suhu_sebelumnya AS perubahan_suhu_c
FROM suhu_berurutan
WHERE suhu_sebelumnya IS NOT NULL
ORDER BY perubahan_suhu_c DESC, desa, forecast_local_ts
LIMIT 10;
