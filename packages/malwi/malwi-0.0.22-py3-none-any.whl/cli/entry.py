import os
import sys
import argparse
import shutil

from tqdm import tqdm
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed


from research.malwi_object import (
    MalwiObject,
    MalwiReport,
)
from research.predict_distilbert import get_model_version_string
from common.messaging import (
    configure_messaging,
    banner,
    model_warning,
    path_error,
    info,
    result,
)
from malwi._version import __version__
from common.config import SUPPORTED_EXTENSIONS


def copy_malicious_file(file_path: Path, base_input_path: Path, move_dir: Path) -> None:
    """
    Copy a malicious file to the move directory while preserving folder structure.

    Args:
        file_path: Path to the malicious file to copy
        base_input_path: Base input path that was scanned (to calculate relative path)
        move_dir: Directory to copy files to
    """
    try:
        # Calculate relative path from the base input path
        if base_input_path.is_file():
            # If scanning a single file, just use the filename
            relative_path = file_path.name
        else:
            # If scanning a directory, preserve the folder structure
            relative_path = file_path.relative_to(base_input_path)

        # Create the destination path
        dest_path = move_dir / relative_path

        # Create parent directories if they don't exist
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy the file
        shutil.copy2(file_path, dest_path)

    except Exception as e:
        # Don't fail the scan if copying fails, just log it
        print(f"Warning: Failed to copy {file_path}: {e}", file=sys.stderr)


def create_real_time_findings_display(silent: bool = False):
    """Create a callback function for real-time malicious findings display."""
    if silent:
        return None, None

    # Keep track of findings count and whether we've displayed before
    findings_state = {"count": 0, "lines_displayed": 0}

    def display_malicious_finding(file_path: Path, malicious_objects):
        """Display malicious findings in real-time using demo-like format."""
        # Clear previous lines if any
        if findings_state["lines_displayed"] > 0:
            # Move cursor up and clear lines
            for _ in range(findings_state["lines_displayed"]):
                tqdm.write("\033[1A\033[2K", file=sys.stderr, end="")

        # Increment counter
        findings_state["count"] += 1

        # Display count header
        count_display = f"- 👹 suspicious files: {findings_state['count']}"
        tqdm.write(count_display, file=sys.stderr)

        # Display latest finding with first object name
        lines_written = 1
        if malicious_objects:
            obj_display = f"     └── {file_path}, {malicious_objects[0].name}"
            tqdm.write(obj_display, file=sys.stderr)
            lines_written = 2

        # Update lines displayed count
        findings_state["lines_displayed"] = lines_written

        # Force flush to ensure immediate display
        sys.stderr.flush()

    def cleanup_display():
        """Clear the real-time display after scan completes."""
        if findings_state["lines_displayed"] > 0:
            # Move cursor up and clear lines
            for _ in range(findings_state["lines_displayed"]):
                tqdm.write("\033[1A\033[2K", file=sys.stderr, end="")
            sys.stderr.flush()

    return display_malicious_finding, cleanup_display


def run_batch_scan(child_folder: Path, args) -> dict:
    """Run a single scan on a child folder and return results."""
    # Check if output file already exists
    format_ext = {
        "demo": ".txt",
        "markdown": ".md",
        "json": ".json",
        "yaml": ".yaml",
        "tokens": ".txt",
        "code": ".txt",
    }
    extension = format_ext.get(args.format, ".txt")
    output_file = Path.cwd() / f"malwi_{child_folder.name}{extension}"

    if output_file.exists():
        return {"folder": child_folder.name, "success": True, "skipped": True}

    try:
        report: MalwiReport = MalwiReport.create(
            input_path=child_folder,
            accepted_extensions=args.extensions,
            predict=True,
            silent=True,  # Silent for individual folder processing in batch mode
            malicious_threshold=args.threshold,
        )

        # Generate output based on format
        if args.format == "yaml":
            output = report.to_report_yaml()
        elif args.format == "json":
            output = report.to_report_json()
        elif args.format == "markdown":
            output = report.to_report_markdown()
        elif args.format == "tokens":
            output = report.to_tokens_text()
        elif args.format == "code":
            output = report.to_code_text()
        else:
            output = report.to_demo_text()

        # Save the output
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(output, encoding="utf-8")

        return {"folder": child_folder.name, "success": True, "skipped": False}

    except Exception as e:
        return {
            "folder": child_folder.name,
            "success": False,
            "error": str(e),
            "skipped": False,
        }


