-- Q01 - Desa Kota Bogor yang memiliki slot hujan pada snapshot aktif.
-- Kolom keluaran: kecamatan, desa, slot_hujan, slot_total, persentase_slot_hujan.
-- Jawaban yang diharapkan: 46 dari 68 desa memiliki sedikitnya satu slot hujan,
-- dengan total 53 slot hujan dari 1.156 slot prakiraan.

SELECT w.kecamatan,
       w.desa,
       sum(CASE WHEN c.is_hujan THEN 1 ELSE 0 END) AS slot_hujan,
       count(*) AS slot_total,
       round(100.0 * sum(CASE WHEN c.is_hujan THEN 1 ELSE 0 END)
             / nullif(count(*), 0), 2) AS persentase_slot_hujan
FROM fact_prakiraan_cuaca f
JOIN dim_wilayah w USING (wilayah_sk)
JOIN dim_cuaca c USING (cuaca_sk)
WHERE w.kabkot = 'Kota Bogor'                   -- slice Kelompok 1
  AND f.analysis_ts = (SELECT max(analysis_ts) FROM fact_prakiraan_cuaca)
GROUP BY w.kecamatan, w.desa
HAVING sum(CASE WHEN c.is_hujan THEN 1 ELSE 0 END) > 0
ORDER BY slot_hujan DESC, w.kecamatan, w.desa;
