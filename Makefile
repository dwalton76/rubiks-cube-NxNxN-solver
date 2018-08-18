
all:
	sudo python3 setup.py install
	gcc -o ida_search ida_search_core.c ida_search.c rotate_xxx.c ida_search_555.c ida_search_666.c -lm

ida:
	gcc -ggdb -o ida_search ida_search_core.c ida_search.c rotate_xxx.c ida_search_555.c ida_search_666.c -lm

clean:
	sudo rm -rf build dist rubikscubennnsolver.egg-info