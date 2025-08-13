#!/usr/bin/env python3
"""
HWP 파일 일괄 처리 예제

디렉토리 내의 모든 HWP/HWPX 파일을 일괄 처리하여 텍스트를 추출하는 예제입니다.
"""

import os
import sys
from pathlib import Path
import glob
import json
from datetime import datetime

# 패키지 경로 추가 (개발 환경에서 실행할 때)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from extract_hwp import extract_text_from_hwp, is_hwp_file_password_protected


def find_hwp_files(directory):
    """디렉토리에서 HWP/HWPX 파일을 찾습니다."""
    hwp_files = []
    
    # .hwp 파일 찾기
    hwp_files.extend(glob.glob(os.path.join(directory, "**", "*.hwp"), recursive=True))
    
    # .hwpx 파일 찾기
    hwp_files.extend(glob.glob(os.path.join(directory, "**", "*.hwpx"), recursive=True))
    
    return sorted(hwp_files)


def process_hwp_files(directory, output_format="txt"):
    """
    디렉토리의 모든 HWP 파일을 처리합니다.
    
    Args:
        directory: 처리할 디렉토리 경로
        output_format: 출력 형식 ("txt", "json")
    """
    print(f"=== HWP 파일 일괄 처리 ===")
    print(f"대상 디렉토리: {directory}")
    print(f"출력 형식: {output_format}")
    print()
    
    # HWP 파일 찾기
    hwp_files = find_hwp_files(directory)
    
    if not hwp_files:
        print("처리할 HWP 파일이 없습니다.")
        return
    
    print(f"발견된 HWP 파일: {len(hwp_files)}개")
    print()
    
    # 처리 결과 저장
    results = []
    success_count = 0
    error_count = 0
    protected_count = 0
    
    for i, file_path in enumerate(hwp_files, 1):
        print(f"[{i}/{len(hwp_files)}] 처리 중: {os.path.basename(file_path)}")
        
        result = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "processed_at": datetime.now().isoformat(),
            "status": "unknown",
            "text": "",
            "error": None,
            "text_length": 0,
            "is_protected": False
        }
        
        try:
            # 암호화 확인
            if is_hwp_file_password_protected(file_path):
                print(f"  🔒 암호로 보호된 파일 (건너뛰기)")
                result["status"] = "protected"
                result["is_protected"] = True
                protected_count += 1
            else:
                # 텍스트 추출
                text, error = extract_text_from_hwp(file_path)
                
                if error is None:
                    print(f"  ✅ 성공 ({len(text)} 문자)")
                    result["status"] = "success"
                    result["text"] = text
                    result["text_length"] = len(text)
                    success_count += 1
                    
                    # 개별 텍스트 파일 저장 (txt 형식인 경우)
                    if output_format == "txt":
                        save_text_file(file_path, text)
                        
                else:
                    print(f"  ❌ 실패: {error}")
                    result["status"] = "error"
                    result["error"] = error
                    error_count += 1
                    
        except Exception as e:
            print(f"  💥 예외 발생: {e}")
            result["status"] = "exception"
            result["error"] = str(e)
            error_count += 1
        
        results.append(result)
        print()
    
    # 결과 요약
    print("=== 처리 결과 요약 ===")
    print(f"전체 파일: {len(hwp_files)}개")
    print(f"성공: {success_count}개")
    print(f"실패: {error_count}개")
    print(f"암호화됨: {protected_count}개")
    print()
    
    # 결과 저장
    if output_format == "json":
        save_json_results(directory, results)
    
    return results


def save_text_file(original_path, text):
    """추출된 텍스트를 개별 파일로 저장합니다."""
    base_name = os.path.splitext(os.path.basename(original_path))[0]
    output_path = f"{base_name}_extracted.txt"
    
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"    💾 텍스트 저장: {output_path}")
    except Exception as e:
        print(f"    ❌ 저장 실패: {e}")


def save_json_results(directory, results):
    """처리 결과를 JSON 파일로 저장합니다."""
    output_path = f"hwp_extraction_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"💾 결과 저장: {output_path}")
    except Exception as e:
        print(f"❌ JSON 저장 실패: {e}")


def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print("사용법: python batch_processing.py <디렉토리> [출력형식]")
        print("출력형식: txt (기본값) 또는 json")
        print()
        print("예제:")
        print("  python batch_processing.py ./documents")
        print("  python batch_processing.py ./documents txt")
        print("  python batch_processing.py ./documents json")
        return
    
    directory = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else "txt"
    
    if not os.path.exists(directory):
        print(f"❌ 디렉토리가 존재하지 않습니다: {directory}")
        return
    
    if output_format not in ["txt", "json"]:
        print(f"❌ 지원하지 않는 출력 형식: {output_format}")
        print("   지원 형식: txt, json")
        return
    
    # 일괄 처리 실행
    process_hwp_files(directory, output_format)


if __name__ == "__main__":
    main()