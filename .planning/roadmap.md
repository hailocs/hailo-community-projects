# Project Roadmap: Hailo Agentic Development Infrastructure Transition

## Vision

Transform hailo-community-projects into the central hub for Hailo community development with integrated **cross-platform** agentic AI tooling. The repo uses hailo-apps-infra as a git submodule (installed in editable mode), hosts shared agentic knowledge in `.hailo/`, community-generated apps, and existing community projects. Supports Claude Code, VS Code Copilot, and Cursor through thin platform-specific entry points. No backward compatibility with the current repo structure is required — this is a clean restructure.

---

## Phase 1: Foundation — Git Submodule & Clean Install

- **Goal:** Establish hailo-apps-infra as a git submodule and rewrite the installation flow.
- **Status:** Not started
- **Key Deliverables:** `.gitmodules`, rewritten `install.sh`, `setup_env.sh`, clean `.gitignore`, remove `basic_pipelines/` and legacy scripts
- **Success Criteria:** `source setup_env.sh` works, imports succeed

---

## Phase 2+4: Cross-Platform Agentic Infrastructure ✅ DONE

- **Goal:** Merge two parallel agentic systems (System A: `.claude/`, System B: `.github/.github/`) into ONE unified cross-platform system.
- **Status:** ✅ Complete (2026-03-20)
- **Architecture Decision:** `.hailo/` as canonical shared directory (platform-neutral)
- **Key Deliverables:**
  - `.hailo/` directory with instructions (7), toolsets (5), skills (13), knowledge (8), memory (9), templates (4), examples (11)
  - 7 Claude Code slash commands (`/hl-build-app`, `/hl-build-vlm-app`, `/hl-build-standalone-app`, `/hl-build-agent-app`, `/hl-add-voice`, `/hl-profile`, `/hl-contribute`)
  - 6 reference skills (monitoring, event-detection, camera, model-management, plan-and-execute, validate)
  - Platform entry points: `.cursor/rules`, `.github/copilot-instructions.md`, `.github/prompts/hl-*.prompt.md`
  - Thin `CLAUDE.md` at repo root pointing to `.hailo/`
- **Success Criteria:** ✅ All met
  - All `.hailo/` references resolve to real files
  - No orphan refs to old paths (`.claude/skills/app-builder`, `.github/.github`)
  - Skills load correctly via Claude Code slash commands
  - Copilot and Cursor entry points reference `.hailo/`

---

## Phase 3: Port Community Apps & Gesture Detection

- **Goal:** Copy the 20+ community apps from hailo-apps-infra and create a gesture detection community example.
- **Status:** Not started
- **Key Deliverables:** community/apps/ with 23 apps, gesture_detection_example, community/contributions/
- **Success Criteria:** All apps compile, imports work

---

## Phase 5: Testing & Documentation

- **Goal:** Validate everything end-to-end. Update documentation.
- **Status:** Not started
- **Key Deliverables:** Install test, import test, skill path test, app test, updated README/tests
- **Success Criteria:** install.sh completes, tests pass, community app runs, skill paths resolve

---

## Execution Order

```
Phase 1 (foundation) → Phase 3 (community apps) → Phase 5 (testing)

Phase 2+4 (agentic infrastructure) ✅ DONE — completed independently
```
