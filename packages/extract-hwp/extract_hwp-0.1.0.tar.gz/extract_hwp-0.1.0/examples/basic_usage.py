#!/usr/bin/env python3
"""
extract-hwp 기본 사용법 예제

HWP 및 HWPX 파일에서 텍스트를 추출하는 기본적인 방법을 보여줍니다.
"""

import os
import sys
from pathlib import Path

# 패키지 경로 추가 (개발 환경에서 실행할 때)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from extract_hwp import (
    extract_text_from_hwp,
    extract_text_from_hwpx,
    extract_text_from_hwp5,
    is_hwp_file_password_protected
)


def main():
    """기본 사용법 데모"""
    print("=== extract-hwp 기본 사용법 예제 ===\n")
    
    # 예제 파일 경로 (실제 파일이 있다고 가정)
    sample_files = [
        "sample_document.hwp",
        "sample_document.hwpx",
        "protected_document.hwp"
    ]
    
    for file_path in sample_files:
        print(f"파일 처리: {file_path}")
        
        # 파일 존재 확인
        if not os.path.exists(file_path):
            print(f"  ⚠️  파일이 존재하지 않습니다: {file_path}")
            print(f"      실제 HWP/HWPX 파일을 사용해보세요.\n")
            continue
        
        # 암호화 파일 확인
        try:
            is_protected = is_hwp_file_password_protected(file_path)
            if is_protected:
                print(f"  🔒 암호로 보호된 파일입니다.")
                print(f"      암호화된 파일은 텍스트 추출이 불가능합니다.\n")
                continue
            else:
                print(f"  ✅ 암호화되지 않은 파일입니다.")
        except Exception as e:
            print(f"  ❌ 암호화 확인 중 오류: {e}\n")
            continue
        
        # 텍스트 추출
        try:
            # 통합 함수 사용 (권장 방법)
            text, error = extract_text_from_hwp(file_path)
            
            if error is None:
                print(f"  📄 텍스트 추출 성공!")
                print(f"     추출된 텍스트 길이: {len(text)} 문자")
                
                # 첫 100자 미리보기
                preview = text[:100].replace('\n', ' ')
                if len(text) > 100:
                    preview += "..."
                print(f"     미리보기: {preview}")
                
            else:
                print(f"  ❌ 텍스트 추출 실패: {error}")
                
        except Exception as e:
            print(f"  ❌ 처리 중 오류 발생: {e}")
        
        print()  # 빈 줄


def demo_format_specific_extraction():
    """포맷별 추출 함수 사용법 데모"""
    print("=== 포맷별 추출 함수 사용법 ===\n")
    
    print("1. HWPX 파일 전용 추출:")
    print("   from extract_hwp import extract_text_from_hwpx")
    print("   text = extract_text_from_hwpx('document.hwpx')")
    print()
    
    print("2. HWP 5.0 파일 전용 추출:")
    print("   from extract_hwp import extract_text_from_hwp5")
    print("   text = extract_text_from_hwp5('document.hwp')")
    print()
    
    print("3. 통합 함수 사용 (권장):")
    print("   from extract_hwp import extract_text_from_hwp")
    print("   text, error = extract_text_from_hwp('document.hwp')")
    print("   if error is None:")
    print("       print(text)")
    print("   else:")
    print("       print(f'오류: {error}')")
    print()


def demo_error_handling():
    """오류 처리 예제"""
    print("=== 오류 처리 예제 ===\n")
    
    # 존재하지 않는 파일
    try:
        text, error = extract_text_from_hwp("nonexistent.hwp")
        if error:
            print(f"예상된 오류 (파일 없음): {error}")
    except FileNotFoundError as e:
        print(f"FileNotFoundError 처리: {e}")
    
    # 지원하지 않는 파일 형식
    try:
        # 임시 텍스트 파일 생성
        with open("temp.txt", "w", encoding="utf-8") as f:
            f.write("이것은 HWP 파일이 아닙니다.")
        
        text, error = extract_text_from_hwp("temp.txt")
        if error:
            print(f"예상된 오류 (지원하지 않는 형식): {error}")
            
        # 임시 파일 삭제
        os.remove("temp.txt")
        
    except Exception as e:
        print(f"기타 오류: {e}")
        # 임시 파일 정리
        if os.path.exists("temp.txt"):
            os.remove("temp.txt")
    
    print()


if __name__ == "__main__":
    main()
    demo_format_specific_extraction()
    demo_error_handling()
    
    print("=== 예제 실행 완료 ===")
    print("실제 HWP/HWPX 파일로 테스트해보세요!")