#starting python environment 

#
for bash
source ./.venv/script/active


python -m reflex db makemigrations --message "add file upload system"
python -m reflex db migrate

python -m reflex run

#supervisor credentials
#admin , admin123