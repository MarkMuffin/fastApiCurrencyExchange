**To start up:**

1. Run docker container 
```shell
 docker compose up
```
2. Install dependencies
```shell
pip instal -r requirements.txt
```
3. Run Application. It will automaticly create table
```shell
uvicorn app.main:app --reload 
```
4. Populate Database with data (if needed)
```shell
python app/populate_initial_data_from_file.py
```
5. Use [swagger](http://127.0.0.1:8000/docs)
