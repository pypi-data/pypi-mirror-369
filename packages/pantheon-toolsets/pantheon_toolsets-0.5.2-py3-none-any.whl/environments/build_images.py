#!/usr/bin/env python3
"""
Docker image build automation script with automatic Dockerfile detection
"""
import argparse
import subprocess
import sys
import platform
from pathlib import Path

DOCKER_DIR = Path(__file__).parent.resolve()
PROJECT_DIR = DOCKER_DIR.parent.resolve()


def detect_dockerfiles() -> dict:
    """Detect available Dockerfiles in the directory"""
    configs = {}

    # Find all Dockerfiles in the current directory
    for dockerfile in DOCKER_DIR.glob("*.Dockerfile"):
        image_name = dockerfile.stem  # Remove .Dockerfile extension
        configs[image_name] = {
            "file": dockerfile.name,
        }

    return configs


def build_image(target: str, configs: dict, registry: str | None = None, push: bool = False):
    """Build specified Docker image and optionally push it"""
    if target not in configs:
        print(f"Error: Invalid target '{target}'\nAvailable targets: {', '.join(configs.keys())}")
        sys.exit(1)

    config = configs[target]
    # Construct the image tag
    image_tag = target
    if registry:
        # Ensure image names are lowercase for GHCR
        image_tag = f"{registry}/{target.lower()}:latest"
    
    cmd_build = [
        "docker", "buildx", "build",
        "-t", image_tag,
        "-f", str(DOCKER_DIR / config["file"]),
        str(PROJECT_DIR)
    ]

    # Auto-detect macOS and force amd64 build
    if platform.system() == "Darwin" and not push: # Only force platform if not pushing, as push implies linux/amd64 from runner
        print("Detected macOS: Forcing build for linux/amd64 (x86_64)")
        cmd_build += ["--platform", "linux/amd64", "--load"]
    elif push:
        # Ensure the image is built for linux/amd64 for registry compatibility, and enable pushing
        cmd_build += ["--platform", "linux/amd64", "--push"]


    print(f"Building {image_tag}...")
    try:
        print(" ".join(cmd_build))
        subprocess.run(cmd_build, check=True)
        print(f"Successfully built {image_tag}")

        # if push: # This is handled by buildx --push now
        #     cmd_push = ["docker", "push", image_tag]
        #     print(f"Pushing {image_tag}...")
        #     subprocess.run(cmd_push, check=True)
        #     print(f"Successfully pushed {image_tag}")

    except subprocess.CalledProcessError as e:
        print(f"Operation failed for {image_tag} (exit code {e.returncode})")
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)


def list_configs(configs: dict):
    """Display detected Docker configurations"""
    if not configs:
        print("No Dockerfiles found in directory")
        return

    print("Available Docker images:")
    for target in configs.keys():
        print(f"  {target.ljust(20)}")


def main():
    configs = detect_dockerfiles()

    parser = argparse.ArgumentParser(
        description="Docker image build automation",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="Build all detected images"
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="List available Docker configurations"
    )
    parser.add_argument(
        "-b", "--build",
        metavar="TARGET",
        help="Build specific image by target name"
    )
    parser.add_argument(
        "--registry",
        metavar="REGISTRY_PATH",
        help="Specify Docker registry path (e.g., ghcr.io/username)"
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Push the image(s) to the specified registry after building"
    )

    args = parser.parse_args()

    if args.list:
        list_configs(configs)
        return

    if not configs:
        print("Error: No Dockerfiles found (*.Dockerfile)")
        sys.exit(1)

    if args.all:
        for target in configs:
            build_image(target, configs, args.registry, args.push)
        return

    if args.build:
        build_image(args.build, configs, args.registry, args.push)
        return

    parser.print_help()


if __name__ == "__main__":
    main() 
