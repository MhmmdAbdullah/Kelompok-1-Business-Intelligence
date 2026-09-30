-- ============================================================
-- 20_dim_cuaca.sql - kamus kondisi cuaca BMKG
-- SCD TYPE 1: koreksi label/terjemahan ditimpa; analisis historis tetap
-- menggunakan kode cuaca yang sama dan tidak memerlukan histori label.
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_cuaca (
    cuaca_sk           INTEGER PRIMARY KEY,      -- surrogate key warehouse
    weather_code       INTEGER NOT NULL,         -- natural key dari BMKG
    deskripsi_id       VARCHAR NOT NULL,
    deskripsi_en       VARCHAR,
    is_hujan           BOOLEAN NOT NULL,
    UNIQUE (weather_code)
);

INSERT INTO dim_cuaca
SELECT -1, -1, 'TIDAK DIKETAHUI', 'UNKNOWN', FALSE
WHERE NOT EXISTS (SELECT 1 FROM dim_cuaca WHERE cuaca_sk = -1);

-- weather_desc tidak boleh menjadi natural key: pada profil K1, kode 0 dan 1
-- sama-sama berdeskripsi "Cerah". is_hujan = weather_code BETWEEN 60 AND 99.
