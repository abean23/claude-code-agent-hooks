#!/bin/bash
claude "$(cat sample_prompt.txt)"  # Non-interactive: Runs prompt and exits
cat generated_tests.py  # Check output file