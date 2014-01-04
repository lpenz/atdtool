
PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
MANDIR ?= $(PREFIX)/share/man

CFLAGS=-Wall -Werror


all: atdtool.1

.PHONY: all install clean

atdtool.1: manual.t2t
	txt2tags -t man -i $^ -o $@

README.textile: manual.t2t
	txt2tags -t html -H -i $^ -o $@
	sed -i -e 's@<B>@**@g' -e 's@</B>@**@g' $@

clean:
	rm -f atdtool.1

install: atdtool.1
	mkdir -p $(BINDIR)
	install atdtool $(BINDIR)/atdtool
	mkdir -p $(MANDIR)/man1
	install atdtool.1 $(MANDIR)/man1/atdtool.1

