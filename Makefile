clean-gcc:
	rm -f ida_search_via_graph ida_search_444_phase1 ida_search_444_phase2 ida_search_555_phase1 ida_search_555_phase2 ida_search_555_phase3 ida_search_555_phase4 ida_search_555_phase5 ida_search_555_phase6 ida_search_666_centers_stage ida_search_666_daisy_centers ida_search_777_centers_stage ida_search_777_daisy_centers ida_search_777_UD_centers_stage my-pt-states.txt

clean: clean-gcc
	rm -rf build dist venv rubikscubennnsolver.egg-info cache
	find . -name __pycache__ | xargs rm -rf

gcc: clean-gcc
	gcc -O3 -o ida_search_via_graph rubikscubennnsolver/ida_search_core.c rubikscubennnsolver/rotate_xxx.c rubikscubennnsolver/ida_search_via_graph.c -lm
	gcc -O3 -o ida_search_444_phase1 rubikscubennnsolver/ida_search_core.c rubikscubennnsolver/rotate_xxx.c rubikscubennnsolver/ida_search_444_phase1.c -lm -lpthread
	gcc -O3 -o ida_search_444_phase2 rubikscubennnsolver/ida_search_core.c rubikscubennnsolver/rotate_xxx.c rubikscubennnsolver/ida_search_444_phase2.c -lm -lpthread
	gcc -O3 -Wall -Wextra -o ida_search_555_phase1 rubikscubennnsolver/ida_search_core.c rubikscubennnsolver/rotate_xxx.c rubikscubennnsolver/ida_search_555_phase1.c -lm
	gcc -O3 -Wall -Wextra -o ida_search_555_phase2 rubikscubennnsolver/ida_search_core.c rubikscubennnsolver/rotate_xxx.c rubikscubennnsolver/ida_search_555_phase2.c -lm
	gcc -O3 -Wall -Wextra -o ida_search_555_phase3 rubikscubennnsolver/ida_search_core.c rubikscubennnsolver/rotate_xxx.c rubikscubennnsolver/ida_search_555_phase3.c -lm
	gcc -O3 -Wall -Wextra -o ida_search_555_phase4 rubikscubennnsolver/ida_search_core.c rubikscubennnsolver/rotate_xxx.c rubikscubennnsolver/ida_search_555_phase4.c -lm
	gcc -O3 -Wall -Wextra -o ida_search_555_phase5 rubikscubennnsolver/ida_search_core.c rubikscubennnsolver/rotate_xxx.c rubikscubennnsolver/ida_search_555_phase5.c -lm
	gcc -O3 -Wall -Wextra -o ida_search_555_phase6 rubikscubennnsolver/ida_search_core.c rubikscubennnsolver/rotate_xxx.c rubikscubennnsolver/ida_search_555_phase6.c -lm
	gcc -O3 -o ida_search_666_centers_stage rubikscubennnsolver/ida_search_core.c rubikscubennnsolver/rotate_xxx.c rubikscubennnsolver/ida_search_666_centers_stage.c -lm -lpthread
	gcc -O3 -o ida_search_666_daisy_centers rubikscubennnsolver/ida_search_core.c rubikscubennnsolver/rotate_xxx.c rubikscubennnsolver/ida_search_666_daisy_centers.c -lm -lpthread
	gcc -O3 -o ida_search_777_centers_stage rubikscubennnsolver/ida_search_core.c rubikscubennnsolver/rotate_xxx.c rubikscubennnsolver/ida_search_777_centers_stage.c -lm -lpthread
	gcc -O3 -o ida_search_777_daisy_centers rubikscubennnsolver/ida_search_core.c rubikscubennnsolver/rotate_xxx.c rubikscubennnsolver/ida_search_777_daisy_centers.c -lm -lpthread
	gcc -O3 -o ida_search_777_UD_centers_stage rubikscubennnsolver/ida_search_core.c rubikscubennnsolver/rotate_xxx.c rubikscubennnsolver/ida_search_777_UD_centers_stage.c -lm -lpthread

init: clean gcc
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
