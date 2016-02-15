GHOME=/home/glamfame/glamfame
GENV=/home/ENV/glamfame/bin/activate

#source $GENV && killall gunicorn;
cd $GHOME && git reset --hard;
cd $GHOME && git pull;
find -type d -name migration -exec rm -rf {} $GHOME;
cd $GHOME && git pull;
source $GENV && cd $GHOME && python manage.py reset_db;
source $GENV && cd $GHOME && python manage.py syncdb;
source $GENV && cd $GHOME && python manage.py rebuild_index --noinput;
source $GENV && cd $GHOME && python manage.py collectstatic;
source $GENV && cd $GHOME && python manage.py python manage.py loaddata dumpdata.json;
source $GENV && cd $GHOME && python manage.py python manage.py migrate django_cron;