# AI Hub 데이터 다운로드 가이드

## 빠른 시작

1. **AI Hub 접속**: https://aihub.or.kr/aihubdata/data/view.do?dataSetSn=576
2. **로그인** (회원가입 필요)
3. **데이터 신청** 버튼 클릭
4. **승인 대기** (보통 1-2일 소요)
5. **다운로드** 진행

---

## 다운로드할 파일 (라벨링 데이터만!)

### 📂 경로
```
166.약품식별 인공지능 개발을 위한 경구약제 이미지 데이터
└── 01.데이터
    └── 1.Training
        └── 라벨링데이터
```

### 📥 다운로드 목록

**경구약제조합 5000종** (8개 파일, 약 60MB):
```
TL_1_조합.zip  (7.84 MB)
TL_2_조합.zip  (7.31 MB)
TL_3_조합.zip  (7.38 MB)
TL_4_조합.zip  (6.95 MB)
TL_5_조합.zip  (7.76 MB)
TL_6_조합.zip  (7.72 MB)
TL_7_조합.zip  (7.26 MB)
TL_8_조합.zip  (7.35 MB)
```

**단일경구약제 5000종** (81개 파일, 약 2GB):
```
TL_1_단일.zip ~ TL_81_단일.zip
```

### ⚠️ 다운로드하지 말 것
- ❌ `TS_*.zip` (원천데이터) - 이미지 파일로 수백 GB
- ❌ `VS_*.zip` (Validation 원천데이터)
- ✅ `TL_*.zip` (라벨링 데이터)만 다운로드!

---

## 다운로드 후 설정

### 1. 압축 해제 (JSON 파일만 추출)
```bash
# 다운로드 폴더로 이동
cd ~/Downloads

# 프로젝트 data 폴더에 JSON만 압축 해제 (-j 옵션으로 폴더 제거)
mkdir -p /Users/tlsalsco/pillmate/data/aihub

for file in TL_*.zip; do 
    unzip -j "$file" '*.json' -d /Users/tlsalsco/pillmate/data/aihub/
done
```

**최종 폴더 구조**:
```
/Users/tlsalsco/pillmate/
└── data/
    └── aihub/
        ├── 001.json
        ├── 002.json
        ├── 003.json
        └── ... (JSON 파일만)
```

### 2. 파일 확인
```bash
cd /Users/tlsalsco/pillmate

# JSON 파일 개수 확인
ls -1 data/aihub/*.json | wc -l

# 파일 크기 확인
du -sh data/aihub/

# 첫 번째 파일 내용 확인
head -20 data/aihub/*.json | head -20
```

### 3. 데이터 로드 테스트
```bash
# 가상환경 활성화
source venv/bin/activate

# 데이터 로드 확인
python -c "from app.utils.aihub_loader import get_aihub_loader; loader = get_aihub_loader(); print(f'✅ 로드된 약 개수: {len(loader.medicine_data)}')"
```

---

## 예상 결과

성공 시 출력:
```
📂 89개의 JSON 파일을 찾았습니다.
✅ 총 10000개의 약 데이터 로드 완료
✅ 로드된 약 개수: 10000
```

---

## 트러블슈팅

### 문제: "JSON 파일이 없습니다"
**해결**: ZIP 파일 압축 해제 확인
```bash
ls data/aihub/*.json
```

### 문제: "데이터 경로가 없습니다"
**해결**: 폴더 생성
```bash
mkdir -p data/aihub
```

### 문제: 다운로드 용량이 너무 큼
**해결**: 원천데이터(TS_*.zip) 대신 라벨링 데이터(TL_*.zip)만 다운로드

---

## 다음 단계

1. ✅ 데이터 다운로드 완료
2. ✅ 압축 해제 및 배치 완료
3. ✅ 데이터 로드 테스트 완료
4. 🔄 서버 재시작 후 OCR API 테스트
5. 🔄 Google Cloud Vision API 설정 (선택사항)

자세한 내용은 `AIHUB_SETUP.md` 참고
