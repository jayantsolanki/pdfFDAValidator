@echo off
echo ========================================
echo Building PDF Batch Processor Executable
echo ========================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Installing/Updating PyInstaller...
python -m pip install --upgrade pyinstaller

echo.
echo Building executable...
pyinstaller --onefile --console --name pdfFDAValidator pdf_batch_processor.py

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Executable location: dist\pdfFDAValidator.exe
echo.
echo You can now run:
echo   dist\pdfFDAValidator.exe "C:\path\to\pdf\folder"
echo.
pause