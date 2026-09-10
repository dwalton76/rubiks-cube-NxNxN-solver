
clean:
	rm -rf build dist venv rubikscubennnsolver.egg-info cache ida_search ida_search_via_graph ida_search_666_centers_stage my-pt-states.txt
	find . -name __pycache__ | xargs rm -rf

init: clean
	gcc -O3 -o ida_search_via_graph rubikscubennnsolver/ida_search_core.c rubikscubennnsolver/rotate_xxx.c rubikscubennnsolver/ida_search_666.c rubikscubennnsolver/ida_search_777.c rubikscubennnsolver/ida_search_via_graph.c -lm
	gcc -O3 -o ida_search_666_centers_stage rubikscubennnsolver/ida_search_core.c rubikscubennnsolver/rotate_xxx.c rubikscubennnsolver/ida_search_666_centers_stage.c -lm -lpthread
	python3 -m venv venv
	@./venv/bin/python3 -m pip install -U pip==26.2.1
	@./venv/bin/python3 -m pip install -r requirements.dev.txt
	@./venv/bin/python3 -m pip install -e . --no-build-isolation

format:
	isort rubikscubennnsolver usr utils
	@./venv/bin/python3 -m black --config=pyproject.toml .
	@./venv/bin/python3 -m flake8 --config=.flake8

wheel:
	@./venv/bin/python3 setup.py bdist_wheel

test:
	./venv/bin/python3 -m pytest -vv tests
