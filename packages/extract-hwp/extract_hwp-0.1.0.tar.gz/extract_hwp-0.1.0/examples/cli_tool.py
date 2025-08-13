#!/usr/bin/env python3
"""
extract-hwp 명령줄 도구

HWP 파일 텍스트 추출을 위한 간단한 CLI 도구입니다.
"""

import os
import sys
import argparse
from pathlib import Path

# 패키지 경로 추가 (개발 환경에서 실행할 때)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from extract_hwp import (
    extract_text_from_hwp,
    is_hwp_file_password_protected
)


def create_parser():
    """명령줄 인자 파서를 생성합니다."""
    parser = argparse.ArgumentParser(
        description="HWP/HWPX 파일에서 텍스트를 추출합니다.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예제:
  %(prog)s document.hwp
  %(prog)s document.hwpx --output extracted.txt
  %(prog)s document.hwp --check-password
  %(prog)s document.hwpx --quiet --output-dir ./outputs
        """
    )
    
    parser.add_argument(
        "input_file",
        help="처리할 HWP 또는 HWPX 파일 경로"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="출력 파일 경로 (기본값: 표준 출력)"
    )
    
    parser.add_argument(
        "--output-dir",
        help="출력 디렉토리 (파일명은 자동 생성)"
    )
    
    parser.add_argument(
        "-c", "--check-password",
        action="store_true",
        help="암호화 여부만 확인하고 종료"
    )
    
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="진행 상황 메시지 숨기기"
    )
    
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="출력 파일 인코딩 (기본값: utf-8)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="extract-hwp 0.1.0"
    )
    
    return parser


def check_password_only(file_path, quiet=False):
    """암호화 여부만 확인합니다."""
    try:
        is_protected = is_hwp_file_password_protected(file_path)
        
        if not quiet:
            if is_protected:
                print(f"🔒 파일이 암호로 보호되어 있습니다: {file_path}")
            else:
                print(f"✅ 파일이 암호화되지 않았습니다: {file_path}")
        
        # 종료 코드: 0=암호화되지 않음, 1=암호화됨, 2=오류
        return 1 if is_protected else 0
        
    except Exception as e:
        if not quiet:
            print(f"❌ 암호화 확인 중 오류: {e}", file=sys.stderr)
        return 2


def extract_text(file_path, quiet=False):
    """텍스트를 추출합니다."""
    try:
        if not quiet:
            print(f"처리 중: {file_path}", file=sys.stderr)
        
        # 암호화 확인
        if is_hwp_file_password_protected(file_path):
            if not quiet:
                print(f"❌ 암호로 보호된 파일입니다: {file_path}", file=sys.stderr)
            return None, "암호로 보호된 파일"
        
        # 텍스트 추출
        text, error = extract_text_from_hwp(file_path)
        
        if error is None:
            if not quiet:
                print(f"✅ 추출 완료 ({len(text)} 문자)", file=sys.stderr)
            return text, None
        else:
            if not quiet:
                print(f"❌ 추출 실패: {error}", file=sys.stderr)
            return None, error
            
    except Exception as e:
        error_msg = f"처리 중 오류: {e}"
        if not quiet:
            print(f"❌ {error_msg}", file=sys.stderr)
        return None, error_msg


def save_to_file(text, output_path, encoding="utf-8", quiet=False):
    """텍스트를 파일로 저장합니다."""
    try:
        # 출력 디렉토리 생성
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        with open(output_path, "w", encoding=encoding) as f:
            f.write(text)
        
        if not quiet:
            print(f"💾 저장 완료: {output_path}", file=sys.stderr)
        
        return True
        
    except Exception as e:
        if not quiet:
            print(f"❌ 저장 실패: {e}", file=sys.stderr)
        return False


def generate_output_path(input_path, output_dir):
    """출력 파일 경로를 자동 생성합니다."""
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_filename = f"{base_name}_extracted.txt"
    
    if output_dir:
        return os.path.join(output_dir, output_filename)
    else:
        return output_filename


def main():
    """메인 함수"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 입력 파일 확인
    if not os.path.exists(args.input_file):
        print(f"❌ 파일이 존재하지 않습니다: {args.input_file}", file=sys.stderr)
        return 1
    
    # 암호화 확인만 하는 경우
    if args.check_password:
        return check_password_only(args.input_file, args.quiet)
    
    # 텍스트 추출
    text, error = extract_text(args.input_file, args.quiet)
    
    if error:
        print(f"❌ {error}", file=sys.stderr)
        return 1
    
    if text is None:
        return 1
    
    # 출력 처리
    if args.output:
        # 명시적 출력 파일
        if save_to_file(text, args.output, args.encoding, args.quiet):
            return 0
        else:
            return 1
    elif args.output_dir:
        # 출력 디렉토리 지정
        output_path = generate_output_path(args.input_file, args.output_dir)
        if save_to_file(text, output_path, args.encoding, args.quiet):
            return 0
        else:
            return 1
    else:
        # 표준 출력
        try:
            print(text)
            return 0
        except Exception as e:
            if not args.quiet:
                print(f"❌ 출력 오류: {e}", file=sys.stderr)
            return 1


if __name__ == "__main__":
    sys.exit(main())