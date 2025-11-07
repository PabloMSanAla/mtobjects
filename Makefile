# Makefile for mtobjects C extensions
# This ensures reliable compilation across different platforms

# Detect the operating system
UNAME := $(shell uname)

# Set platform-specific settings
ifeq ($(UNAME), Darwin)
    # macOS
    CC = gcc
    SHARED_FLAGS = -shared -fPIC
    LIB_EXT = .so
else ifeq ($(UNAME), Linux)
    # Linux
    CC = gcc
    SHARED_FLAGS = -shared -fPIC
    LIB_EXT = .so
else
    # Windows (assumes MinGW or similar)
    CC = gcc
    SHARED_FLAGS = -shared
    LIB_EXT = .dll
endif

# Directories
SRC_DIR = mtolib/src
LIB_DIR = mtolib/lib

# Source files
HEAP_SRC = $(SRC_DIR)/mt_heap.c
STACK_SRC = $(SRC_DIR)/mt_stack.c
OBJECTS_SRC = $(SRC_DIR)/mt_objects.c
MAXTREE_SRC = $(SRC_DIR)/maxtree.c
NODE_TEST_SRC = $(SRC_DIR)/mt_node_test_4.c

# Header files
MAIN_HEADER = $(SRC_DIR)/main.h
MAIN_DOUBLE_HEADER = $(SRC_DIR)/main_double.h

# Output libraries
MT_OBJECTS_LIB = $(LIB_DIR)/mt_objects$(LIB_EXT)
MAXTREE_LIB = $(LIB_DIR)/maxtree$(LIB_EXT)
MT_OBJECTS_DOUBLE_LIB = $(LIB_DIR)/mt_objects_double$(LIB_EXT)
MAXTREE_DOUBLE_LIB = $(LIB_DIR)/maxtree_double$(LIB_EXT)

# All targets
ALL_LIBS = $(MT_OBJECTS_LIB) $(MAXTREE_LIB) $(MT_OBJECTS_DOUBLE_LIB) $(MAXTREE_DOUBLE_LIB)

.PHONY: compile install clean rebuild check all help

# Default target
all: compile

# Create lib directory if it doesn't exist
$(LIB_DIR):
	@echo "Creating library directory: $(LIB_DIR)"
	@mkdir -p $(LIB_DIR)

# Build mt_objects.so (single precision)
$(MT_OBJECTS_LIB): $(OBJECTS_SRC) $(HEAP_SRC) $(NODE_TEST_SRC) $(MAIN_HEADER) | $(LIB_DIR)
	@echo "Compiling mt_objects (single precision)..."
	$(CC) $(SHARED_FLAGS) -include $(MAIN_HEADER) -o $@ $(OBJECTS_SRC) $(HEAP_SRC) $(NODE_TEST_SRC)

# Build maxtree.so (single precision)
$(MAXTREE_LIB): $(MAXTREE_SRC) $(STACK_SRC) $(HEAP_SRC) $(MAIN_HEADER) | $(LIB_DIR)
	@echo "Compiling maxtree (single precision)..."
	$(CC) $(SHARED_FLAGS) -include $(MAIN_HEADER) -o $@ $(MAXTREE_SRC) $(STACK_SRC) $(HEAP_SRC)

# Build mt_objects_double.so (double precision)
$(MT_OBJECTS_DOUBLE_LIB): $(OBJECTS_SRC) $(HEAP_SRC) $(NODE_TEST_SRC) $(MAIN_DOUBLE_HEADER) | $(LIB_DIR)
	@echo "Compiling mt_objects (double precision)..."
	$(CC) $(SHARED_FLAGS) -include $(MAIN_DOUBLE_HEADER) -o $@ $(OBJECTS_SRC) $(HEAP_SRC) $(NODE_TEST_SRC)

# Build maxtree_double.so (double precision)
$(MAXTREE_DOUBLE_LIB): $(MAXTREE_SRC) $(STACK_SRC) $(HEAP_SRC) $(MAIN_DOUBLE_HEADER) | $(LIB_DIR)
	@echo "Compiling maxtree (double precision)..."
	$(CC) $(SHARED_FLAGS) -include $(MAIN_DOUBLE_HEADER) -o $@ $(MAXTREE_SRC) $(STACK_SRC) $(HEAP_SRC)

# Compile all libraries
compile: $(ALL_LIBS)

# Clean built libraries
clean:
	@echo "Cleaning compiled libraries..."
	@rm -f $(LIB_DIR)/*$(LIB_EXT)

# Force rebuild
rebuild: clean compile

# Check if all libraries exist
check:
	@echo "Checking for compiled libraries..."
	@for lib in $(ALL_LIBS); do \
		if [ -f "$$lib" ]; then \
			echo "✓ $$lib exists ($$(stat -f%z "$$lib" 2>/dev/null || stat -c%s "$$lib" 2>/dev/null || echo "unknown") bytes)"; \
		else \
			echo "✗ $$lib missing"; \
		fi; \
	done

# Install with pip after compilation
install: compile
	pip install .

# Help target
help:
	@echo "Available targets:"
	@echo "  all/compile - Build all C extensions (default)"
	@echo "  clean       - Remove compiled libraries"
	@echo "  rebuild     - Clean and build all"
	@echo "  check       - Check if all libraries exist"
	@echo "  install     - Build all C extensions and install with pip"
	@echo "  help        - Show this help message"