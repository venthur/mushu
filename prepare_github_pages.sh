#!/bin/sh

GH_PAGES=gh_pages


rm -rf $GH_PAGES
git clone . $GH_PAGES
cd $GH_PAGES
git checkout gh-pages
cp -r ../doc/_build/html/* .

