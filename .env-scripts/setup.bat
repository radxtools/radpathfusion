python -m venv .env
python -m pip install --upgrade pip
pip install --upgrade setuptools wheel
pip install -r dev_requirements.txt
pip install ipywidgets
jupyter nbextension enable --py widgetsnbextension
pip install ipyevents
jupyter nbextension enable --py --sys-prefix ipyevents
pip install "holoviews[recommended]"