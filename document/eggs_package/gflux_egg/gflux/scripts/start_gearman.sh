nohup python manage.py gearman_worker_send_email >/dev/null 2>&1  &
nohup python manage.py gearman_worker_import_data >/dev/null 2>&1   &
nohup python manage.py gearman_worker_import_sp_excel_data >/dev/null 2>&1   &
nohup python manage.py gearman_worker_import_ycshell_excel_data >/dev/null 2>&1   &
nohup python manage.py gearman_worker_compute_station_daybatch >/dev/null 2>&1   &
nohup python manage.py gearman_worker_compute_fuel_daybatch >/dev/null 2>&1  &
