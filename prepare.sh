source /virtualenv-1.9.1/glamazer/bin/activate && killall gunicorn;
cd /var/www/glamazer/ && git reset --hard;
cd /var/www/glamazer/ && git pull;
find -type d -name migration -exec rm -rf {} /var/www/glamazer/;
cd /var/www/glamazer/ && git pull;
source /virtualenv-1.9.1/glamazer/bin/activate && cd /var/www/glamazer/ && python manage.py reset_db;
source /virtualenv-1.9.1/glamazer/bin/activate && cd /var/www/glamazer/ && python manage.py syncdb;
source /virtualenv-1.9.1/glamazer/bin/activate && cd /var/www/glamazer/ && python manage.py rebuild_index --noinput;
source /virtualenv-1.9.1/glamazer/bin/activate && cd /var/www/glamazer/ && python manage.py collectstatic;
source /virtualenv-1.9.1/glamazer/bin/activate && cd /var/www/glamazer/ && python manage.py python manage.py loaddata dumpdata.json;
source /virtualenv-1.9.1/glamazer/bin/activate && cd /var/www/glamazer/ && python manage.py python manage.py migrate django_cron;