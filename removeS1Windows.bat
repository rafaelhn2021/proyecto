@echo desinstalando SiDeclara.
@echo Esto desistala todo el software y su contenido.
@echo Se recomienda respaldar primero
@set /p DUMMY=presione ENTER para continuar o cierre para cancelar.
@set COMPOSE_CONVERT_WINDOWS_PATHS=1
@echo off
(for /f delims=" %%i in ('type proyecto\declaraciones\.env') do (
 if "%%b"=="1" (echo %%i) else (
  echo %%i|find "LOAD_INITIAL_DATA" >null&& echo %i= ||echo %%i=%%b
 )
)) > proyecto/declaraciones/.env
@echo on
@docker-compose -f proyecto/docker-compose.yml down
@set /p DUMMY=Finalizado, presione ENTER para continuar...
@start "" "C:\Program Files\Docker\Docker\frontend\Docker Desktop.exe"
