-- ============================================================
-- 20_dim_wilayah.sql - dimensi conformed wilayah Kelompok 1
-- SCD TYPE 2: nama atau hierarki wilayah dapat berubah; fakta lama harus
-- tetap menunjuk versi wilayah yang berlaku saat snapshot dibuat.
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_wilayah (
    wilayah_sk       BIGINT PRIMARY KEY,       -- surrogate key warehouse
    wilayah_nk       VARCHAR NOT NULL,          -- natural key: kode desa BPS/adm4
    desa              VARCHAR NOT NULL,
    kecamatan_nk      VARCHAR,
    kecamatan         VARCHAR,
    kabkot_nk         VARCHAR,
    kabkot            VARCHAR,
    provinsi_nk       VARCHAR,
    provinsi          VARCHAR,
    valid_from        DATE NOT NULL,
    valid_to          DATE NOT NULL,
    is_current        BOOLEAN NOT NULL,
    UNIQUE (wilayah_nk, valid_from),
    CHECK (valid_to >= valid_from)
);

-- Anggota Unknown menampung fakta yang kode wilayahnya tidak ditemukan.
INSERT INTO dim_wilayah
SELECT -1, 'UNKNOWN', 'TIDAK DIKETAHUI', NULL, 'TIDAK DIKETAHUI',
       NULL, 'TIDAK DIKETAHUI', NULL, 'TIDAK DIKETAHUI',
       DATE '1900-01-01', DATE '9999-12-31', TRUE
WHERE NOT EXISTS (SELECT 1 FROM dim_wilayah WHERE wilayah_sk = -1);

-- Desain pemberian key untuk versi baru:
-- max(wilayah_sk) + row_number() OVER (ORDER BY wilayah_nk).
-- Logika close-current lalu insert-new-version dijelaskan di DESIGN_load.md.
