import sqlite3
import typing as T

import omronconnect as OC


def open_db(path: str) -> sqlite3.Connection:
    db = sqlite3.connect(path)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS bp_measurements (
            timestamp_utc   INTEGER PRIMARY KEY,
            systolic        INTEGER NOT NULL,
            diastolic       INTEGER NOT NULL,
            pulse           INTEGER NOT NULL,
            irregular_hb    INTEGER NOT NULL,
            movement_detect INTEGER NOT NULL,
            cuff_wrap_detect INTEGER NOT NULL,
            timezone        TEXT NOT NULL,
            notes           TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS weight_measurements (
            timestamp_utc        INTEGER PRIMARY KEY,
            weight_kg            REAL NOT NULL,
            bmi                  REAL NOT NULL,
            body_fat_pct         REAL NOT NULL,
            resting_metabolism   REAL NOT NULL,
            skeletal_muscle_pct  REAL NOT NULL,
            visceral_fat_level   REAL NOT NULL,
            metabolic_age        INTEGER NOT NULL,
            timezone             TEXT NOT NULL,
            notes                TEXT NOT NULL
        );
    """)
    return db


def store_measurement(db: sqlite3.Connection, m: OC.MeasurementTypes) -> bool:
    if isinstance(m, OC.BPMeasurement):
        cur = db.execute(
            "INSERT OR IGNORE INTO bp_measurements VALUES (?,?,?,?,?,?,?,?,?)",
            (
                m.measurementDate,
                m.systolic,
                m.diastolic,
                m.pulse,
                int(m.irregularHB),
                int(m.movementDetect),
                int(m.cuffWrapDetect),
                str(m.timeZone),
                m.notes,
            ),
        )
    elif isinstance(m, OC.WeightMeasurement):
        cur = db.execute(
            "INSERT OR IGNORE INTO weight_measurements VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                m.measurementDate,
                m.weight,
                m.bmiValue,
                m.bodyFatPercentage,
                m.restingMetabolism,
                m.skeletalMusclePercentage,
                m.visceralFatLevel,
                m.metabolicAge,
                str(m.timeZone),
                m.notes,
            ),
        )
    else:
        return False
    return cur.rowcount > 0


def store_measurements(db: sqlite3.Connection, measurements: T.List[OC.MeasurementTypes]) -> T.Tuple[int, int]:
    added = sum(1 for m in measurements if store_measurement(db, m))
    db.commit()
    return added, len(measurements) - added
