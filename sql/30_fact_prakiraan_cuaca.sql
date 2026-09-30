-- ============================================================
-- 30_fact_prakiraan_cuaca.sql - fact prakiraan cuaca Kelompok 1
-- GRAIN: satu baris = satu desa pada satu slot waktu prakiraan dalam satu
-- snapshot analisis BMKG.
-- ============================================================

CREATE TABLE IF NOT EXISTS fact_prakiraan_cuaca (
    date_sk              INTEGER NOT NULL,       -- FK dim_date, tanggal lokal WIB
    wilayah_sk           BIGINT NOT NULL,        -- FK dim_wilayah versi yang berlaku
    slot_sk              INTEGER NOT NULL,       -- FK dim_slot
    cuaca_sk             INTEGER NOT NULL,       -- FK dim_cuaca

    analysis_ts          TIMESTAMP NOT NULL,     -- degenerate snapshot identifier
    forecast_local_ts    TIMESTAMP NOT NULL,     -- degenerate event timestamp WIB
    forecast_utc_ts      TIMESTAMP NOT NULL,
    horizon_start_hour   SMALLINT,
    horizon_end_hour     SMALLINT,

    temperature_c        DECIMAL(5,2),           -- NON-ADDITIVE: gunakan AVG/MIN/MAX
    humidity_pct         DECIMAL(5,2),           -- NON-ADDITIVE: persentase tidak dijumlah
    precipitation_mm     DECIMAL(8,2),           -- SEMI-ADDITIVE: SUM lintas waktu untuk
                                                 -- satu desa; jangan SUM lintas desa
    cloud_cover_pct      DECIMAL(5,2),           -- NON-ADDITIVE: persentase tidak dijumlah
    wind_speed           DECIMAL(8,2),           -- NON-ADDITIVE: gunakan AVG/MAX
    wind_direction_deg   DECIMAL(6,2),           -- NON-ADDITIVE: arah bersifat sirkular

    PRIMARY KEY (wilayah_sk, forecast_local_ts, analysis_ts),
    CHECK (humidity_pct BETWEEN 0 AND 100 OR humidity_pct IS NULL),
    CHECK (cloud_cover_pct BETWEEN 0 AND 100 OR cloud_cover_pct IS NULL),
    CHECK (precipitation_mm >= 0 OR precipitation_mm IS NULL)
);

-- Relasi star saat memuat fact (satu JOIN langsung per dimensi):
-- stg_prakiraan_cuaca s
-- JOIN dim_date d ON d.full_date = CAST(s.local_datetime AS DATE)
-- JOIN dim_wilayah w ON w.wilayah_nk = s.adm4
--   AND CAST(s.analysis_date AS DATE) >= w.valid_from
--   AND CAST(s.analysis_date AS DATE) <  w.valid_to
-- JOIN dim_slot sl ON sl.jam_lokal = CAST(s.local_datetime AS TIME)
-- JOIN dim_cuaca c ON c.weather_code = TRY_CAST(s.weather AS INTEGER)
-- Setiap lookup yang gagal memakai surrogate key -1, bukan membuang fakta.
