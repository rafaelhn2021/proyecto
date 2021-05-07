@echo *******************************************************************************************
@echo Bienvenido a el Script para instalar en Windows 10 del software SiDECLARA v1.0
@echo *******************************************************************************************
@echo Recuerde que es necesario que siga los sguientes pasos para que este script sea efectivo:
@echo 1.- Necesita instalar DOCKER y DOCKER-COMPOSE en su equipo windows y habilitar docker con los contenedores tipo Linux
@echo 2.- En el docker dashboard, necesia ir a Settings>Resources>File sharing y agregar la ubicación del proyecto
@set /p DUMMY=si ya ha hecho estos pasos presione ENTER para continuar o cierre para salir...	
@echo off
@set COMPOSE_CONVERT_WINDOWS_PATHS=1
@echo Puede combrobar el avance en el docker dashboard.
@echo Cuando la consola de docker muestre un mensaje como 'spawned uWSGI worker' es que a terminado ya puede ir a su navegador para ver el resultado en http://localhost
@echo on
@docker-compose -f proyecto/docker-compose.yml up -d
@set /p DUMMY=presione ENTER para continuar...	
@start "" "C:\Program Files\Docker\Docker\frontend\Docker Desktop.exe"