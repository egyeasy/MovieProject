# 환경설정
- python global 3.6.7
- django 2.1.8
- movie-venv
- bash 설정
```bash
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bashrc
exec "$SHELL"

git clone https://github.com/pyenv/pyenv-virtualenv.git $(pyenv root)/plugins/pyenv-virtualenv
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
exec "$SHELL"

pyenv install 3.6.7
pyenv global 3.6.7
mkdir MovieProject
cd MovieProject
pyenv virtualenv 3.6.7 movie-venv
pyenv local movie-venv
pip install Django==2.1.8

pip install django-bootstrap4
```



## 190416 프로젝트 시작
- 회원가입, 로그인, 로그아웃 구현
- bootstrap 다운로드하여 프로젝트 최상단 static 폴더에 로드
- `settings.py`에서 `STATICFILE_DIRS` 설정하여 `debug=True`일 때 static load 가능하도록 설정


## 190418 프로젝트 원상복구
- 회원가입 직후 로그인 구현
- 로그인 여부에 따라 navbar 다르게 보여주기 구현