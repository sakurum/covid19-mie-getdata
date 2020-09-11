#!/bin/bash

git config --global user.name "sakurum"
git config --global user.email "sakuranomiyu@gmail.com"

git remote set-url origin https://github.com/sakurum/covid19-mie-getdata.git

git checkout master

date = $(date +%Y/%m/%d)
git commit -m "[updater] update data (${date})"
