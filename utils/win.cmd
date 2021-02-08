: ======= Setup your home path and virtual env ======= :
: variable info.
: H	- home dir.
: W - working dir.
: V	- virtual env. path
: ========================================= : 

: TO-DO list 
: 1. automation activate virtual env


@echo off
set "H=C:\Users\jellato\"
set "W=C:\Users\jellato\AppData\Local\Packages\CanonicalGroupLimited.Ubuntu18.04onWindows_79rhkp1fndgsc\LocalState\rootfs\home\coolseaweed\PRJ\stone82"
set "V=C:\venv\py38_32\Scripts"

echo ----------- win.cmd info. -----------
echo 32bit python virtual env path: [%V%]
echo home path: [%H%]
echo workspace path: [%W%]
echo ---------------------------------------
cd %V%









