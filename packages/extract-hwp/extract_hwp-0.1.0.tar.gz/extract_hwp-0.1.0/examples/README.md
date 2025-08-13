# extract-hwp 사용 예제

이 디렉토리에는 extract-hwp 라이브러리를 사용하는 다양한 예제들이 포함되어 있습니다.

## 예제 파일들

### 1. `basic_usage.py` - 기본 사용법
라이브러리의 기본적인 사용 방법을 보여주는 예제입니다.

```bash
python basic_usage.py
```

**주요 기능:**
- 단일 파일 텍스트 추출
- 암호화 파일 감지
- 오류 처리 방법
- 포맷별 추출 함수 사용법

### 2. `batch_processing.py` - 일괄 처리
디렉토리 내의 모든 HWP 파일을 일괄 처리하는 예제입니다.

```bash
python batch_processing.py <디렉토리> [출력형식]
```

**사용 예제:**
```bash
# 현재 디렉토리의 모든 HWP 파일을 텍스트 파일로 저장
python batch_processing.py ./documents txt

# JSON 형식으로 결과 저장
python batch_processing.py ./documents json
```

**주요 기능:**
- 재귀적 파일 검색 (하위 디렉토리 포함)
- 일괄 처리 진행 상황 표시
- 처리 결과 통계
- 다양한 출력 형식 지원

### 3. `cli_tool.py` - 명령줄 도구
HWP 파일 처리를 위한 완전한 명령줄 인터페이스입니다.

```bash
python cli_tool.py <파일경로> [옵션]
```

**사용 예제:**
```bash
# 기본 사용 (표준 출력)
python cli_tool.py document.hwp

# 파일로 저장
python cli_tool.py document.hwp --output extracted.txt

# 암호화 여부만 확인
python cli_tool.py document.hwp --check-password

# 조용한 모드로 실행
python cli_tool.py document.hwpx --quiet --output-dir ./outputs
```

**주요 옵션:**
- `-o, --output`: 출력 파일 지정
- `--output-dir`: 출력 디렉토리 지정
- `-c, --check-password`: 암호화 여부만 확인
- `-q, --quiet`: 진행 메시지 숨기기
- `--encoding`: 출력 파일 인코딩 지정

## 실행 방법

### 개발 환경에서 실행
```bash
# extract-hwp 프로젝트 루트 디렉토리에서
cd examples
python basic_usage.py
python batch_processing.py ./test_files
python cli_tool.py test.hwp
```

### 설치된 패키지로 실행
패키지가 설치된 상태에서는 import 경로 수정이 필요합니다:

```python
# 예제 파일 상단의 다음 부분을 제거하거나 주석 처리
# sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
```

## 테스트 파일 준비

예제를 실제로 테스트해보려면 HWP/HWPX 파일이 필요합니다:

1. **샘플 파일 생성**: 한글(HWP)에서 간단한 문서를 작성하고 `.hwp` 및 `.hwpx` 형식으로 저장
2. **테스트 디렉토리**: `./test_files/` 디렉토리를 만들고 샘플 파일들을 넣기
3. **암호화 파일**: 암호가 설정된 HWP 파일도 테스트용으로 준비

## 고급 사용법

### 커스텀 처리 로직
```python
from extract_hwp import extract_text_from_hwp, is_hwp_file_password_protected

def custom_processor(file_path):
    """커스텀 HWP 파일 처리기"""
    
    # 1. 암호화 확인
    if is_hwp_file_password_protected(file_path):
        return None, "암호화된 파일"
    
    # 2. 텍스트 추출
    text, error = extract_text_from_hwp(file_path)
    if error:
        return None, error
    
    # 3. 후처리 (예: 텍스트 정리)
    processed_text = text.strip()
    processed_text = '\n'.join(line.strip() for line in processed_text.split('\n') if line.strip())
    
    return processed_text, None
```

### 에러 처리 패턴
```python
import logging

def safe_extract(file_path):
    """안전한 텍스트 추출 (로깅 포함)"""
    try:
        text, error = extract_text_from_hwp(file_path)
        if error:
            logging.warning(f"추출 실패: {file_path} - {error}")
            return ""
        
        logging.info(f"추출 성공: {file_path} ({len(text)} 문자)")
        return text
        
    except Exception as e:
        logging.error(f"예외 발생: {file_path} - {e}")
        return ""
```

## 성능 최적화 팁

1. **대용량 파일**: 매우 큰 HWP 파일의 경우 메모리 사용량에 주의
2. **일괄 처리**: 많은 파일을 처리할 때는 멀티프로세싱 사용 고려
3. **암호화 확인**: 처리 전에 암호화 여부를 먼저 확인하여 불필요한 처리 방지

## 문제 해결

### 일반적인 문제들

1. **ImportError**: 패키지가 설치되지 않은 경우
   ```bash
   pip install extract-hwp
   ```

2. **파일을 찾을 수 없음**: 파일 경로 확인
   ```python
   import os
   print(os.path.exists("your_file.hwp"))
   ```

3. **인코딩 오류**: 파일명에 특수문자가 있는 경우
   ```python
   file_path = file_path.encode('utf-8').decode('utf-8')
   ```

4. **권한 오류**: 파일 읽기 권한 확인
   ```bash
   ls -la your_file.hwp
   ```

더 자세한 정보는 프로젝트의 메인 README.md를 참조하세요.