def process_batch_mode(input_path: Path, args) -> None:
    """Process multiple child folders in batch mode."""
    if not input_path.is_dir():
        path_error("Batch mode requires a directory path")
        return

    # Get all child directories
    child_folders = [p for p in input_path.iterdir() if p.is_dir()]

    if not child_folders:
        info("No child directories found for batch processing")
        return

    # Load ML models once for batch processing
    try:
        MalwiObject.load_models_into_memory(
            distilbert_model_path=args.model_path,
            tokenizer_path=args.tokenizer_path,
        )
    except Exception as e:
        model_warning("ML", e)

    info(f"🚀 Starting batch scan of {len(child_folders)} folders")

    # Use ThreadPoolExecutor for parallel processing (shares memory space for models)
    max_workers = min(4, len(child_folders))  # Restore parallel processing

    failed = 0
    skipped = 0
    failed_folders = []

    # Create progress bar (disable if quiet mode)
    with tqdm(
        total=len(child_folders),
        desc="📈 Scanning folders",
        unit="folder",
        disable=args.quiet,
    ) as pbar:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            try:
                # Submit all jobs
                future_to_folder = {
                    executor.submit(run_batch_scan, folder, args): folder
                    for folder in child_folders
                }

                # Process completed jobs
                for future in as_completed(future_to_folder):
                    folder = future_to_folder[future]
                    try:
                        batch_result = future.result()

                        if batch_result.get("skipped", False):
                            skipped += 1
                            pbar.set_postfix_str(f"⏭️ {batch_result['folder']}")
                        elif batch_result["success"]:
                            pbar.set_postfix_str(f"✅ {batch_result['folder']}")
                        else:
                            failed += 1
                            error_msg = batch_result.get("error", "Unknown error")
                            failed_folders.append(
                                f"{batch_result['folder']}: {error_msg}"
                            )
                            pbar.set_postfix_str(f"❌ {batch_result['folder']}")

                    except Exception as e:
                        failed += 1
                        failed_folders.append(f"{folder.name}: {str(e)}")
                        pbar.set_postfix_str(f"❌ {folder.name}")

                    pbar.update(1)

            except KeyboardInterrupt:
                info("\n🛑 Interrupt received. Shutting down...")
                # Force immediate exit to avoid thread cleanup issues
                os._exit(130)

    # Summary
    processed = len(child_folders) - skipped
    success_count = processed - failed
    info(
        f"🎯 Batch scan complete: {success_count} successful, {failed} failed, {skipped} skipped"
    )

    # Show failed folders if any
    if failed_folders and not args.quiet:
        info("Failed folders:")
        for failure in failed_folders:
            info(f"  - {failure}")


