VENV = venv
PROGRAM = Stockholm.py
DEPS = cryptography
PYTHON = $(venv)/bin/python
PIP = $(venv)/bin/pip

$(NAME) :  $(VENV)/bin/activate
	echo "Finishing to create the venv"
	$(PYTHON) $(PROGRAM)

$(VENV)/bin/activate:
	echo "Creating venv"
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install $(DEPS)

clean: 
	rm -rf $(VENV)