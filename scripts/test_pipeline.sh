#!/bin/bash
claude "$(cat examples/sample_prompt.txt)"  # Non-interactive: Runs prompt and exits
cat outputs/generated_tests.py  # Check output file