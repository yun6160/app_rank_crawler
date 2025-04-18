## 1. 가상환경 설치 및 실행

### 꼭 cmd 터미널에서 커맨드 한줄씩 입력(python3 설치했는데 버전 못찾는다고 에러뜨면 vscode 다시 실행)

python -m venv venv
venv\Scripts\activate

## 2. 패키지 설치

pip install -r requirements.txt

## 3. 실행 커맨드(이메일 입력 무시하면 됨)

streamlit run app.py

## 4. .env 파일 생성

UPUP_EMAIL=banfigvow@bangban.uk
UPUP_PASSWORD=dbswjdgus02!
ENV=development