def scan_command(args):
    """Execute the scan subcommand."""
    # Configure unified messaging system
    configure_messaging(quiet=args.quiet)

    banner(
        """
                  __          __
  .--------.---.-|  .--.--.--|__|
  |        |  _  |  |  |  |  |  |
  |__|__|__|___._|__|________|__|
     AI Python Malware Scanner\n\n"""
    )

    # Process files using the consolidated function
    input_path = Path(args.path)
    if not input_path.exists():
        path_error(input_path)
        return

    # Handle batch mode - run independent scans on child folders
    if args.batch:
        process_batch_mode(input_path, args)
        return

    # Load ML models (only for non-batch mode)
    try:
        MalwiObject.load_models_into_memory(
            distilbert_model_path=args.model_path,
            tokenizer_path=args.tokenizer_path,
        )
    except Exception as e:
        model_warning("ML", e)

    # Create callbacks for real-time display and file copying
    real_time_callback = None
    cleanup_callback = None
    file_copy_callback = None

    # Set up move directory if specified
    move_dir = None
    if args.move:
        move_dir = Path(args.move)
        move_dir.mkdir(parents=True, exist_ok=True)

        def file_copy_callback(file_path: Path, malicious_objects):
            copy_malicious_file(file_path, input_path, move_dir)

    # Enable real-time display for directories when not in quiet mode and not disabled
    if input_path.is_dir() and not args.quiet and not args.no_realtime:
        real_time_callback, cleanup_callback = create_real_time_findings_display(
            silent=args.quiet
        )

    # Combine callbacks if both exist
    combined_callback = None
    if real_time_callback and file_copy_callback:

        def combined_callback(file_path: Path, malicious_objects):
            real_time_callback(file_path, malicious_objects)
            file_copy_callback(file_path, malicious_objects)
    elif real_time_callback:
        combined_callback = real_time_callback
    elif file_copy_callback:
        combined_callback = file_copy_callback

    report: MalwiReport = MalwiReport.create(
        input_path=input_path,
        accepted_extensions=args.extensions,
        predict=True,  # Enable prediction for malwi scanner
        silent=args.quiet,
        malicious_threshold=args.threshold,
        on_malicious_found=combined_callback,
    )

    # Clean up the real-time display
    if cleanup_callback:
        cleanup_callback()

    output = ""

    if args.format == "yaml":
        output = report.to_report_yaml()
    elif args.format == "json":
        output = report.to_report_json()
    elif args.format == "markdown":
        output = report.to_report_markdown()
    elif args.format == "tokens":
        output = report.to_tokens_text()
    elif args.format == "code":
        output = report.to_code_text()
    else:
        output = report.to_demo_text()

    if args.save:
        save_path = Path(args.save)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(output, encoding="utf-8")
        info(f"Output saved to {args.save}")
    else:
        # Ensure all streams are flushed before final output
        import sys

        sys.stdout.flush()
        sys.stderr.flush()

        # Use result() for consistent output handling
        result(output, force=True)


def pypi_command(args):
    """Execute the pypi subcommand."""
    # Configure unified messaging system
    configure_messaging(quiet=args.quiet)

    banner(
        """
                  __          __
  .--------.---.-|  .--.--.--|__|
  |        |  _  |  |  |  |  |  |
  |__|__|__|___._|__|________|__|
     AI Python Malware Scanner\n\n"""
    )

    # Import PyPI scanner
    from research.pypi import scan_pypi_package

    # Use specified download folder
    download_path = Path(args.folder)

    # Download and extract the package
    temp_dir, extracted_dirs = scan_pypi_package(
        args.package, args.version, download_path, show_progress=not args.quiet
    )

    if not extracted_dirs:
        from common.messaging import error

        error("Failed to download or extract package")
        return

    # Load ML models for scanning
    try:
        MalwiObject.load_models_into_memory(
            distilbert_model_path=args.model_path,
            tokenizer_path=args.tokenizer_path,
        )
    except Exception as e:
        model_warning("ML", e)

    # Set up move directory if specified
    move_dir = None
    file_copy_callback = None
    if args.move:
        move_dir = Path(args.move)
        move_dir.mkdir(parents=True, exist_ok=True)

    # Scan each extracted directory
    all_reports = []
    for extracted_dir in extracted_dirs:
        # Create file copy callback for this extracted directory
        if move_dir:

            def file_copy_callback(file_path: Path, malicious_objects):
                copy_malicious_file(file_path, extracted_dir, move_dir)

        report: MalwiReport = MalwiReport.create(
            input_path=extracted_dir,
            accepted_extensions=[".py"],  # Focus on Python files for PyPI packages
            predict=True,
            silent=args.quiet,
            malicious_threshold=args.threshold,
            on_malicious_found=file_copy_callback,
        )
        all_reports.append(report)

    # Combine reports and show results
    if all_reports:
        # For now, use the first report (could be enhanced to merge multiple)
        main_report = all_reports[0]

        # Generate output based on format
        if args.format == "yaml":
            output = main_report.to_report_yaml()
        elif args.format == "json":
            output = main_report.to_report_json()
        elif args.format == "markdown":
            output = main_report.to_report_markdown()
        elif args.format == "tokens":
            output = main_report.to_tokens_text()
        elif args.format == "code":
            output = main_report.to_code_text()
        else:
            output = main_report.to_demo_text()

        if args.save:
            save_path = Path(args.save)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.write_text(output, encoding="utf-8")
            if not args.quiet:
                info(f"Output saved to {args.save}")
        else:
            result(output, force=True)

    else:
        info("No files were processed")


