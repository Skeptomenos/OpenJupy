# Implementation Plan - OpenCode Jupyter Integration

## Phase 1: Setup Documentation & Environment [COMPLETED]
- [x] Task 1: Create `SETUP_INSTRUCTIONS.md` with required `opencode.json` and `oh-my-opencode.json` snippets (DO NOT edit files directly)
- [x] Task 2: Create a validation script to check for Jupyter and dependencies
- [x] Task 3: Define the proposed `data-scientist` agent configuration in a local file

## Phase 2: Smart Error Handling & Guidance Logic [COMPLETED]
- [x] Task 4: Implement a Python-based middleware layer for traceback interception
- [x] Task 5: Implement ModuleNotFoundError fix mapping
- [x] Task 6: Implement package name mismatch mapping (e.g., cv2 -> opencv-python)
- [x] Task 7: Implement tool response wrapper for 'claude_tip' and 'claude_next' enrichment

## Phase 3: Integration & Testing [COMPLETED]
- [x] Task 8: Create unit tests for ErrorHandler, ResponseWrapper, and mappings (53 tests)
- [x] Task 9: Verify multimodal plot rendering (integration tests with mocks)
- [x] Task 10: Document real-time sync verification in SETUP_INSTRUCTIONS.md
- [x] Task 11: Final end-to-end validation (all tests pass, build succeeds, mypy clean)
