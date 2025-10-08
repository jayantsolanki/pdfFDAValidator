@echo off
echo ========================================
echo PDF Batch Processor
echo ========================================
echo.

if "%~1"=="" (
    set /p folder="Enter path to PDF folder: "
) else (
    set folder=%~1
)

echo.
echo Processing PDFs in: %folder%
echo.

PDFBatchProcessor.exe "%folder%"

echo.
pause