BEGIN;
CREATE TABLE `gcustomer_wheeluser` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(255) NOT NULL UNIQUE,
    `sha1` varchar(40) NOT NULL,
    `password` varchar(255) NOT NULL,
    `time` datetime NOT NULL,
    `user_type` integer NOT NULL,
    `career` varchar(128) NOT NULL,
    `avarta_sha1` varchar(40) NOT NULL,
    `nick` varchar(128) NOT NULL,
    `score` integer NOT NULL,
    `payment_info` longtext NOT NULL
)
;
CREATE TABLE `gcustomer_wheeldevice` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `imei_code` varchar(128) NOT NULL UNIQUE,
    `mac_address` varchar(255) NOT NULL,
    `sim_number` varchar(32) NOT NULL,
    `device_type` varchar(128) NOT NULL UNIQUE,
    `time` datetime NOT NULL
)
;
CREATE TABLE `gcustomer_wheeluserdevice` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `user_sha1` varchar(40) NOT NULL,
    `imei_code` varchar(128) NOT NULL,
    `time` datetime NOT NULL,
    UNIQUE (`user_sha1`, `imei_code`)
)
;
CREATE TABLE `gcustomer_wheeluserlocation` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `user_type` integer NOT NULL,
    `user_id` varchar(128) NOT NULL,
    `time` datetime NOT NULL,
    `geo_x` double precision NOT NULL,
    `geo_y` double precision NOT NULL
)
;
CREATE TABLE `gcustomer_wheelmessage` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `sha1` varchar(40) NOT NULL UNIQUE,
    `title` varchar(128) NOT NULL,
    `body` varchar(512) NOT NULL,
    `author_sha1` varchar(40) NOT NULL,
    `message_type` integer NOT NULL,
    `time` datetime NOT NULL,
    `geo_x` double precision NOT NULL,
    `geo_y` double precision NOT NULL,
    `attachment_info` varchar(512) NOT NULL,
    `parent_sha1` varchar(40) NOT NULL,
    `root_sha1` varchar(40) NOT NULL
)
;
CREATE TABLE `gcustomer_wheelfileimage` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `sha1` varchar(40) NOT NULL UNIQUE,
    `file_type` integer NOT NULL,
    `file_name` varchar(256) NOT NULL,
    `file_suffix` varchar(32) NOT NULL,
    `content_digest` varchar(40) NOT NULL,
    `file_size` integer NOT NULL,
    `base64_content` longtext NOT NULL,
    `time` datetime NOT NULL,
    `author_sha1` varchar(40) NOT NULL
)
;
CREATE TABLE `gcustomer_wheelmessagemembership` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `message_sha1` varchar(40) NOT NULL,
    `user_sha1` varchar(40) NOT NULL,
    `delivery_type` integer NOT NULL,
    `time` datetime NOT NULL,
    UNIQUE (`message_sha1`, `user_sha1`)
)
;
CREATE TABLE `gcustomer_wheelmessagestat` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `message_sha1` varchar(40) NOT NULL UNIQUE,
    `nb_deliveries` integer NOT NULL,
    `nb_reads` integer NOT NULL,
    `nb_replies` integer NOT NULL,
    `nb_spreads` integer NOT NULL,
    `nb_ignores` integer NOT NULL,
    `recent_click_trend` longtext NOT NULL,
    `recent_spread_trend` longtext NOT NULL,
    `recent_reply_trend` longtext NOT NULL
)
;
CREATE TABLE `gcustomer_wheelsaleitem` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `sha1` varchar(40) NOT NULL UNIQUE,
    `name` varchar(256) NOT NULL,
    `price` double precision NOT NULL,
    `discount` varchar(256) NOT NULL,
    `discount_end_time` datetime NOT NULL,
    `available_source` longtext NOT NULL
)
;
CREATE TABLE `gcustomer_wheelsaleitemusage` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `item_sha1` varchar(40) NOT NULL,
    `item_type` integer NOT NULL,
    `user_sha1` varchar(40) NOT NULL,
    `nb_purchases` integer NOT NULL,
    `purchased_amount` double precision NOT NULL,
    `pickup_setting` integer NOT NULL,
    UNIQUE (`user_sha1`, `item_type`, `item_sha1`)
)
;
CREATE TABLE `gcustomer_wheelsaleservice` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `sha1` varchar(40) NOT NULL UNIQUE,
    `seller_name` varchar(256) NOT NULL,
    `service_name` varchar(256) NOT NULL,
    `average_score` double precision NOT NULL,
    `discount_score` double precision NOT NULL,
    `discount_end_time` datetime NOT NULL,
    `price` double precision NOT NULL,
    `nb_comments` integer NOT NULL,
    `geo_x` double precision NOT NULL,
    `geo_y` double precision NOT NULL
)
;
CREATE TABLE `gcustomer_wheelpurchasecomment` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `item_sha1` varchar(40) NOT NULL,
    `item_type` integer NOT NULL,
    `user_sha1` varchar(40) NOT NULL,
    `transaction_sha1` varchar(40) NOT NULL,
    `user_score` double precision NOT NULL,
    `comment_content` longtext NOT NULL,
    `time` datetime NOT NULL,
    UNIQUE (`item_sha1`, `item_type`, `user_sha1`)
)
;
CREATE TABLE `gcustomer_wheeltransaction` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `sha1` varchar(40) NOT NULL UNIQUE,
    `user_sha1` varchar(40) NOT NULL,
    `item_sha1` varchar(40) NOT NULL,
    `item_type` integer NOT NULL,
    `item_total` double precision NOT NULL,
    `time` datetime NOT NULL
)
;
CREATE TABLE `gcustomer_wheelappusage` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `user_type` integer NOT NULL,
    `user_id` varchar(256) NOT NULL,
    `time` datetime NOT NULL,
    `data_type` integer NOT NULL,
    `object_type` integer NOT NULL,
    `object_sha1` varchar(40) NOT NULL,
    UNIQUE (`user_type`, `user_id`, `time`)
)
;
CREATE INDEX `gcustomer_wheeluser_4da47e07` ON `gcustomer_wheeluser` (`name`);
CREATE INDEX `gcustomer_wheeldevice_dc843bf9` ON `gcustomer_wheeldevice` (`imei_code`);
CREATE INDEX `gcustomer_wheeluserdevice_7a9f45d0` ON `gcustomer_wheeluserdevice` (`user_sha1`);
CREATE INDEX `gcustomer_wheeluserdevice_dc843bf9` ON `gcustomer_wheeluserdevice` (`imei_code`);

COMMIT;

