@echo off

rem pyTRLCConverter - A tool to convert TRLC files to specific formats.
rem Copyright (c) 2024 - 2025 NewTec GmbH
rem
rem This file is part of pyTRLCConverter program.
rem
rem The pyTRLCConverter program is free software: you can redistribute it and/or modify it under
rem the terms of the GNU General Public License as published by the Free Software Foundation,
rem either version 3 of the License, or (at your option) any later version.
rem
rem The pyTRLCConverter program is distributed in the hope that it will be useful, but
rem WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
rem FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
rem
rem You should have received a copy of the GNU General Public License along with pyTRLCConverter.
rem If not, see <https://www.gnu.org/licenses/>.

set LOBSTER_TRLC=lobster-trlc
set LOBSTER_PYTHON=lobster-python
set LOBSTER_REPORT=lobster-report
set LOBSTER_ONLINE_REPORT=lobster-online-report
set LOBSTER_RENDERER=lobster-html-report
set OUT_DIR=out
set MODELS=.\..\..\trlc\model

set SW_REQ_LOBSTER_CONF=.\lobster-trlc-sw-req.yaml
set SW_REQ_LOBSTER_OUT=%OUT_DIR%\sw_req-lobster.json

set SW_TEST_LOBSTER_CONF=.\lobster-trlc-sw-test.yaml
set SW_TEST_LOBSTER_OUT=%OUT_DIR%\sw_test-lobster.json

set SW_CODE_SOURCES=.\..\..\src\pyTRLCConverter
set SW_CODE_LOBSTER_OUT=%OUT_DIR%\sw_code-lobster.json

set SW_TEST_CODE_SOURCES=.\..\..\tests
set SW_TEST_CODE_LOBSTER_OUT=%OUT_DIR%\sw_test_code-lobster.json

set SW_REQ_LOBSTER_REPORT_CONF=.\lobster-report-sw-req.conf
set SW_REQ_LOBSTER_REPORT_OUT=%OUT_DIR%\lobster-report-sw-req-lobster.json
set SW_REQ_LOBSTER_ONLINE_REPORT_OUT=%OUT_DIR%\lobster-online-report-sw-req-lobster.json
set SW_REQ_LOBSTER_HTML_OUT=%OUT_DIR%\sw_req_tracing_online_report.html

set SW_TEST_LOBSTER_REPORT_CONF=.\lobster-report-sw-test.conf
set SW_TEST_LOBSTER_REPORT_OUT=%OUT_DIR%\lobster-report-sw-test-lobster.json
set SW_TEST_LOBSTER_ONLINE_REPORT_OUT=%OUT_DIR%\lobster-online-report-sw-rest-lobster.json
set SW_TEST_LOBSTER_HTML_OUT=%OUT_DIR%\sw_test_tracing_online_report.html

set LOCAL_REPOSITORY_ROOT=.\..\..

if not exist "%OUT_DIR%" (
    md %OUT_DIR%
) else (
    del /q "%OUT_DIR%\*"
)

rem ********** SW-Requirements **********
%LOBSTER_TRLC% --config %SW_REQ_LOBSTER_CONF% --out %SW_REQ_LOBSTER_OUT%

if errorlevel 1 (
    goto error
)

rem ********** SW-Tests **********
%LOBSTER_TRLC% --config %SW_TEST_LOBSTER_CONF% --out %SW_TEST_LOBSTER_OUT%

if errorlevel 1 (
    goto error
)

rem ********** SW-Code **********
%LOBSTER_PYTHON% --out %SW_CODE_LOBSTER_OUT% %SW_CODE_SOURCES%

if errorlevel 1 (
    goto error
)

rem ********** SW-Test Code **********
%LOBSTER_PYTHON% --out %SW_TEST_CODE_LOBSTER_OUT% --activity %SW_TEST_CODE_SOURCES%

if errorlevel 1 (
    goto error
)

rem ********** Report SW-Requirements **********
%LOBSTER_REPORT% --lobster-config %SW_REQ_LOBSTER_REPORT_CONF% --out %SW_REQ_LOBSTER_REPORT_OUT%

if errorlevel 1 (
    goto error
)

rem ********** Online Report SW-Requirements **********
%LOBSTER_ONLINE_REPORT% --out %SW_REQ_LOBSTER_ONLINE_REPORT_OUT% %SW_REQ_LOBSTER_REPORT_OUT% --repo-root %LOCAL_REPOSITORY_ROOT%

if errorlevel 1 (
    goto error
)

rem ********** Report SW-Requirements to HTML **********
%LOBSTER_RENDERER% --out %SW_REQ_LOBSTER_HTML_OUT% %SW_REQ_LOBSTER_ONLINE_REPORT_OUT%

if errorlevel 1 (
    goto error
)

rem ********** Report SW-Tests **********
%LOBSTER_REPORT% --lobster-config %SW_TEST_LOBSTER_REPORT_CONF% --out %SW_TEST_LOBSTER_REPORT_OUT%

if errorlevel 1 (
    goto error
)

rem ********** Online Report SW-Tests **********
%LOBSTER_ONLINE_REPORT% --out %SW_TEST_LOBSTER_ONLINE_REPORT_OUT% %SW_TEST_LOBSTER_REPORT_OUT% --repo-root %LOCAL_REPOSITORY_ROOT%

if errorlevel 1 (
    goto error
)

rem ********** Report SW-Tests to HTML **********
%LOBSTER_RENDERER% --out %SW_TEST_LOBSTER_HTML_OUT% %SW_TEST_LOBSTER_ONLINE_REPORT_OUT%

if errorlevel 1 (
    goto error
)

goto finished

:error

:finished
echo Finished