
all:
	sudo python3 setup.py install
	gcc -O3 -o ida_search ida_search_core.c ida_search.c rotate_xxx.c ida_search_444.c ida_search_555.c ida_search_666.c ida_search_777.c xxhash.c -lm

ida:
	gcc -O3 -ggdb -o ida_search ida_search_core.c ida_search.c rotate_xxx.c ida_search_444.c ida_search_555.c ida_search_666.c ida_search_777.c xxhash.c -lm

clean:
	sudo rm -rf build dist rubikscubennnsolver.egg-info ida_search
