# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python library for extracting text from Korean HWP (Hangul Word Processor) files, supporting both HWP 5.0 (OLE format) and HWPX (ZIP-based XML format) files. The project includes password protection detection and structured text extraction capabilities.

## Development Commands

### Package Management
- **Install dependencies**: `uv sync` (uses uv for dependency management)
- **Run main script**: `python main.py` (basic hello world entry point)
- **Run extraction**: `python -m extract_hwp` or import functions from `extract_hwp.py`

### Testing and Quality
No specific test commands are configured yet - tests would need to be added to pyproject.toml.

## Code Architecture

### Core Components

**extract_hwp.py**: Main extraction module with three key functions:
- `extract_text_from_hwp()`: Unified interface that routes to appropriate extractor based on file extension
- `extract_text_from_hwpx()`: HWPX file processor (ZIP-based XML format)
- `extract_text_from_hwp5()`: HWP 5.0 processor (OLE compound document format)

**Password Protection Detection**:
- `is_hwpx_password_protected()`: Checks HWPX files via META-INF/manifest.xml encryption data
- `is_hwp5_password_protected()`: Checks HWP 5.0 files via FileHeader stream bit flags
- `is_hwp_file_password_protected()`: Unified interface for both formats

### File Format Handling

**HWPX Files**: 
- ZIP archives containing XML sections in `Contents/section*.xml`
- Text extracted from `<p>` (paragraph) elements containing `<t>` (text) nodes
- Preserves paragraph structure with newlines

**HWP 5.0 Files**:
- OLE compound documents with compressed BodyText streams
- Requires decompression (zlib) and binary parsing of structured records
- Text stored in PARA_TEXT records (tag_id: 67) as Unicode sequences
- Supports multiple sections (`BodyText/Section0`, `BodyText/Section1`, etc.)

### Dependencies

**External Libraries**:
- `olefile`: OLE compound document parsing for HWP 5.0 files
- `superclaude>=3.0.0.2`: Framework dependency (external utility framework)

**Framework Integration**:
The code imports from `core.util_text` and `core.util_extraction` modules, indicating this is part of a larger text extraction framework. These modules provide:
- Text cleaning/indexing utilities
- Error handling decorators (@handle_extraction_errors)
- File validation and logging utilities

### Error Handling Strategy

The codebase uses a defensive approach:
- Password-protected files are detected and skipped (not extracted)
- File validation occurs before processing
- Graceful degradation for parsing errors
- Comprehensive logging for troubleshooting
- Returns empty strings rather than throwing exceptions for most extraction failures

### Character Encoding Considerations

HWP 5.0 extraction includes specific Unicode range validation:
- Basic Latin (0x0020-0x007E)
- Korean syllables (0xAC00-0xD7AF) 
- Korean Jamo (0x3130-0x318F)
- Full-width characters (0xFF00-0xFFEF)
- General punctuation (0x2000-0x206F)