@echo off
setlocal

rem Gradle wrapper launcher for the RajOS Android companion app.

set DIR=%~dp0

if defined JAVA_HOME (
  set "JAVA_EXE=%JAVA_HOME%\bin\java.exe"
) else (
  set "JAVA_EXE=java.exe"
)

"%JAVA_EXE%" -Xmx64m -Xms64m -Dorg.gradle.appname=gradlew -classpath "%DIR%gradle-wrapper.jar" org.gradle.wrapper.GradleWrapperMain %*
