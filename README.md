
![Banner](doc/images/hailo_rpi_examples_banner.png)

# Hailo Community Projects

Welcome to the Hailo Community Projects repository. This project showcases community-contributed applications and examples demonstrating the capabilities of the Hailo AI processor on embedded devices.
The examples are designed to work with the Raspberry Pi AI Kit and AI HAT, and x86_64 Ubuntu machines supporting both the Hailo8 (26 TOPS) and Hailo8L (13 TOPS) AI processors.
Visit the [Hailo Official Website](https://hailo.ai/) and [Hailo Community Forum](https://community.hailo.ai/) for more information.

## Repository Structure

This repository uses [hailo-apps-infra](https://github.com/hailo-ai/hailo-apps-infra) as a **git submodule** providing the core framework, pipelines, and developer tools.

```
hailo-community-projects/
├── hailo-apps-infra/          # Git submodule — core framework & pipelines
├── community/
│   └── apps/
│       ├── pipeline_apps/     # GStreamer real-time video community apps
│       ├── standalone_apps/   # Lightweight HailoRT-only batch apps
│       └── gen_ai_apps/       # Hailo GenAI community apps
├── community_projects/        # Legacy community projects
├── install.sh                 # Thin wrapper — delegates to hailo-apps-infra/install.sh
└── setup_env.sh               # Activates venv and sets PYTHONPATH
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

- **Pipeline Apps** -- GStreamer real-time video applications (detection, pose, segmentation, etc.)
- **Standalone Apps** -- Lightweight HailoRT-only batch processing applications
- **GenAI Apps** -- Generative AI applications for Hailo

```bash
# Pipeline app
python community/apps/pipeline_apps/<app_name>/<app_name>.py --input usb

# Standalone app
python community/apps/standalone_apps/<app_name>/<app_name>.py --input path/to/video.mp4

# GenAI app
python community/apps/gen_ai_apps/<app_name>/<app_name>.py
```

See the [Community Apps README](community/apps/README.md) for the full list of available apps.

## Legacy Community Projects

Community-contributed projects from previous versions remain in `community_projects/`.
Check out the [Community Projects](community_projects/community_projects.md) page for details.

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

We welcome contributions from the community:
1. Build and share [Community Apps](community/apps/README.md).
2. Contribute to [Legacy Community Projects](community_projects/community_projects.md).
3. Report issues and bugs.
4. Suggest new features or improvements.
5. Join the discussion on the [Hailo Community Forum](https://community.hailo.ai/).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Disclaimer

This code example is provided by Hailo solely on an "AS IS" basis and "with all faults." No responsibility or liability is accepted or shall be imposed upon Hailo regarding the accuracy, merchantability, completeness, or suitability of the code example. Hailo shall not have any liability or responsibility for errors or omissions in, or any business decisions made by you in reliance on this code example or any part of it. If an error occurs when running this example, please open a ticket in the "Issues" tab.
