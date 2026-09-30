-- Metrik: persentase slot hujan pada snapshot prakiraan aktif.
-- Grain keluaran: satu tanggal lokal x satu kecamatan Kota Bogor.
-- Rumus harus sama dengan docs/kamus_metrik.md.

SELECT d.full_date AS tanggal,
       w.kecamatan,
       round(
           100.0 * sum(CASE WHEN c.is_hujan THEN 1 ELSE 0 END)
           / nullif(count(*), 0),
           2
       ) AS persentase_slot_hujan
FROM fact_prakiraan_cuaca f
JOIN dim_date d USING (date_sk)
JOIN dim_wilayah w USING (wilayah_sk)
JOIN dim_cuaca c USING (cuaca_sk)
WHERE w.kabkot = 'Kota Bogor'
  AND f.analysis_ts = (SELECT max(analysis_ts) FROM fact_prakiraan_cuaca)
  AND f.wilayah_sk <> -1
  AND f.cuaca_sk <> -1
GROUP BY d.full_date, w.kecamatan
ORDER BY d.full_date, w.kecamatan;
