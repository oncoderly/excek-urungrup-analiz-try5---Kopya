@echo off
echo =====================================================
echo GEREKSIZ DOSYA TEMIZLEME
echo =====================================================
echo.
echo Bu script calisan programa zarar vermeden gereksiz dosyalari siler.
echo.
pause

echo Temizleniyor...

REM Debug ve test dosyalari
del "DEBUG_RUN.bat" 2>nul
del "HIZLI_BASLAT.bat" 2>nul
del "KOLAY_KURULUM.bat" 2>nul
del "TEMIZ_KURULUM.bat" 2>nul
del "CALISTIR_BASIT.bat" 2>nul
del "ALTERNATIF_AGGRID.bat" 2>nul

REM Eski kurulum scriptleri
del "setup_portable.bat" 2>nul
del "BASIT_KURULUM.bat" 2>nul
del "quick_start.bat" 2>nul

REM Eski build scriptleri
del "build_basit_exe.bat" 2>nul
del "build_exe.bat" 2>nul
del "build_windows_release.bat" 2>nul
del "create_exe.bat" 2>nul

REM Gereksiz Python dosyalari (__ ile baslayan yardimci dosyalar)
del "__check_connector.py" 2>nul
del "__cleanup_detail.py" 2>nul
del "__find_block_indices.py" 2>nul
del "__fix_indent.py" 2>nul
del "__fix_lines.py" 2>nul
del "__fix_metric.py" 2>nul
del "__remove_block.py" 2>nul
del "__rewrite_global_block.py" 2>nul
del "__trim_block.py" 2>nul
del "__view_pareto.py" 2>nul

REM Eski/kullanilmayan dosyalar
del "excel_analyzer_fixed.py" 2>nul
del "launcher.py" 2>nul
del "create_launcher.py" 2>nul
del "decode_sequences.py" 2>nul
del "remove_group_charts.py" 2>nul
del "rewrite_overall_section.py" 2>nul

REM Dokuman dosyalari (gerekirse silebilir)
del "distribution_guide.md" 2>nul
del "online_deployment_guide.md" 2>nul
del "setup_guide.md" 2>nul
del "PORTABLE_README.txt" 2>nul
del "DISTRIBUTION_README.txt" 2>nul

REM Git ve PowerShell dosyalari
del "git_upload_commands.bat" 2>nul
del "add_utf8_fix.ps1" 2>nul

REM Gereksiz CSS ve bos dosyalar
del "styles.css" 2>nul
del "runtime.txt" 2>nul

REM Temp ve build klasorleri
if exist "build" rmdir /s /q "build" 2>nul
if exist "__pycache__" rmdir /s /q "__pycache__" 2>nul

REM Gereksiz klasorler
if exist "fonts" rmdir /s /q "fonts" 2>nul
if exist "excek-urungrup-analiz-try5---Kopya" rmdir /s /q "excek-urungrup-analiz-try5---Kopya" 2>nul

echo.
echo =====================================================
echo ✓ TEMIZLIK TAMAMLANDI!
echo =====================================================
echo.
echo KALAN GEREKLI DOSYALAR:
echo ✓ excel_analyzer.py        (Ana uygulama)
echo ✓ excel_analyzer_basit.py  (Basit surum - yedek)
echo ✓ requirements.txt         (Kutuphaneler)
echo ✓ venv/                    (Python sanal ortami)
echo ✓ dist/                    (EXE dosyasi burada)
echo ✓ run_app.bat             (Uygulama calistirici)
echo ✓ AGGRID_KURULUM.bat      (st-aggrid kurulum)
echo ✓ FIX_AGGRID.bat          (st-aggrid duzeltici)
echo ✓ KILL_STREAMLIT.bat      (Port temizleyici)
echo ✓ CREATE_PORTABLE_EXE.bat (EXE olusturucu)
echo ✓ README.md               (Aciklama)
echo.
echo Programiniz ayni sekilde calisacak!
pause