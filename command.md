to test whisper :

.\.venv\Scripts\Activate.ps1  
python test_whisper.py

to run all the project :

$env:PYTHONPATH = "src;C:\sblibs"
$env:SMARTBOARD_DEV_INPUT = "1"
py -3.11 -m smartboard.app.main