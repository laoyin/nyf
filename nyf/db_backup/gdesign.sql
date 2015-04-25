BEGIN;
CREATE TABLE `gdesign_accidentstatistics` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `time` varchar(5) NOT NULL,
    `local` integer NOT NULL,
    `type` integer NOT NULL,
    `loss` integer NOT NULL
)
;
CREATE TABLE `gdesign_simulationdata` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `constant` integer NOT NULL,
    `windSpeed` varchar(5) NOT NULL,
    `dischargeSpeed` varchar(5) NOT NULL,
    `distance` varchar(5) NOT NULL,
    `leakage_concentration` varchar(5) NOT NULL,
    `leakage_speed` varchar(5) NOT NULL,
    `single_leakage_concentration` varchar(5) NOT NULL,
    `single_leakage_speed` varchar(5) NOT NULL
)
;

COMMIT;

