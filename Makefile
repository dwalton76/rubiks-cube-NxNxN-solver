clean-gcc:
	rm -f ida_search_444_phase1 ida_search_444_phase2 ida_search_555_phase1 ida_search_555_phase2 ida_search_555_phase3 ida_search_555_phase4 ida_search_555_phase5 ida_search_555_phase6 ida_search_666_centers_stage ida_search_666_daisy_centers ida_search_777_centers_stage ida_search_777_daisy_centers ida_search_777_UD_centers_stage

clean: clean-gcc
	rm -rf build dist venv rubikscubennnsolver.egg-info cache
	find . -name __pycache__ | xargs rm -rf

gcc: clean-gcc
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
	@if [ ! -d ../rubiks-cube-lookup-tables ]; then \
		git clone https://github.com/dwalton76/rubiks-cube-lookup-tables.git ../rubiks-cube-lookup-tables; \
	fi
	@./venv/bin/python3 -m pip install -e ../rubiks-cube-lookup-tables --no-build-isolation

format:
	isort rubikscubennnsolver usr utils
	@./venv/bin/python3 -m black --config=pyproject.toml .
	@./venv/bin/python3 -m flake8 --config=.flake8

wheel:
	@./venv/bin/python3 setup.py bdist_wheel

test:
	./venv/bin/python3 -m pytest -vv tests

# Build every lookup table for one cube size into lookup-tables/. A solve of
# that size exits with instructions to run the matching target when a file is
# missing. Tables that are already present are left in place.
.PHONY: 333-tables 444-tables 555-tables 666-tables 777-tables
333-tables 444-tables 555-tables 666-tables 777-tables:
	@test -x ./venv/bin/python3 || { echo "Run make init first."; exit 1; }
	@mkdir -p lookup-tables
	@RUBIKS_LOOKUP_TABLE_DIR=$(abspath lookup-tables) ./venv/bin/python3 -m rubikscubelookuptables.localbuild $(subst -tables,,$@)
