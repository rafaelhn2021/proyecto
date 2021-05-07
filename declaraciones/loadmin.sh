#!/bin/sh

case "1" in
  ${LOAD_INITIAL_DATA} )
  echo ${LOAD_INITIAL_DATA} &&
  yes | python manage.py makemigrations &&
  yes | python manage.py makemigrations --merge &&
  python manage.py migrate &&
  python manage.py collectstatic --no-input &&

  python manage.py loaddata CatCamposObligatorios;;
esac
echo $LOAD_INITIAL_DATA
