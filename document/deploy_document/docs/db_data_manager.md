1.mysql 任务调度开关

    show processlist;
    set global event_scheduler=ON;
    set global event_scheduler=OFF;

2.mysql 编写任务
    -- 打开任务调度开关

    set global event_scheduler=ON;

    -- 切换到tml数据库

    use xinhua_tml;

    -- 创建任务运行日志表格

    CREATE TABLE IF NOT EXISTS event_schedule_log (
        id INT PRIMARY KEY AUTO_INCREMENT,
        message VARCHAR(255) NOT NULL,
        created_at DATETIME NOT NULL
    );

    -- 创建event

    drop event if exists drop_expired_data;
    delimiter |
    create event if not exists drop_expired_data
    on SCHEDULE EVERY 3 DAY
    STARTS CURRENT_TIMESTAMP
    ENDS CURRENT_TIMESTAMP + INTERVAL 7 YEAR
    ON COMPLETION PRESERVE
    DO
    BEGIN
        INSERT INTO event_schedule_log(message,created_at)
        VALUES('task start...',NOW());
        delete from tml_document where
        crawldatestring<DATE_SUB(now(),INTERVAL 6 MONTH);
        INSERT INTO event_schedule_log(message,created_at)
        VALUES('task end...',NOW());
    END |
    delimiter ;

    -- 切换到intelligence数据库

    use xinhua_intelligence;

    -- 创建event

    CREATE TABLE IF NOT EXISTS event_schedule_log_news (
        id INT PRIMARY KEY AUTO_INCREMENT,
        message VARCHAR(255) NOT NULL,
        created_at DATETIME NOT NULL
    );

    drop event if exists drop_expired_data_news;
    delimiter |
    create event if not exists drop_expired_data_news
    on SCHEDULE EVERY 3 DAY
    STARTS CURRENT_TIMESTAMP
    ENDS CURRENT_TIMESTAMP + INTERVAL 7 YEAR
    ON COMPLETION PRESERVE
    DO
    BEGIN
        INSERT INTO event_schedule_log_news(message,created_at)
        VALUES('task start...',NOW());
        delete from intelligence_news where
        crawltime<UNIX_TIMESTAMP(DATE_SUB(now(),INTERVAL 6 MONTH));
        INSERT INTO event_schedule_log_news(message,created_at)
        VALUES('task end...',NOW());
    END |
    delimiter ;

3.mysql 查看系统中存在的任务

    show events from tml;

4.mysql 删除任务

    drop event if exists drop_expired_data;

5.postgresql function

    -- used on trigger
    DROP FUNCTION fact_trans_auto_update();
    create or replace function fact_trans_auto_update()
    returns trigger as
    $$
    declare
    begin
        delete from fact_trans where site=NEW.name and timestamp<(NEW.latest_date-interval '13' month);
        RETURN NEW;
    end;
    $$ language plpgsql;

    -- used on manually
    DROP FUNCTION fact_trans_update(text,date);
    create or replace function fact_trans_update(site text,latest_date date)
    returns void as
    $$
    declare
    begin
        delete from fact_trans where site=site and timestamp<(latest_date-interval '13' month);
    end;
    $$ language plpgsql;

6.postgresql trigger function

    drop trigger if exists drop_expired_data on station;
    create trigger drop_expired_data
    after update of latest_date on station
    FOR EACH ROW
    WHEN (OLD.latest_date IS DISTINCT FROM NEW.latest_date)
    EXECUTE PROCEDURE fact_trans_auto_update();

7.postgreal show function and trigger

    \df
    \d station

9.mongodb ttl

    import pymongo
    import datetime

    mongo_con = pymongo.Connection('localhost', 27017)
    mongo_db = mongo_con.Mongo_database
    mongo_col = mongo_db.my_TTL_collection

    timestamp = datetime.datetime.now()
    utc_timestamp = datetime.datetime.utcnow()

    mongo_col.ensure_index("date", expireAfterSeconds=3*60)

    mongo_col.insert({'_id': 'session', "date": timestamp, "session": "test session"})
    mongo_col.insert({'_id': 'utc_session', "date": utc_timestamp, "session": "test session"})
    # the utc_session will be deleted after around 3 minutes,
    # the other depending on your timezone

10.solrcloud ttl
solrconfig.xml

    <updateRequestProcessorChain default="true">
    <processor class="solr.processor.DocExpirationUpdateProcessorFactory">
        <!-- EVERY 5 MINUTES START CHECK -->
        <int name="autoDeletePeriodSeconds">300</int>
        <!-- USE DEFAULT TTL -->
        <str name="ttlFieldName"/>
        <!-- DISABLE UPDATE ACTION -->
        <null name="ttlParamName"/>
        <str name="expirationFieldName">_expire_at_</str>
     </processor>
     </updateRequestProcessorChain>

    request need set default ttl paramerter:_ttl_=+6MONTH
