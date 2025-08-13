import os
from typing import List, Dict, Any
from datetime import datetime


def _resolve_cross_step_references(app, step_num: int, params: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve references for file parameters only (avoid resolving non-file params like 'replace')."""
    resolved: Dict[str, Any] = {}
    file_like_keys = {"video_file", "audio_file", "output_file"}

    for key, value in params.items():
        # Resolve list of files for merge operations
        if key == "video_files" and isinstance(value, list):
            new_list = []
            for item in value:
                if isinstance(item, str):
                    file_path = app.resolve_file_reference(item, "video")
                    new_list.append(file_path if file_path else item)
                else:
                    new_list.append(item)
            resolved[key] = new_list
            continue

        # Resolve only explicit file fields
        if key in file_like_keys and isinstance(value, str):
            preferred_type = "audio" if key == "audio_file" else ("video" if key in ["video_file", "output_file"] else None)
            file_path = app.resolve_file_reference(value, preferred_type)
            resolved[key] = file_path if file_path else value
            continue

        # Leave all other params as-is
        resolved[key] = value

    return resolved


def _execute_step(app, step_num: int, intent: str, params: Dict[str, Any]) -> str:
    """Execute a single step by routing to the corresponding app method.
    Records the step output if the invoked method creates a file and app.update_step_output is called therein.
    """
    # Mark current step for downstream methods to know where to store outputs
    app._current_step_num = step_num
    try:
        if intent == "extract_audio_segment":
            return app.execute_extract_audio_segment(
                params.get("video_file"),
                params.get("start_time"),
                params.get("end_time"),
                params.get("audio_format"),
                params.get("quality")
            )
        if intent == "replace_audio":
            return app.execute_replace_audio(
                params.get("video_file"),
                params.get("audio_file"),
                params.get("audio_handling"),
                params.get("audio_codec")
            )
        if intent == "simple_trim":
            return app.execute_trim(
                params.get("video_file"),
                params.get("start_time"),
                params.get("end_time")
            )
        if intent == "extract_audio":
            return app.execute_extract_audio(
                params.get("video_file"),
                params.get("audio_format"),
                params.get("quality")
            )
        if intent == "merge_videos":
            return app.execute_merge_videos(
                params.get("video_files", []),
                params.get("merge_method")
            )
        if intent == "convert_video":
            return app.execute_convert_video(
                params.get("video_file"),
                params.get("target_format"),
                params.get("quality")
            )
        if intent == "simple_resize":
            return app.execute_resize(
                params.get("video_file"),
                params.get("resolution")
            )
        if intent == "compress_video":
            return app.execute_compress_video(
                params.get("video_file"),
                params.get("compression_level")
            )
        if intent == "rotate_video":
            return app.execute_rotate_video(
                params.get("video_file"),
                params.get("rotation")
            )
        if intent == "split_video":
            return app.execute_split_video(
                params.get("video_file"),
                params.get("split_method"),
                params.get("split_value")
            )
        if intent == "video_info":
            return app.execute_video_info(params.get("video_file"))
        if intent == "list_videos":
            return app.execute_list_videos()
        return f"Unknown step operation: {intent}"
    finally:
        # Remove marker once step completes
        try:
            del app._current_step_num
        except Exception:
            pass


def run_multi_step(app, multi_steps: List[Dict[str, Any]]) -> str:
    """Run up to app.max_multi_steps steps in sequence with robust reference resolution."""
    if not multi_steps:
        return "No multi-step operations found"

    # Clip to maximum allowed steps
    steps = multi_steps[: max(1, getattr(app, 'max_multi_steps', 20))]
    print(f"[*] Executing {len(steps)}-step workflow:")

    # Track files created during this multi-step session for cleanup
    # Use snapshot-based tracking instead of timestamps to avoid date math issues
    files_created_during_session = []
    created_seen = set()
    created_before = set()
    try:
        for fi in app.recent_files.get("created", []):
            path = fi.get("path")
            if path:
                created_before.add(path)
    except Exception:
        pass

    results: List[str] = []
    for step in steps:
        step_num = int(step.get("step", len(results) + 1))
        intent = step.get("intent")
        raw_params = step.get("parameters", {})

        # Resolve references for steps after the first
        params = _resolve_cross_step_references(app, step_num, raw_params) if step_num > 1 else raw_params

        print(f"\n[*] Step {step_num}: {intent}")
        result = _execute_step(app, step_num, intent, params)
        results.append(f"Step {step_num}: {result}")
        print(f"[+] Step {step_num} completed: {result}")

        # If an output was produced, store a generic stepX_output alias
        try:
            if step_num in app._step_outputs:
                # already recorded by called method
                pass
            else:
                # As a fallback, try to infer the newest created file
                if app.recent_files.get("created"):
                    app.update_step_output(step_num, app.recent_files["created"][0]["path"])
        except Exception:
            pass

        # Collect files created so far in this session (snapshot-based)
        try:
            for file_info in app.recent_files.get("created", []):
                path = file_info.get("path")
                if not path:
                    continue
                if path in created_before:
                    continue
                if path in created_seen:
                    continue
                files_created_during_session.append(path)
                created_seen.add(path)
        except Exception:
            pass

    print(f"\n[+] Multi-step workflow completed! ({len(steps)} steps)")
    
    # Offer cleanup of intermediate files
    if files_created_during_session and len(files_created_during_session) > 1:
        print(f"\n[*] Multi-step workflow created {len(files_created_during_session)} files:")
        for i, file_path in enumerate(files_created_during_session, 1):
            try:
                size = os.path.getsize(file_path) / (1024*1024)  # MB
                print(f"  {i}. {os.path.basename(file_path)} ({size:.1f}MB)")
            except:
                print(f"  {i}. {os.path.basename(file_path)}")
        
        try:
            # Respect auto-clean setting if available
            auto_clean = getattr(app, 'auto_cleanup_intermediate', False)
            cleanup_choice = 'y' if auto_clean else input("\n> Clean up intermediate files? (y/n): ").strip().lower()
            if cleanup_choice in ['y', 'yes']:
                cleaned_count = 0
                # Determine the final output to keep
                final_output = None
                try:
                    if hasattr(app, '_step_outputs') and app._step_outputs:
                        final_output = app._step_outputs.get(max(app._step_outputs.keys()))
                except Exception:
                    final_output = None

                # Keep only the final output file (explicit if available, else last created)
                if final_output and final_output in files_created_during_session:
                    files_to_delete = [p for p in files_created_during_session if p != final_output]
                    kept_name = os.path.basename(final_output)
                else:
                    files_to_delete = files_created_during_session[:-1]
                    kept_name = os.path.basename(files_created_during_session[-1])
                
                for file_path in files_to_delete:
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            print(f"[+] Cleaned up: {os.path.basename(file_path)}")
                            cleaned_count += 1
                    except Exception as e:
                        print(f"[!] Could not delete {os.path.basename(file_path)}: {e}")
                
                if cleaned_count > 0:
                    print(f"[+] Cleaned up {cleaned_count} intermediate files")
                    print(f"[+] Kept final output: {kept_name}")
                else:
                    print("[*] No files were cleaned up")
            else:
                print("[*] Keeping all files")
        except KeyboardInterrupt:
            print("\n[*] Cleanup cancelled")
        except Exception as e:
            print(f"[!] Error during cleanup: {e}")
    
    return "; ".join(results)


