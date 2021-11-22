FROM python:2.7

WORKDIR ./application

COPY ./techtrends/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./techtrends ./

RUN python init_db.py

EXPOSE 3111

CMD [ "python", "app.py" ]
