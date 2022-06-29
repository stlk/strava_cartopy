FROM condaforge/miniforge3

RUN conda install cartopy

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

RUN pip install python-dotenv["cli"]