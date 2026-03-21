
![Banner](doc/images/hailo_rpi_examples_banner.png)

# Hailo Community Projects

The central hub for Hailo community development — community-contributed AI applications and **agentic AI development tooling** for Hailo edge accelerators.

Built on top of [hailo-apps-infra](https://github.com/hailo-ai/hailo-apps-infra) (included as a git submodule), this repo provides 20+ ready-to-run community apps, a growing knowledge base of real-world optimizations, and an AI-powered development framework that lets you build production-ready Hailo apps through natural language.

Supports **Hailo-8** (26 TOPS), **Hailo-8L** (13 TOPS), and **Hailo-10H** (GenAI: LLM, VLM, Whisper + vision pipelines).

Visit the [Hailo Official Website](https://hailo.ai/) and [Hailo Community Forum](https://community.hailo.ai/) for more information.

## Repository Structure

```
hailo-community-projects/
├── hailo-apps-infra/              # Git submodule — core framework & official apps
├── community/
│   ├── apps/
│   │   ├── pipeline_apps/         # 14 GStreamer real-time video community apps
│   │   ├── standalone_apps/       # 5 lightweight HailoRT-only batch apps
│   │   └── gen_ai_apps/           # 2 Hailo-10H GenAI community apps
│   └── contributions/             # Community-shared optimization insights
├── community_projects/            # Legacy community projects (games, robots, etc.)
├── .hailo/                        # Shared agentic knowledge (cross-platform)
├── install.sh                     # Thin wrapper → hailo-apps-infra/install.sh
└── setup_env.sh                   # Activates venv and sets PYTHONPATH
```

See the [Hailo Apps Infra documentation](https://github.com/hailo-ai/hailo-apps-infra) for the full development guide and API reference.

## Hardware Setup

For instructions on setting up Hailo hardware and software on the Raspberry Pi 5, see the [Hailo Raspberry Pi 5 installation guide](doc/install-raspberry-pi5.md#how-to-set-up-raspberry-pi-5-and-hailo).

## Installation

### Clone the Repository
```bash
git clone --recurse-submodules https://github.com/hailo-ai/hailo-community-projects.git
cd hailo-community-projects
```

If you already cloned without `--recurse-submodules`, initialize the submodule manually:
```bash
git submodule update --init --recursive
```

### Run the Installer
The install script initializes the hailo-apps-infra submodule, runs its installer, creates a virtual environment symlink, and installs community-specific dependencies:
```bash
./install.sh
```

### Set Up the Environment
When opening a new terminal session, source the environment setup script. This activates the `venv_hailo_apps` virtual environment and sets `PYTHONPATH` for both the project root and hailo-apps-infra:
```bash
source setup_env.sh
```

## Official Pipeline Apps

The official apps (detection, pose estimation, segmentation, depth, etc.) are provided by the [hailo-apps-infra](https://github.com/hailo-ai/hailo-apps-infra) submodule. Run them via CLI commands after sourcing the environment:

```bash
source setup_env.sh

# Object detection
hailo-detect --input usb

# Pose estimation
hailo-pose --input usb

# Instance segmentation
hailo-seg --input usb

# Depth estimation
hailo-depth --input usb
```

For all options: `hailo-detect --help`

See the [Hailo Apps Infra documentation](https://github.com/hailo-ai/hailo-apps-infra) for the full list of official apps and their usage.

## Community Apps

Community apps are organized into three categories under `community/apps/`:

- **Pipeline Apps** (14) — GStreamer real-time video apps (detection, tracking, pose analysis, multi-camera, etc.)
- **Standalone Apps** (5) — Lightweight HailoRT-only batch processing apps
- **GenAI Apps** (2) — Hailo-10H generative AI apps (VLM, voice)

```bash
# Pipeline app
python community/apps/pipeline_apps/<app_name>/<app_name>.py --input usb

# Standalone app
python community/apps/standalone_apps/<app_name>/<app_name>.py --input path/to/video.mp4

# GenAI app (Hailo-10H only)
python community/apps/gen_ai_apps/<app_name>/<app_name>.py
```

See the [Community Apps README](community/apps/README.md) for the full list of available apps.

## Legacy Community Projects

Community-contributed projects from previous versions remain in `community_projects/` — including games, robots, and creative demos.
Check out the [Community Projects](community_projects/community_projects.md) page for details.

## Agentic AI Development

This repository is designed for **agentic-first development**. AI coding agents can build complete, production-ready Hailo AI applications by following structured instructions, knowledge bases, and skill definitions — without manually writing code.

### How It Works

All shared agentic knowledge lives in `.hailo/` — a platform-neutral directory that works with any AI coding agent:

| Component | Location | Description |
|-----------|----------|-------------|
| **Skills** | `.hailo/skills/` | 13 step-by-step workflow guides (hl- prefix) |
| **Instructions** | `.hailo/instructions/` | Architecture, coding standards, orchestration |
| **Toolsets** | `.hailo/toolsets/` | API references for Hailo SDK, GStreamer, VLM |
| **Knowledge** | `.hailo/knowledge/` | App catalog, decision tree, code snippets, troubleshooting |
| **Memory** | `.hailo/memory/` | Persistent cross-session knowledge from real sessions |
| **Templates** | `.hailo/templates/` | Scaffold templates for pipeline, standalone, GenAI apps |
| **Examples** | `.hailo/examples/` | Minimal runnable examples and callback patterns |

See the [.hailo/ README](.hailo/README.md) for the complete index.

### Supported Platforms

| Platform | Entry Point | Skills Available |
|----------|-------------|-----------------|
| **Claude Code** | `CLAUDE.md` + `.claude/skills/hl-*/SKILL.md` | 7 slash commands (`/hl-build-app`, `/hl-profile`, etc.) |
| **VS Code Copilot** | `.github/copilot-instructions.md` + `.github/prompts/hl-*.prompt.md` | 6 ready-to-use prompt templates |
| **Cursor** | `.cursor/rules` | Full access to `.hailo/` knowledge |
| **Any AI agent** | `.hailo/` directory | Read skills, instructions, and knowledge directly |

### Available Skills

| Skill | Description |
|-------|-------------|
| `hl-build-app` | Build new Hailo AI apps (main builder with 7-phase workflow) |
| `hl-build-vlm-app` | Build Vision-Language Model apps for Hailo-10H |
| `hl-build-standalone-app` | Build standalone HailoRT inference apps |
| `hl-build-agent-app` | Build AI agent apps with tool calling |
| `hl-add-voice` | Add speech-to-text / text-to-speech to any app |
| `hl-profile` | Profile GStreamer pipeline performance with GST-Shark |
| `hl-contribute` | Share optimization insights with the community |
| `hl-monitoring` | Continuous video monitoring pattern |
| `hl-event-detection` | Event detection from VLM responses |
| `hl-camera` | Camera setup and management |
| `hl-model-management` | HEF model management and resolution |
| `hl-plan-and-execute` | Orchestrated multi-phase workflow |
| `hl-validate` | Validation and testing patterns |

### Community Knowledge Base

The `community/contributions/` directory contains real-world optimization insights shared by community members and AI agents. Each contribution is a structured Markdown file documenting a finding, its root cause, and the fix — with before/after metrics.

See the [Contributions README](community/contributions/README.md) for how to contribute your own insights.

## Additional Examples and Resources

### CLIP Application

CLIP (Contrastive Language-Image Pre-training) predicts the most relevant text prompt on real-time video frames using the Hailo AI processor.
See the [hailo-CLIP Repository](https://github.com/hailo-ai/hailo-CLIP) for more information.

[![Watch the demo on YouTube](https://img.youtube.com/vi/XXizBHtCLew/0.jpg)](https://youtu.be/XXizBHtCLew)

### Frigate Integration

Hailo is officially integrated into Frigate starting from version 0.16.0.
See [Hailo Official Integration with Frigate](https://community.hailo.ai/t/hailo-official-integration-with-frigate/13679) for more information.

### Raspberry Pi Official Examples

#### rpicam-apps
Raspberry Pi [rpicam-apps](https://www.raspberrypi.com/documentation/computers/camera_software.html#rpicam-apps) Hailo post-processing examples.
Documentation: [Raspberry Pi AI documentation](https://www.raspberrypi.com/documentation/computers/ai.html).

#### picamera2
Raspberry Pi [picamera2](https://github.com/raspberrypi/picamera2) provides an easy-to-use Python API for the camera stack.

### Hailo Python API
For Python inference examples, see the [Python code examples](https://github.com/hailo-ai/Hailo-Application-Code-Examples/tree/main/runtime/python).
Visit the [HailoRT Python API documentation](https://hailo.ai/developer-zone/documentation/hailort-v4-18-0/?page=api%2Fpython_api.html#module-hailo_platform.drivers) for the full API reference.

### Hailo Dataflow Compiler (DFC)
The DFC compiles neural networks to run on Hailo-8/8L processors. Download from the [Hailo Developer Zone](https://hailo.ai/developer-zone/software-downloads/).
For training and deployment, see the [Hailo Model Zoo](https://github.com/hailo-ai/hailo_model_zoo) and the [Retraining Example](https://github.com/hailo-ai/hailo-apps-infra/blob/main/doc/developer_guide/retraining_example.md).

## Contributing

We welcome contributions from the community! There are several ways to get involved:

### Build Apps with AI Agents
Use the agentic development tools to build new Hailo apps:
- **Claude Code:** Run `/hl-build-app` to start the guided app builder
- **VS Code Copilot:** Use the prompt templates in `.github/prompts/`
- **Any agent:** Follow the skill docs in `.hailo/skills/`

New apps are scaffolded in `community/apps/` automatically.

### Share Optimization Insights
After profiling or optimizing a pipeline, share your findings:
- **Claude Code:** Run `/hl-contribute` to format and submit
- **Manual:** Follow the [contribution format](community/contributions/README.md)

### Other Ways to Contribute
1. Build and share [Community Apps](community/apps/README.md)
2. Contribute to [Legacy Community Projects](community_projects/community_projects.md)
3. Report issues and bugs
4. Suggest new features or improvements
5. Join the discussion on the [Hailo Community Forum](https://community.hailo.ai/)

## Hardware

| Architecture | Value | Use Case |
|---|---|---|
| Hailo-8 | `hailo8` (26 TOPS) | Full performance, all pipeline + standalone apps |
| Hailo-8L | `hailo8l` (13 TOPS) | Lower power, compatible model subset |
| Hailo-10H | `hailo10h` | GenAI (LLM, VLM, Whisper) + vision pipelines |

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Disclaimer

This code example is provided by Hailo solely on an "AS IS" basis and "with all faults." No responsibility or liability is accepted or shall be imposed upon Hailo regarding the accuracy, merchantability, completeness, or suitability of the code example. Hailo shall not have any liability or responsibility for errors or omissions in, or any business decisions made by you in reliance on this code example or any part of it. If an error occurs when running this example, please open a ticket in the "Issues" tab.
