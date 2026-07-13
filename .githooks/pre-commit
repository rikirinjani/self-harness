@echo off
REM Pre-commit hook — validate tools code + run skill validator
REM Install: cd self-harness && git config core.hooksPath .githooks

echo [pre-commit] Checking syntax...
python -c "import ast; ast.parse(open('tools/validate_skills.py').read())" || exit /b 1
python -c "import ast; ast.parse(open('tools/bundle_web.py').read())" || exit /b 1
python -c "import yaml; yaml.safe_load(open('tools/module.yaml'))" || exit /b 1

echo [pre-commit] Validating skills...
python tools/validate_skills.py --json > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [Skill Validator] Skills have issues. Run: python tools/validate_skills.py
    exit /b 1
)

echo [pre-commit] All good
