# Makefile for compiling Python files in the specified directory using mpy_cross


# Define the mpy_cross tool path
MPY_CROSS := ../../components/micropython/core/mpy-cross/mpy-cross
# If PY_LIB is not set, use 'lib' as the default
PY_LIB ?= py_lib

# Define the output directory for compiled .mpy files
BUILD_DIR = build_mpy/$(PY_LIB)_mpy

# Identify all Python files in the specified directory
SRC_FILES = $(wildcard $(PY_LIB)/*.py)

# Generate a list of corresponding .mpy files in the 'build' directory
OUT_FILES = $(patsubst $(PY_LIB)/%.py,$(BUILD_DIR)/%.mpy,$(SRC_FILES))

# Target: build all .mpy files in the 'build' directory
all: $(OUT_FILES)

# Rule: compile each source .py file to .mpy
$(BUILD_DIR)/%.mpy: $(PY_LIB)/%.py
	@mkdir -p $(BUILD_DIR)
	@echo "Compiling $<"
	@$(MPY_CROSS) -o $@ $<

# Target: create 'build' directory if it doesn't exist
$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

# Target: clean up build artifacts
clean:
	@rm -rf $(BUILD_DIR)

.PHONY: all clean