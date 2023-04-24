praktikum_new_diplom

sudo docker-compose exec backend python manage.py migrate
sudo docker-compose exec backend python manage.py createsuperuser
sudo docker-compose exec backend python manage.py collectstatic --no-input

sudo docker-compose exec backend python manage.py ingredients_load /app/ingredients.csv
