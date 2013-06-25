#!/bin/sh

DOCDIR=doc/
APIDOCDIR=$DOCDIR/api
SRCDIR=libmushu/


rm -rf $APIDOCDIR
mkdir -p $APIDOCDIR
sphinx-apidoc -o $APIDOCDIR $SRCDIR
cd $DOCDIR
make html

