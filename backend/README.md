Three open terminals: Populate knowledge graph backend

#1
python3 -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
python3 example_usage.py //Only after #2 and #3 are running

#2
ollama serve

#3
ollama pull gemma2:2b
ollama run gemma2:2b

//

One open terminal: Search backend

#1
python3.12 -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
python3 api.py