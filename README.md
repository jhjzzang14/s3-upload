# S3 Image Upload Service

FastAPI와 Jinja2를 사용한 S3 이미지 업로드 웹 서비스입니다.

## 기능

- 웹 UI를 통한 이미지 파일 업로드
- S3 bucket에 prefix(폴더) 지정 업로드
- 업로드 후 공개 URL 제공
- 이미지 미리보기 및 URL 복사 기능
- 파일 유효성 검사 및 에러 처리

## 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 AWS 설정을 입력하세요:

```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=ap-northeast-2
S3_BUCKET_NAME=your-bucket-name
S3_BASE_URL=https://your-bucket-name.s3.ap-northeast-2.amazonaws.com
```

### 3. S3 버킷 설정

- S3 버킷의 Block Public Access 설정을 해제
- 버킷 정책에서 public read 권한 허용
- 필요시 CORS 설정 추가

### 4. 서버 실행

```bash
# 개발 모드
python main.py

# 또는 uvicorn 직접 실행
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API 엔드포인트

- `GET /` - 업로드 폼 페이지
- `POST /upload` - 이미지 업로드 처리
- `GET /health` - 헬스 체크

## 지원 이미지 형식

- JPG, JPEG
- PNG
- GIF
- WebP
- BMP

## 사용법

1. 웹 브라우저에서 `http://localhost:8000` 접속
2. Prefix 입력 (예: `images/profile`, `docs/thumbnails`)
3. 이미지 파일 선택
4. 업로드 버튼 클릭
5. 결과 페이지에서 공개 URL 확인 및 복사

## 보안 주의사항

- 프로덕션 환경에서는 적절한 인증 및 권한 관리 필요
- 파일 크기 제한 및 업로드 속도 제한 고려
- S3 버킷 권한을 최소한으로 설정