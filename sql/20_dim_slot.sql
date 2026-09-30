-- ============================================================
-- 20_dim_slot.sql - dimensi slot waktu lokal WIB
-- SCD TYPE 0: jam dan label bagian hari adalah klasifikasi tetap; perubahan
-- aturan berarti versi desain baru, bukan overwrite data historis.
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_slot (
    slot_sk           INTEGER PRIMARY KEY,      -- surrogate key warehouse
    jam_lokal         TIME NOT NULL,            -- natural key
    jam_ke             SMALLINT NOT NULL,
    nama_slot          VARCHAR NOT NULL,
    bagian_hari        VARCHAR NOT NULL,
    zona_waktu         VARCHAR NOT NULL DEFAULT 'WIB',
    UNIQUE (jam_lokal),
    CHECK (jam_ke BETWEEN 0 AND 23)
);

INSERT INTO dim_slot
SELECT -1, TIME '00:00:00', -1, 'TIDAK DIKETAHUI', 'TIDAK DIKETAHUI', 'WIB'
WHERE NOT EXISTS (SELECT 1 FROM dim_slot WHERE slot_sk = -1);

-- Nilai time_index sumber (misalnya 11-12 atau 26-27) tidak menjadi natural
-- key karena itu horizon/offset prakiraan, bukan jam dinding.
