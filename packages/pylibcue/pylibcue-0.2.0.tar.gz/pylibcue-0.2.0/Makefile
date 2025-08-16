CC = gcc
LEX = flex
YACC = bison
PYTHON = python3
LIBCUE = vendor/libcue

default: wheel

$(LIBCUE)/cue_scanner.c:
	$(LEX) -o $@ $(LIBCUE)/cue_scanner.l

$(LIBCUE)/cue_parser.c $(LIBCUE)/cue_parser.h:
	$(YACC) -l -d -o $(firstword $@) $(LIBCUE)/cue_parser.y

parser: $(LIBCUE)/cue_scanner.c $(LIBCUE)/cue_parser.c $(LIBCUE)/cue_parser.h

ext: parser
	CC=$(CC) $(PYTHON) setup.py build_ext --inplace

test: ext
	$(PYTHON) -m unittest discover -v -s tests

sdist: parser
	$(PYTHON) -m build --sdist

wheel: parser
	CC=$(CC) $(PYTHON) -m build --wheel

clean:
	rm -f pylibcue/*.so pylibcue/*.c
	rm -f $(LIBCUE)/cue_scanner.c $(LIBCUE)/cue_parser.c $(LIBCUE)/cue_parser.h
	rm -f dist/* wheelhouse/*
	rm -rf build/* *.egg-info