def main():
    parser = argparse.ArgumentParser(description="malwi - AI Python Malware Scanner")
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=get_model_version_string(__version__),
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scan subcommand (existing functionality)
    scan_parser = subparsers.add_parser("scan", help="Scan local files or directories")
    scan_parser.add_argument(
        "path", metavar="PATH", help="Specify the package file or folder path."
    )
    scan_parser.add_argument(
        "--format",
        "-f",
        choices=["demo", "markdown", "json", "yaml", "tokens", "code"],
        default="demo",
        help="Specify the output format.",
    )
    # Create mutually exclusive group for batch and save modes
    output_group = scan_parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "--save",
        "-s",
        metavar="FILE",
        help="Specify a file path to save the output.",
        default=None,
    )
    output_group.add_argument(
        "--batch",
        action="store_true",
        help="Run independent scans on each child folder and save results to current directory as malwi_<foldername>.<format>.",
    )
    scan_parser.add_argument(
        "--threshold",
        "-mt",
        metavar="FLOAT",
        type=float,
        default=0.7,
        help="Specify the threshold for classifying code objects as malicious (default: 0.7).",
    )
    scan_parser.add_argument(
        "--extensions",
        "-e",
        nargs="+",
        default=SUPPORTED_EXTENSIONS,
        help=f"Specify file extensions to process (default: {', '.join(SUPPORTED_EXTENSIONS)}).",
    )
    scan_parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress logging output and progress bar.",
    )
    scan_parser.add_argument(
        "--no-realtime",
        action="store_true",
        help="Disable real-time display of malicious findings during large scans.",
    )
    scan_parser.add_argument(
        "--move",
        nargs="?",
        const="findings",
        metavar="DIR",
        default=None,
        help="Copy files with malicious findings to the specified directory, preserving folder structure (default: findings).",
    )

    developer_group = scan_parser.add_argument_group("Developer Options")
    developer_group.add_argument(
        "--tokenizer-path",
        "-t",
        metavar="PATH",
        help="Specify the tokenizer path",
        default=None,
    )
    developer_group.add_argument(
        "--model-path",
        "-m",
        metavar="PATH",
        help="Specify the DistilBert model path",
        default=None,
    )

    # PyPI subcommand (new functionality)
    pypi_parser = subparsers.add_parser("pypi", help="Scan PyPI packages")
    pypi_parser.add_argument("package", help="PyPI package name to scan")
    pypi_parser.add_argument(
        "version",
        nargs="?",
        default=None,
        help="Package version (optional, defaults to latest)",
    )
    pypi_parser.add_argument(
        "--folder",
        "-d",
        metavar="FOLDER",
        default="downloads",
        help="Folder to download packages to (default: downloads)",
    )
    pypi_parser.add_argument(
        "--format",
        "-f",
        choices=["demo", "markdown", "json", "yaml", "tokens", "code"],
        default="demo",
        help="Specify the output format.",
    )
    pypi_parser.add_argument(
        "--threshold",
        "-mt",
        metavar="FLOAT",
        type=float,
        default=0.7,
        help="Specify the threshold for classifying code objects as malicious (default: 0.7).",
    )
    pypi_parser.add_argument(
        "--save",
        "-s",
        metavar="FILE",
        help="Specify a file path to save the output.",
        default=None,
    )
    pypi_parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress logging output.",
    )
    pypi_parser.add_argument(
        "--move",
        nargs="?",
        const="findings",
        metavar="DIR",
        default=None,
        help="Copy files with malicious findings to the specified directory, preserving folder structure (default: findings).",
    )

    pypi_developer_group = pypi_parser.add_argument_group("Developer Options")
    pypi_developer_group.add_argument(
        "--tokenizer-path",
        "-t",
        metavar="PATH",
        help="Specify the tokenizer path",
        default=None,
    )
    pypi_developer_group.add_argument(
        "--model-path",
        "-m",
        metavar="PATH",
        help="Specify the DistilBert model path",
        default=None,
    )

    args = parser.parse_args()

    # If no command is specified, show help
    if not args.command:
        parser.print_help()
        return

    # Route to appropriate command handler
    if args.command == "scan":
        scan_command(args)
    elif args.command == "pypi":
        pypi_command(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        result("👋", force=True)
        os._exit(130)
