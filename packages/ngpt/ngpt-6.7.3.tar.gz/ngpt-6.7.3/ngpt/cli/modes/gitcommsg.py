import os
import re
import sys
import tempfile
import time
import subprocess
import threading
from datetime import datetime
import logging
from ngpt.ui.colors import COLORS
from ngpt.ui.tui import spinner, copy_to_clipboard
from ngpt.core.log import create_gitcommsg_logger
from ngpt.core.cli_config import get_cli_config_option
from ngpt.ui.pipe import process_piped_input

def get_diff_content(diff_file=None):
    """Get git diff content from file or git staged changes.
    
    Args:
        diff_file: Path to a diff file to use instead of git staged changes
        
    Returns:
        str: Content of the diff, or None if no diff is available
    """
    if diff_file:
        try:
            with open(diff_file, 'r') as f:
                content = f.read()
                return content
        except Exception as e:
            print(f"{COLORS['yellow']}Error reading diff file: {str(e)}{COLORS['reset']}")
            return None
            
    # No diff file specified, get staged changes from git
    try:
        result = subprocess.run(
            ["git", "diff", "--staged"], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Git command failed: {result.stderr}")
            
        # Check if there are staged changes
        if not result.stdout.strip():
            print(f"{COLORS['yellow']}No staged changes found. Stage changes with 'git add' first.{COLORS['reset']}")
            return None
            
        return result.stdout
    except Exception as e:
        print(f"{COLORS['yellow']}Error getting git diff: {str(e)}{COLORS['reset']}")
        return None

def split_into_chunks(content, chunk_size=200):
    """Split content into chunks of specified size.
    
    Args:
        content: The content to split into chunks
        chunk_size: Maximum number of lines per chunk
        
    Returns:
        list: List of content chunks
    """
    lines = content.splitlines()
    chunks = []
    
    for i in range(0, len(lines), chunk_size):
        chunk = lines[i:i+chunk_size]
        chunks.append("\n".join(chunk))
        
    return chunks

def create_technical_analysis_system_prompt(preprompt=None):
    """Create system prompt for technical analysis based on preprompt data.
    
    Args:
        preprompt: The raw preprompt string from --preprompt flag
        
    Returns:
        str: System prompt for the technical analysis stage
    """
    base_prompt = """You are an expert at analyzing git diffs and extracting precise technical details. Your task is to analyze the git diff and create a detailed technical summary of the changes.

OUTPUT FORMAT:
[FILES]: Comma-separated list of affected files with full paths

[CHANGES]: 
- Technical detail 1 (include specific function/method names and line numbers)
- Technical detail 2 (be precise about exactly what code was added/modified/removed)
- Additional technical details (include only significant functional changes in this chunk)

[IMPACT]: Brief technical description of what the changes accomplish

RULES:
1. BE 100% FACTUAL - Mention ONLY code explicitly shown in the diff
2. NEVER invent or assume changes not directly visible in the code
3. ALWAYS identify exact function names, method names, class names, and line numbers where possible
4. Use format 'filename:function_name()' or 'filename:line_number' when referencing code locations
5. Be precise and factual - only describe code that actually changed
6. Include ONLY significant functional changes - EXCLUDE:
   - Version number updates in package manifests
   - Lock file changes (any *.lock, *-lock.*, *.lock.* files)
   - Simple comment additions or documentation updates
   - Dependency version updates that don't affect functionality
   - Formatting or whitespace-only changes (unless that's the main purpose)
   - Build configuration changes that don't affect core functionality
7. Focus on technical specifics, avoid general statements
8. When analyzing multiple files, clearly separate each file's changes
9. Include proper technical details (method names, component identifiers, etc.)
10. PRIORITIZE the main functional change - if there's one primary change, focus on that
11. CRITICAL: Completely ignore any automated build system changes or dependency management updates"""

    # If preprompt is provided, prepend it to the base prompt with strong wording about absolute priority
    if preprompt:
        preprompt_section = f"""===CRITICAL USER PREPROMPT - ABSOLUTE HIGHEST PRIORITY===
The following preprompt from the user OVERRIDES ALL OTHER INSTRUCTIONS and must be followed exactly:

{preprompt}

THIS USER PREPROMPT HAS ABSOLUTE PRIORITY over any other instructions that follow. If it contradicts other instructions, the user preprompt MUST be followed. No exceptions.

"""
        return preprompt_section + base_prompt
    
    return base_prompt

def create_system_prompt(preprompt=None):
    """Create system prompt for commit message generation based on preprompt data.
    
    Args:
        preprompt: The raw preprompt string from --preprompt flag
        
    Returns:
        str: System prompt for the AI
    """
    base_prompt = """You are an expert Git commit message writer. Your task is to analyze the git diff and create a precise, factual commit message following the conventional commit format.

FORMAT:
type[(scope)]: <concise summary> (max 50 chars)

- [type] <specific change 1> (filename:function/method/line)
- [type] <specific change 2> (filename:function/method/line)
- [type] <additional changes...>

RULES FOR FILENAMES:
1. For the FIRST mention of a file, use the full relative path
2. For SUBSEQUENT mentions of the same file, use ONLY the filename without path
   - Example: First mention: "utils/helpers/format.js" → Subsequent mentions: "format.js"
3. Only include the full path again if there are multiple files with the same name
4. For repeated mentions of the same file, consider grouping related changes in one bullet
5. Avoid breaking filenames across lines
6. Only include function names when they add clarity

COMMIT TYPES:
- feat: New user-facing features
- fix: Bug fixes or error corrections
- refactor: Code restructuring (no behavior change)
- style: Formatting/whitespace changes only
- docs: Documentation only
- test: Test-related changes
- perf: Performance improvements
- build: Build system changes
- ci: CI/CD pipeline changes
- chore: Routine maintenance tasks
- revert: Reverting previous changes
- add: New files without user-facing features
- remove: Removing files/code
- update: Changes to existing functionality
- security: Security-related changes
- config: Configuration changes
- ui: User interface changes
- api: API-related changes

EXAMPLES:

1. Bug fix with UI scope:
fix(ui): correct primary button focus style

- [fix] Add :focus outline to Button component (Button.jsx:Button())
- [chore] Bump Tailwind config to include ring-offset (tailwind.config.js:1-8)
- [refactor] Extract common styles into buttonStyles util (styles/buttons.js:1-15)

2. Feature with API scope:
feat(api): add authentication endpoint for OAuth

- [feat] Implement OAuth authentication route (auth/routes.js:createOAuthRoute())
- [feat] Add token validation middleware (middleware/auth.js:validateToken())
- [test] Add integration tests for OAuth flow (tests/auth.test.js:45-87)

3. Multiple types in one commit:
refactor(core): simplify data processing pipeline

- [refactor] Replace nested loops with map/reduce (utils/process.js:transformData())
- [perf] Optimize memory usage in large dataset handling (utils/memory.js:optimize())
- [fix] Correct edge case in null value handling (utils/validators.js:checkNull())
- [test] Update tests for new pipeline structure (tests/pipeline.test.js)

4. Multiple changes to the same file:
refactor(core): simplify preprompt handling for commit prompts

- [refactor] Remove process_preprompt function (cli/modes/gitcommsg.py:69-124)
- [refactor] Update all functions to accept raw preprompt string (gitcommsg.py:create_system_prompt())
- [refactor] Replace preprompt_data usages with preprompt (gitcommsg.py)
- [docs] Update library usage doc (docs/usage/library_usage.md:516,531-537)


BULLET POINT FORMAT:
- Each bullet MUST start with a type in square brackets: [type]
- DO NOT use the format "- type: description" (without square brackets)
- Instead, ALWAYS use "- [type] description" (with square brackets)
- Example: "- [feat] Add new login component" (correct)
- Not: "- feat: Add new login component" (incorrect)

RULES:
1. BE 100% FACTUAL - Mention ONLY code explicitly shown in the diff
2. NEVER invent or assume changes not directly visible in the code
3. EVERY bullet point MUST reference specific files/functions/lines
4. Include ONLY significant functional changes - EXCLUDE:
   - Version number updates in package manifests
   - Lock file changes (any *.lock, *-lock.*, *.lock.* files)
   - Simple comment additions or documentation updates
   - Dependency version updates that don't affect functionality
   - Formatting or whitespace-only changes (unless that's the main purpose)
   - Build configuration changes that don't affect core functionality
5. If unsure about a change's purpose, describe WHAT changed, not WHY
6. Keep summary line under 50 characters (mandatory)
7. Use appropriate type tags for each change (main summary and each bullet)
8. ONLY describe code that was actually changed
9. Focus on technical specifics, avoid general statements
10. Include proper technical details (method names, component identifiers, etc.)
11. When all changes are to the same file, mention it once in the summary
12. PRIORITIZE the main functional change - if there's one primary change, focus on that
13. CRITICAL: Completely ignore any automated build system changes or dependency management updates"""

    # If preprompt is provided, prepend it with strong wording about absolute priority
    if preprompt:
        preprompt_section = f"""===CRITICAL USER PREPROMPT - ABSOLUTE HIGHEST PRIORITY===
The following preprompt from the user OVERRIDES ALL OTHER INSTRUCTIONS and must be followed exactly:

{preprompt}

THIS USER PREPROMPT HAS ABSOLUTE PRIORITY over any other instructions that follow. If it contradicts other instructions, the user preprompt MUST be followed. No exceptions.

"""
        return preprompt_section + base_prompt
    
    return base_prompt

def create_chunk_prompt(chunk):
    """Create prompt for processing a single diff chunk.
    
    Args:
        chunk: The diff chunk to process
        
    Returns:
        str: Prompt for the AI
    """
    return f"""Analyze this PARTIAL git diff and create a detailed technical summary.

The system prompt already contains your output format instructions with [FILES], [CHANGES], and [IMPACT] sections.

REMINDER: 
- Identify exact function names, method names, class names, and line numbers
- Use format 'filename:function_name()' or 'filename:line_number' for references
- Be precise and factual - only describe code that actually changed

Diff chunk:

{chunk}"""

def create_rechunk_prompt(combined_analysis, depth):
    """Create prompt for re-chunking process.
    
    Args:
        combined_analysis: The combined analysis to re-chunk
        depth: Current recursion depth
        
    Returns:
        str: Prompt for the AI
    """
    return f"""IMPORTANT: You are analyzing SUMMARIES of git changes, not raw git diff.

You are in a re-chunking process (depth: {depth}) where the input is already summarized changes.
Create a terse technical summary following the format in the system prompt.

DO NOT ask for raw git diff. These summaries are all you need to work with.
Keep your response factual and specific to what's in the summaries.

Section to summarize:

{combined_analysis}"""

def create_final_prompt(diff_content):
    """Create prompt for direct processing without chunking.
    
    Args:
        diff_content: The full diff content
        
    Returns:
        str: Prompt for the AI
    """
    return f"""Analyze ONLY the exact changes in this git diff and create a precise, factual commit message.

FORMAT:
type[(scope)]: <concise summary> (max 50 chars)

- [type] <specific change 1> (filename:function/method/line)
- [type] <specific change 2> (filename:function/method/line)
- [type] <additional changes...>

RULES FOR FILENAMES:
1. For the FIRST mention of a file, use the full relative path
2. For SUBSEQUENT mentions of the same file, use ONLY the filename without path
   - Example: First mention: "utils/helpers/format.js" → Subsequent mentions: "format.js"
3. Only include the full path again if there are multiple files with the same name
4. For repeated mentions of the same file, consider grouping related changes in one bullet
5. Avoid breaking filenames across lines
6. Only include function names when they add clarity

COMMIT TYPES:
- feat: New user-facing features
- fix: Bug fixes or error corrections
- refactor: Code restructuring (no behavior change)
- style: Formatting/whitespace changes only
- docs: Documentation only
- test: Test-related changes
- perf: Performance improvements
- build: Build system changes
- ci: CI/CD pipeline changes
- chore: Routine maintenance tasks
- revert: Reverting previous changes
- add: New files without user-facing features
- remove: Removing files/code
- update: Changes to existing functionality
- security: Security-related changes
- config: Configuration changes
- ui: User interface changes
- api: API-related changes

EXAMPLES:

1. Bug fix with UI scope:
fix(ui): correct primary button focus style

- [fix] Add :focus outline to Button component (Button.jsx:Button())
- [chore] Bump Tailwind config to include ring-offset (tailwind.config.js:1-8)
- [refactor] Extract common styles into buttonStyles util (styles/buttons.js:1-15)

2. Feature with API scope:
feat(api): add authentication endpoint for OAuth

- [feat] Implement OAuth authentication route (auth/routes.js:createOAuthRoute())
- [feat] Add token validation middleware (middleware/auth.js:validateToken())
- [test] Add integration tests for OAuth flow (tests/auth.test.js:45-87)

3. Multiple types in one commit:
refactor(core): simplify data processing pipeline

- [refactor] Replace nested loops with map/reduce (utils/process.js:transformData())
- [perf] Optimize memory usage in large dataset handling (utils/memory.js:optimize())
- [fix] Correct edge case in null value handling (utils/validators.js:checkNull())
- [test] Update tests for new pipeline structure (tests/pipeline.test.js)

4. Multiple changes to the same file:
refactor(core): simplify preprompt handling for commit prompts

- [refactor] Remove process_preprompt function (cli/modes/gitcommsg.py:69-124)
- [refactor] Update all functions to accept raw preprompt string (gitcommsg.py:create_system_prompt())
- [refactor] Replace preprompt_data usages with preprompt (gitcommsg.py)
- [docs] Update library usage doc (docs/usage/library_usage.md:516,531-537)


BULLET POINT FORMAT:
- Each bullet MUST start with a type in square brackets: [type]
- DO NOT use the format "- type: description" (without square brackets)
- Instead, ALWAYS use "- [type] description" (with square brackets)
- Example: "- [feat] Add new login component" (correct)
- Not: "- feat: Add new login component" (incorrect)

RULES:
1. BE 100% FACTUAL - Mention ONLY code explicitly shown in the diff
2. NEVER invent or assume changes not directly visible in the code
3. EVERY bullet point MUST reference specific files/functions/lines
4. Include ONLY significant functional changes - EXCLUDE:
   - Version number updates in package manifests
   - Lock file changes (any *.lock, *-lock.*, *.lock.* files)
   - Simple comment additions or documentation updates
   - Dependency version updates that don't affect functionality
   - Formatting or whitespace-only changes (unless that's the main purpose)
   - Build configuration changes that don't affect core functionality
5. If unsure about a change's purpose, describe WHAT changed, not WHY
6. Keep summary line under 50 characters (mandatory)
7. Use appropriate type tags for each change (main summary and each bullet)
8. ONLY describe code that was actually changed
9. Focus on technical specifics, avoid general statements
10. Include proper technical details (method names, component identifiers, etc.)
11. When all changes are to the same file, mention it once in the summary
12. PRIORITIZE the main functional change - if there's one primary change, focus on that

Git diff to process:

{diff_content}"""

def handle_api_call(client, prompt, system_prompt=None, logger=None, max_retries=3):
    """Handle API call with retries and error handling.
    
    Args:
        client: The NGPTClient instance
        prompt: The prompt to send to the API
        system_prompt: Optional system prompt
        logger: Optional logger instance
        max_retries: Maximum number of retries on error
        
    Returns:
        str: Response from the API
    """
    if logger:
        # Enhanced logging of full prompt and system prompt
        logger.log_prompt("DEBUG", system_prompt, prompt)
    
    retry_count = 0
    wait_seconds = 5
    
    while True:
        try:
            # Create messages array with system prompt if available
            messages = None
            if system_prompt:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            else:
                messages = [
                    {"role": "user", "content": prompt}
                ]
            
            response = client.chat(
                prompt=prompt,
                stream=False,
                markdown_format=False,
                messages=messages
            )
            
            if logger:
                # Log full response
                logger.log_response("DEBUG", response)
                
            return response
            
        except Exception as e:
            retry_count += 1
            error_msg = f"Error (attempt {retry_count}/{max_retries}): {str(e)}"
            
            if logger:
                logger.error(error_msg)
                
            if retry_count >= max_retries:
                raise Exception(f"Failed after {max_retries} retries: {str(e)}")
                
            print(f"{COLORS['yellow']}{error_msg}{COLORS['reset']}")
            print(f"{COLORS['yellow']}Retrying in {wait_seconds} seconds...{COLORS['reset']}")
            
            # Use the spinner function
            spinner(f"Retrying in {wait_seconds} seconds...", wait_seconds, color=COLORS['yellow'])
            
            # Exponential backoff
            wait_seconds *= 2

def process_with_chunking(client, diff_content, preprompt, chunk_size=200, recursive=False, logger=None, max_msg_lines=20, max_recursion_depth=3, analyses_chunk_size=None):
    """Process diff with chunking to handle large diffs.
    
    Args:
        client: The NGPTClient instance
        diff_content: The diff content to process
        preprompt: The raw preprompt string
        chunk_size: Maximum number of lines per chunk
        recursive: Whether to use recursive chunking
        logger: Optional logger instance
        max_msg_lines: Maximum number of lines in commit message before condensing
        max_recursion_depth: Maximum recursion depth for message condensing
        analyses_chunk_size: Maximum number of lines per chunk for recursive analysis chunking
        
    Returns:
        str: Generated commit message
    """
    # If analyses_chunk_size not provided, default to chunk_size
    if analyses_chunk_size is None:
        analyses_chunk_size = chunk_size
        
    # Create different system prompts for different stages
    technical_system_prompt = create_technical_analysis_system_prompt(preprompt)
    commit_system_prompt = create_system_prompt(preprompt)
    
    # Log initial diff content
    if logger:
        logger.log_diff("DEBUG", diff_content)
    
    # Split diff into chunks
    chunks = split_into_chunks(diff_content, chunk_size)
    chunk_count = len(chunks)
    
    if logger:
        logger.info(f"Processing {chunk_count} chunks of {chunk_size} lines each")
    
    print(f"{COLORS['green']}Processing diff in {chunk_count} chunks...{COLORS['reset']}")
    
    # Process each chunk
    partial_analyses = []
    for i, chunk in enumerate(chunks):
        print(f"\n{COLORS['cyan']}[Chunk {i+1}/{chunk_count}]{COLORS['reset']}")
        
        # Log chunk content
        if logger:
            logger.log_chunks("DEBUG", i+1, chunk_count, chunk)
        
        # Create chunk prompt
        chunk_prompt = create_chunk_prompt(chunk)
        
        # Log chunk template
        if logger:
            logger.log_template("DEBUG", "CHUNK", chunk_prompt)
        
        # Process chunk - use technical system prompt for analysis
        stop_spinner = threading.Event()
        spinner_thread = threading.Thread(
            target=spinner, 
            args=("Analyzing changes...",), 
            kwargs={"stop_event": stop_spinner, "color": COLORS['yellow']}
        )
        spinner_thread.daemon = True
        spinner_thread.start()
        
        try:
            result = handle_api_call(client, chunk_prompt, technical_system_prompt, logger)
            # Stop the spinner
            stop_spinner.set()
            spinner_thread.join()
            # Show success message
            print(f"{COLORS['green']}✓ Chunk {i+1} processed{COLORS['reset']}")
            partial_analyses.append(result)
        except Exception as e:
            # Stop the spinner
            stop_spinner.set()
            spinner_thread.join()
            print(f"{COLORS['red']}Error processing chunk {i+1}: {str(e)}{COLORS['reset']}")
            if logger:
                logger.error(f"Error processing chunk {i+1}: {str(e)}")
            return None
        
        # Rate limit protection between chunks
        if i < chunk_count - 1:
            # Use the spinner function with fixed duration
            spinner("Waiting to avoid rate limits...", 5, color=COLORS['yellow'])
    
    # Combine partial analyses
    print(f"\n{COLORS['cyan']}Combining analyses from {len(partial_analyses)} chunks...{COLORS['reset']}")
    
    # Log partial analyses
    if logger:
        combined_analyses = "\n\n".join(partial_analyses)
        logger.log_content("DEBUG", "PARTIAL_ANALYSES", combined_analyses)
    
    # Check if we need to use recursive chunking
    combined_analyses = "\n\n".join(partial_analyses)
    combined_line_count = len(combined_analyses.splitlines())
    
    if recursive and combined_line_count > analyses_chunk_size:
        # Use recursive analysis chunking
        return recursive_chunk_analysis(
            client, 
            combined_analyses, 
            preprompt, 
            analyses_chunk_size,
            logger,
            max_msg_lines,
            max_recursion_depth
        )
    else:
        # Combined analysis is under the chunk size limit, generate the commit message
        # Start spinner for generating commit message
        stop_spinner = threading.Event()
        spinner_thread = threading.Thread(
            target=spinner, 
            args=("Generating commit message from combined analysis...",), 
            kwargs={"stop_event": stop_spinner, "color": COLORS['green']}
        )
        spinner_thread.daemon = True
        spinner_thread.start()
        
        combine_prompt = create_combine_prompt(partial_analyses)
        
        # Log combine template
        if logger:
            logger.log_template("DEBUG", "COMBINE", combine_prompt)
        
        try:
            # Use commit message system prompt for final generation
            commit_message = handle_api_call(client, combine_prompt, commit_system_prompt, logger)
            
            # Stop the spinner
            stop_spinner.set()
            spinner_thread.join()
            
            # If the commit message is too long, we need to condense it
            if len(commit_message.splitlines()) > max_msg_lines:
                commit_message = condense_commit_message(
                    client,
                    commit_message,
                    commit_system_prompt,
                    max_msg_lines,
                    max_recursion_depth,
                    1,  # Start at depth 1
                    logger
                )
                
            # Format the final commit message to eliminate path repetition and improve readability
            commit_message = optimize_file_references(client, commit_message, commit_system_prompt, logger)
                
            return commit_message
        except Exception as e:
            # Stop the spinner
            stop_spinner.set()
            spinner_thread.join()
            
            print(f"{COLORS['red']}Error combining analyses: {str(e)}{COLORS['reset']}")
            if logger:
                logger.error(f"Error combining analyses: {str(e)}")
            return None

def recursive_chunk_analysis(client, combined_analysis, preprompt, chunk_size, logger=None, max_msg_lines=20, max_recursion_depth=3, current_depth=1):
    """Recursively chunk and process large analysis results until they're small enough.
    
    Args:
        client: The NGPTClient instance
        combined_analysis: The combined analysis to process
        preprompt: The raw preprompt string
        chunk_size: Maximum number of lines per chunk
        logger: Optional logger instance
        max_msg_lines: Maximum number of lines in commit message before condensing
        max_recursion_depth: Maximum recursion depth for message condensing
        current_depth: Current recursive analysis depth
        
    Returns:
        str: Generated commit message
    """
    # Create different system prompts for different stages
    technical_system_prompt = create_technical_analysis_system_prompt(preprompt)
    commit_system_prompt = create_system_prompt(preprompt)
    
    print(f"\n{COLORS['cyan']}Recursive analysis chunking level {current_depth}...{COLORS['reset']}")
    
    if logger:
        logger.info(f"Starting recursive analysis chunking at depth {current_depth}")
        logger.debug(f"Combined analysis size: {len(combined_analysis.splitlines())} lines")
        logger.log_content("DEBUG", f"COMBINED_ANALYSIS_DEPTH_{current_depth}", combined_analysis)
    
    # If analysis is under chunk size, generate the commit message
    if len(combined_analysis.splitlines()) <= chunk_size:
        print(f"{COLORS['green']}Analysis is small enough, generating commit message...{COLORS['reset']}")
        
        # Create final prompt
        final_prompt = f"""Create a CONVENTIONAL COMMIT MESSAGE based on these analyzed git changes:

{combined_analysis}

FORMAT:
type[(scope)]: <concise summary> (max 50 chars)

- [type] <specific change 1> (filename:function/method/line)
- [type] <specific change 2> (filename:function/method/line)
- [type] <additional changes...>

BULLET POINT FORMAT:
- Each bullet MUST start with a type in square brackets: [type]
- DO NOT use the format "- type: description" (without square brackets)
- Instead, ALWAYS use "- [type] description" (with square brackets)
- Example: "- [feat] Add new login component" (correct)
- Not: "- feat: Add new login component" (incorrect)

RULES:
1. First line must be under 50 characters
2. Include a blank line after the first line
3. Each bullet must include specific file references
4. BE SPECIFIC - mention technical details and function names

DO NOT include any explanation or commentary outside the commit message format."""
        
        # Log final template
        if logger:
            logger.log_template("DEBUG", f"FINAL_PROMPT_DEPTH_{current_depth}", final_prompt)
        
        # Generate the commit message - use commit message system prompt
        commit_message = handle_api_call(client, final_prompt, commit_system_prompt, logger)
        
        if logger:
            logger.log_content("DEBUG", f"COMMIT_MESSAGE_DEPTH_{current_depth}", commit_message)
        
        # If the commit message is too long, we need to condense it
        if len(commit_message.splitlines()) > max_msg_lines:
            commit_message = condense_commit_message(
                client,
                commit_message,
                commit_system_prompt,
                max_msg_lines,
                max_recursion_depth,
                1,  # Start at depth 1
                logger
            )
        
        # Format the final commit message to eliminate path repetition and improve readability
        commit_message = optimize_file_references(client, commit_message, commit_system_prompt, logger)
        
        return commit_message
    
    # Analysis is still too large, need to chunk it
    print(f"{COLORS['yellow']}Analysis still too large ({len(combined_analysis.splitlines())} lines), chunking...{COLORS['reset']}")
    
    # Split the analysis into chunks
    analysis_chunks = split_into_chunks(combined_analysis, chunk_size)
    analysis_chunk_count = len(analysis_chunks)
    
    if logger:
        logger.info(f"Split analysis into {analysis_chunk_count} chunks at depth {current_depth}")
    
    # Process each analysis chunk and get a condensed version
    condensed_chunks = []
    for i, analysis_chunk in enumerate(analysis_chunks):
        print(f"\n{COLORS['cyan']}[Analysis chunk {i+1}/{analysis_chunk_count} at depth {current_depth}]{COLORS['reset']}")
        
        # Create a target size based on how many chunks we have
        target_size = min(int(chunk_size / analysis_chunk_count), 100)  # Make sure it's not too small
        
        # Create a prompt to condense this analysis chunk
        condense_prompt = f"""You are analyzing a PORTION of already analyzed git changes. This is analysis data, not raw git diff.

Take this SECTION of technical analysis and condense it to be UNDER {target_size} lines while preserving the most important technical details.

Keep the format consistent with the system prompt.
Preserve full file paths, function names, and technical changes.
Group related changes when appropriate.

SECTION OF ANALYSIS TO CONDENSE:

{analysis_chunk}"""
        
        if logger:
            logger.log_template("DEBUG", f"CONDENSE_ANALYSIS_DEPTH_{current_depth}_CHUNK_{i+1}", condense_prompt)
        
        # Start spinner for analysis
        stop_spinner = threading.Event()
        spinner_thread = threading.Thread(
            target=spinner, 
            args=(f"Condensing analysis chunk {i+1}/{analysis_chunk_count}...",), 
            kwargs={"stop_event": stop_spinner, "color": COLORS['yellow']}
        )
        spinner_thread.daemon = True
        spinner_thread.start()
        
        # Condense this analysis chunk - use technical system prompt for condensing analysis
        try:
            condensed_chunk = handle_api_call(client, condense_prompt, technical_system_prompt, logger)
            # Stop the spinner
            stop_spinner.set()
            spinner_thread.join()
            
            print(f"{COLORS['green']}✓ Analysis chunk {i+1}/{analysis_chunk_count} condensed{COLORS['reset']}")
            condensed_chunks.append(condensed_chunk)
            
            if logger:
                logger.log_content("DEBUG", f"CONDENSED_ANALYSIS_DEPTH_{current_depth}_CHUNK_{i+1}", condensed_chunk)
        except Exception as e:
            # Stop the spinner
            stop_spinner.set()
            spinner_thread.join()
            
            print(f"{COLORS['red']}Error condensing analysis chunk {i+1}: {str(e)}{COLORS['reset']}")
            if logger:
                logger.error(f"Error condensing analysis chunk {i+1} at depth {current_depth}: {str(e)}")
            return None
        
        # Rate limit protection between chunks
        if i < analysis_chunk_count - 1:
            # Use the spinner function with fixed duration
            spinner("Waiting to avoid rate limits...", 5, color=COLORS['yellow'])
    
    # Combine condensed chunks
    combined_condensed = "\n\n".join(condensed_chunks)
    condensed_line_count = len(combined_condensed.splitlines())
    
    print(f"\n{COLORS['cyan']}Condensed analysis to {condensed_line_count} lines at depth {current_depth}{COLORS['reset']}")
    
    if logger:
        logger.info(f"Combined condensed analysis: {condensed_line_count} lines at depth {current_depth}")
        logger.log_content("DEBUG", f"COMBINED_CONDENSED_DEPTH_{current_depth}", combined_condensed)
    
    # Recursively process the combined condensed analysis
    return recursive_chunk_analysis(
        client,
        combined_condensed,
        preprompt,
        chunk_size,
        logger,
        max_msg_lines,
        max_recursion_depth,
        current_depth + 1
    )

def condense_commit_message(client, commit_message, system_prompt, max_msg_lines, max_recursion_depth, current_depth=1, logger=None):
    """Recursively condense a commit message to be under the maximum length.
    
    Args:
        client: The NGPTClient instance
        commit_message: The commit message to condense
        system_prompt: The system prompt
        max_msg_lines: Maximum number of lines in commit message
        max_recursion_depth: Maximum recursion depth for condensing
        current_depth: Current recursion depth
        logger: Optional logger instance
        
    Returns:
        str: Condensed commit message
    """
    # Always use commit message system prompt for condensing commit messages
    if not isinstance(system_prompt, str) or not system_prompt.startswith("You are an expert Git commit message writer"):
        system_prompt = create_system_prompt(None)  # Use default commit message system prompt
    
    commit_lines = len(commit_message.splitlines())
    print(f"\n{COLORS['cyan']}Commit message has {commit_lines} lines (depth {current_depth}/{max_recursion_depth}){COLORS['reset']}")
    
    if logger:
        logger.info(f"Commit message has {commit_lines} lines at depth {current_depth}/{max_recursion_depth}")
        logger.log_content("DEBUG", f"COMMIT_MESSAGE_DEPTH_{current_depth}", commit_message)
    
    # If already under the limit, return as is
    if commit_lines <= max_msg_lines:
        return commit_message
    
    # Check if we've reached the maximum recursion depth
    is_final_depth = current_depth >= max_recursion_depth
    
    # Create the condense prompt - only mention the specific max_msg_lines at final depth
    if is_final_depth:
        condense_prompt = f"""Rewrite this git commit message to be MUST BE AT MOST {max_msg_lines} LINES TOTAL.
PRESERVE the first line exactly as is, and keep the most important changes in the bullet points.
Group related changes when possible.

CURRENT MESSAGE (TOO LONG):
{commit_message}

BULLET POINT FORMAT:
- Each bullet MUST start with a type in square brackets: [type]
- DO NOT use the format "- type: description" (without square brackets)
- Instead, ALWAYS use "- [type] description" (with square brackets)
- Example: "- [feat] Add new login component" (correct)
- Not: "- feat: Add new login component" (incorrect)

REQUIREMENTS:
1. First line must be preserved exactly as is
2. MUST BE AT MOST {max_msg_lines} LINES TOTAL including blank lines - THIS IS A HARD REQUIREMENT
3. Include the most significant changes
4. Group related changes when possible
5. Keep proper formatting with bullet points
6. Maintain detailed file/function references in each bullet point
7. KEEP TYPE TAGS IN SQUARE BRACKETS: [type]"""
    else:
        # At earlier depths, don't specify the exact line count limit
        condense_prompt = f"""Rewrite this git commit message to be more concise.
PRESERVE the first line exactly as is, and keep the most important changes in the bullet points.
Group related changes when possible.

CURRENT MESSAGE (TOO LONG):
{commit_message}

BULLET POINT FORMAT:
- Each bullet MUST start with a type in square brackets: [type]
- DO NOT use the format "- type: description" (without square brackets)
- Instead, ALWAYS use "- [type] description" (with square brackets)
- Example: "- [feat] Add new login component" (correct)
- Not: "- feat: Add new login component" (incorrect)

REQUIREMENTS:
1. First line must be preserved exactly as is
2. Make the message significantly shorter while preserving key information
3. Include the most significant changes
4. Group related changes when possible
5. Keep proper formatting with bullet points
6. Maintain detailed file/function references in each bullet point
7. KEEP TYPE TAGS IN SQUARE BRACKETS: [type]"""
    
    if logger:
        logger.log_template("DEBUG", f"CONDENSE_PROMPT_DEPTH_{current_depth}", condense_prompt)
    
    # Start spinner for condensing
    stop_spinner = threading.Event()
    spinner_thread = threading.Thread(
        target=spinner, 
        args=(f"Condensing commit message (depth {current_depth}/{max_recursion_depth})...",), 
        kwargs={"stop_event": stop_spinner, "color": COLORS['yellow']}
    )
    spinner_thread.daemon = True
    spinner_thread.start()
    
    try:
        condensed_result = handle_api_call(client, condense_prompt, system_prompt, logger)
        # Stop the spinner
        stop_spinner.set()
        spinner_thread.join()
        
        if logger:
            logger.log_content("DEBUG", f"CONDENSED_RESULT_DEPTH_{current_depth}", condensed_result)
        
        # Check if we need to condense further
        condensed_lines = len(condensed_result.splitlines())
        
        if condensed_lines > max_msg_lines and current_depth < max_recursion_depth:
            print(f"{COLORS['yellow']}Commit message still has {condensed_lines} lines. Further condensing...{COLORS['reset']}")
            
            if logger:
                logger.info(f"Commit message still has {condensed_lines} lines after condensing at depth {current_depth}")
            
            # Try again at the next depth
            return condense_commit_message(
                client,
                condensed_result,
                system_prompt,
                max_msg_lines,
                max_recursion_depth,
                current_depth + 1,
                logger
            )
        else:
            return condensed_result
    except Exception as e:
        # Stop the spinner
        stop_spinner.set()
        spinner_thread.join()
        
        print(f"{COLORS['red']}Error condensing commit message: {str(e)}{COLORS['reset']}")
        if logger:
            logger.error(f"Error condensing commit message at depth {current_depth}: {str(e)}")
        # Return the original message if condensing fails
        return commit_message

def create_combine_prompt(partial_analyses):
    """Create prompt for combining partial analyses.
    
    Args:
        partial_analyses: List of partial analyses to combine
        
    Returns:
        str: Prompt for the AI
    """
    all_analyses = "\n\n".join(partial_analyses)
    
    return f"""===CRITICAL INSTRUCTION===
You are working with ANALYZED SUMMARIES of git changes, NOT raw git diff.
The raw git diff has ALREADY been processed into these summaries.

TASK: Synthesize these partial analyses into a complete conventional commit message 
following the format specified in the system prompt.

The analyses to combine:

{all_analyses}

RULES FOR FILENAMES:
1. For the FIRST mention of a file, use the full relative path
2. For SUBSEQUENT mentions of the same file, use ONLY the filename without path
   - Example: First mention: "utils/helpers/format.js" → Subsequent mentions: "format.js"
3. Only include the full path again if there are multiple files with the same name
4. For repeated mentions of the same file, consider grouping related changes in one bullet

BULLET POINT FORMAT:
- Each bullet MUST start with a type in square brackets: [type]
- DO NOT use the format "- type: description" (without square brackets)
- Instead, ALWAYS use "- [type] description" (with square brackets)
- Example: "- [feat] Add new login component" (correct)
- Not: "- feat: Add new login component" (incorrect)

EXAMPLE OF PROPERLY FORMATTED COMMIT MESSAGE:
refactor(core): simplify preprompt handling for commit prompts

- [refactor] Remove process_preprompt function (cli/modes/gitcommsg.py:69-124)
- [refactor] Update all functions to accept raw preprompt string (gitcommsg.py:create_system_prompt())
- [refactor] Replace preprompt_data usages with preprompt (gitcommsg.py)
- [docs] Update library usage doc (docs/usage/library_usage.md:516,531-537)


REMINDER:
- First line must be under 50 characters
- Include a blank line after the first line
- Each bullet must include specific file references with format [type]
- Include specific technical details in each bullet point

DO NOT ask for the original diff or add explanations outside the commit message format."""

def is_git_diff(content):
    """Check if the content looks like a git diff.
    
    Args:
        content: The content to check
        
    Returns:
        bool: True if the content looks like a git diff, False otherwise
    """
    # Check for common git diff patterns
    diff_patterns = [
        r'diff --git a/.*? b/.*?',  # diff --git a/file b/file
        r'index [a-f0-9]+\.\.[a-f0-9]+',  # index hash..hash
        r'--- a/.*?',  # --- a/file
        r'\+\+\+ b/.*?',  # +++ b/file
        r'@@ -\d+,\d+ \+\d+,\d+ @@'  # @@ -line,count +line,count @@
    ]
    
    # Check if the content contains at least one of these patterns
    for pattern in diff_patterns:
        if re.search(pattern, content):
            return True
    
    # Check if the content contains lines starting with + or - (changes)
    lines = content.splitlines()
    plus_minus_lines = [line for line in lines if line.startswith('+') or line.startswith('-')]
    
    # If there are many +/- lines, it's likely a diff
    if len(plus_minus_lines) > 5 and len(plus_minus_lines) / len(lines) > 0.1:
        return True
    
    return False

def strip_code_block_formatting(text):
    """Strip code block formatting from the text if present.
    
    Args:
        text: Text to strip code block formatting from
        
    Returns:
        str: Text without code block formatting
    """
    # Check if the text starts with ``` and ends with ```
    pattern = r'^```(?:.*?)\n(.*?)```$'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        # Extract content between backticks and remove any trailing whitespace
        return match.group(1).rstrip()
    return text

def optimize_file_references(client, commit_message, system_prompt=None, logger=None):
    """Optimize the file references in the commit message by eliminating path repetition and improving readability.
    
    Args:
        client: The NGPTClient instance
        commit_message: The commit message to format
        system_prompt: Optional system prompt for formatting
        logger: Optional logger instance
        
    Returns:
        str: Commit message with optimized file references
    """
    # If no system prompt provided, use a minimalist one
    if not system_prompt:
        system_prompt = """You are an expert Git commit message formatter."""
    
    format_prompt = f"""TASK: Reformat file paths in this commit message to make it more readable while preserving the standard format

COMMIT MESSAGE TO OPTIMIZE:
{commit_message}

MAINTAIN THIS EXACT FORMAT FOR EACH BULLET:
- [type] Description with file references (filepath:line/function)

FILE PATH OPTIMIZATION RULES (CRITICAL PRIORITY):
1. PRESERVE PROPER PARENTHESES FORMAT - File references go in parentheses at the end of each bullet:
   • "- [add] Add components (src/components/Button.jsx, Card.jsx)"
   • Always keep references in parentheses at the end

2. ELIMINATE PATH REPETITION in file lists:
   • "- [add] Add components (src/components/Button.jsx, src/components/Card.jsx)" - BAD
   • "- [add] Add components (src/components/*.jsx)" - Use wildcard when appropriate
   • "- [add] Add 5 component files (src/components/)" - Use count for many files

3. AVOID REDUNDANT FILENAMES:
   • Don't repeat filenames in both description and parentheses
   • Group files by category in the description

EXAMPLES THAT FOLLOW THE PROPER FORMAT:

❌ BEFORE (POOR FORMATTING):
- [docs] Add documentation for tawhid, names_of_allah, transcendence (islam/beliefs/tawhid.md, islam/beliefs/names_of_allah.md, islam/beliefs/transcendence.md)

✅ AFTER (GOOD FORMATTING):
- [docs] Add documentation for theological concepts (islam/beliefs/tawhid.md, names_of_allah.md, transcendence.md)

❌ BEFORE (POOR FORMATTING):
- [fix] Update error handling in app/utils/errors.js, app/utils/validation.js, app/utils/formatting.js

✅ AFTER (GOOD FORMATTING):
- [fix] Update error handling (app/utils/errors.js, validation.js, formatting.js)

RULES FOR OUTPUT:
1. PRESERVE proper format with parentheses at the end
2. Keep the same bullet structure and number of bullets
3. DO NOT change type tags or summary line
4. Mention common paths ONCE, then list files

THE STANDARD FORMAT FOR COMMIT MESSAGES IS:
type[(scope)]: concise summary

- [type] Description (filepath:line/function)
- [type] Another description (filepath:line/function)"""
    
    # Log formatting template
    if logger:
        logger.log_template("DEBUG", "OPTIMIZE_FILE_REFS", format_prompt)
    
    # Start spinner for formatting
    stop_spinner = threading.Event()
    spinner_thread = threading.Thread(
        target=spinner, 
        args=("Optimizing file references...",), 
        kwargs={"stop_event": stop_spinner, "color": COLORS['green']}
    )
    spinner_thread.daemon = True
    spinner_thread.start()
    
    try:
        formatted_message = handle_api_call(client, format_prompt, system_prompt, logger)
        # Stop the spinner
        stop_spinner.set()
        spinner_thread.join()
        
        if logger:
            logger.log_content("DEBUG", "OPTIMIZED_FILE_REFS", formatted_message)
        
        return formatted_message
    except Exception as e:
        # Stop the spinner
        stop_spinner.set()
        spinner_thread.join()
        
        print(f"{COLORS['red']}Error optimizing file references: {str(e)}{COLORS['reset']}")
        if logger:
            logger.error(f"Error optimizing file references: {str(e)}")
        # Return the original message if formatting fails
        return commit_message

def gitcommsg_mode(client, args, logger=None):
    """Handle the Git commit message generation mode.
    
    Args:
        client: The NGPTClient instance
        args: The parsed command line arguments
        logger: Optional logger instance
    """
    # Set up logging if requested
    custom_logger = None
    log_path = None
    
    if args.log:
        custom_logger = create_gitcommsg_logger(args.log)
    
    # Use both loggers if they exist
    active_logger = logger if logger else custom_logger
    
    if active_logger:
        active_logger.info("Starting gitcommsg mode")
        active_logger.debug(f"Args: {args}")
    
    try:
        # Process piped input as diff content when --pipe flag is set
        piped_diff_content = None
        if args.pipe:
            if active_logger:
                active_logger.info("Processing piped input as diff content")
            
            if not sys.stdin.isatty():
                piped_diff_content = sys.stdin.read().strip()
                if not piped_diff_content:
                    print(f"{COLORS['yellow']}Warning: No diff content received from stdin.{COLORS['reset']}")
                else:
                    # Validate that the piped content looks like a git diff
                    if not is_git_diff(piped_diff_content):
                        print(f"{COLORS['red']}Error: The piped content doesn't appear to be a git diff. Exiting.{COLORS['reset']}")
                        if active_logger:
                            active_logger.error("Piped content doesn't appear to be a git diff. Aborting.")
                        return
                    elif active_logger:
                        active_logger.info(f"Received {len(piped_diff_content.splitlines())} lines of diff content from stdin")
            else:
                print(f"{COLORS['yellow']}Error: --pipe was specified but no input is piped.{COLORS['reset']}")
                return
        
        # Check if --diff was explicitly passed on the command line
        diff_option_provided = '--diff' in sys.argv
        diff_path_provided = diff_option_provided and args.diff is not None and args.diff is not True
        
        # If piped diff content is available, use it directly
        if piped_diff_content:
            diff_content = piped_diff_content
            if active_logger:
                active_logger.info("Using diff content from stdin")
        # If --diff wasn't explicitly provided on the command line, don't use the config value
        elif not diff_option_provided:
            # Even if diff is in CLI config, don't use it unless --diff flag is provided
            diff_file = None
            if active_logger:
                active_logger.info("Not using diff file from CLI config because --diff flag was not provided")
            
            # Get diff content from git staged changes
            diff_content = get_diff_content(diff_file)
        else:
            # --diff flag was provided on command line
            if args.diff is True:
                # --diff flag was used without a path, use the value from CLI config
                success, config_diff = get_cli_config_option("diff")
                diff_file = config_diff if success and config_diff else None
                if active_logger:
                    if diff_file:
                        active_logger.info(f"Using diff file from CLI config: {diff_file}")
                    else:
                        active_logger.info("No diff file found in CLI config")
            else:
                # --diff flag was used with an explicit path
                diff_file = args.diff
                if active_logger:
                    active_logger.info(f"Using explicitly provided diff file: {diff_file}")
            
            # Get diff content from file
            diff_content = get_diff_content(diff_file)
        
        if not diff_content:
            print(f"{COLORS['red']}No diff content available. Exiting.{COLORS['reset']}")
            return
        
        # Log the diff content
        if active_logger:
            active_logger.log_diff("DEBUG", diff_content)
        
        # Process preprompt if provided
        preprompt = None
        if args.preprompt:
            preprompt = args.preprompt
            if active_logger:
                active_logger.debug(f"Using preprompt: {preprompt}")
                active_logger.log_content("DEBUG", "PREPROMPT", preprompt)
        
        # Create system prompts for different stages
        technical_system_prompt = create_technical_analysis_system_prompt(preprompt)
        commit_system_prompt = create_system_prompt(preprompt)
        
        # Log system prompts
        if active_logger:
            active_logger.log_template("DEBUG", "TECHNICAL_SYSTEM", technical_system_prompt)
            active_logger.log_template("DEBUG", "COMMIT_SYSTEM", commit_system_prompt)
        
        print(f"\n{COLORS['green']}Generating commit message...{COLORS['reset']}")
        
        # Process based on chunking options
        result = None
        if args.chunk_size:
            chunk_size = args.chunk_size
            if active_logger:
                active_logger.info(f"Using chunk size: {chunk_size}")
        
        # Get max_msg_lines from args or use default
        max_msg_lines = getattr(args, 'max_msg_lines', 20)  # Default to 20 if not specified
        if active_logger:
            active_logger.info(f"Maximum commit message lines: {max_msg_lines}")
        
        # Get max_recursion_depth from args or use default
        max_recursion_depth = getattr(args, 'max_recursion_depth', 3)  # Default to 3 if not specified
        if active_logger:
            active_logger.info(f"Maximum recursion depth for message condensing: {max_recursion_depth}")
        
        # Get analyses_chunk_size from args or use default
        analyses_chunk_size = getattr(args, 'analyses_chunk_size', args.chunk_size)  # Default to chunk_size if not specified
        if active_logger:
            active_logger.info(f"Analyses chunk size: {analyses_chunk_size}")
        
        if args.rec_chunk:
            # Use chunking with recursive processing
            if active_logger:
                active_logger.info(f"Using recursive chunking with max_recursion_depth: {max_recursion_depth}")
            
            result = process_with_chunking(
                client, 
                diff_content, 
                preprompt, 
                chunk_size=args.chunk_size,
                recursive=True,
                logger=active_logger,
                max_msg_lines=max_msg_lines,
                max_recursion_depth=max_recursion_depth,
                analyses_chunk_size=analyses_chunk_size
            )
        else:
            # Direct processing without chunking
            if active_logger:
                active_logger.info("Processing without chunking")
            
            # Pass preprompt to create_final_prompt
            prompt = create_final_prompt(diff_content)
            
            # Log final template
            if active_logger:
                active_logger.log_template("DEBUG", "DIRECT_PROCESSING", prompt)
            
            # Use commit message system prompt for direct processing
            result = handle_api_call(client, prompt, commit_system_prompt, active_logger)
            
            # Check if the result exceeds max_msg_lines and recursive_chunk is enabled
            if result and len(result.splitlines()) > max_msg_lines:
                print(f"{COLORS['yellow']}Commit message exceeds {max_msg_lines} lines, condensing...{COLORS['reset']}")
                if active_logger:
                    active_logger.info(f"Commit message exceeds {max_msg_lines} lines, starting condensing process")
                
                # Use our condense_commit_message function with commit message system prompt
                result = condense_commit_message(
                    client,
                    result,
                    commit_system_prompt,
                    max_msg_lines,
                    max_recursion_depth,
                    1,  # Start at depth 1
                    active_logger
                )
                
            # Format the final commit message to eliminate path repetition and improve readability
            result = optimize_file_references(client, result, commit_system_prompt, active_logger)
        
        if not result:
            print(f"{COLORS['red']}Failed to generate commit message.{COLORS['reset']}")
            return
        
        # Strip any code block formatting
        result = strip_code_block_formatting(result)
        
        # Display the result
        print(f"\n{COLORS['green']}✨ Generated Commit Message:{COLORS['reset']}\n")
        print(result)
        
        # Log the result
        if active_logger:
            active_logger.info("Generated commit message successfully")
            active_logger.log_content("INFO", "FINAL_COMMIT_MESSAGE", result)
        
        # Try to copy to clipboard
        copy_to_clipboard(result)
        if active_logger:
            active_logger.info("Offered to copy commit message to clipboard")
    
    except Exception as e:
        print(f"{COLORS['red']}Error: {str(e)}{COLORS['reset']}")
        if active_logger:
            active_logger.error(f"Error in gitcommsg mode: {str(e)}", exc_info=True) 