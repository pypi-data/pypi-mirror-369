# This Makefile compiles various files that are needed for an installation of Pigreads.
# Run "make" before "pip install".
FLAGS = -O3 -Wall -shared -std=c++20 -fPIC -lOpenCL $(shell python3 -m pybind11 --includes)
EXT = $(shell python3-config --extension-suffix)
SOURCE = src/pigreads/models.py src/core1/kernels.h src/core2/kernels.h
TARGETS = $(SOURCE) src/pigreads/core1$(EXT) src/pigreads/core2$(EXT)

all: $(SOURCE)

compile: $(TARGETS)

src/pigreads/models.py: src/models/compile.py $(wildcard src/models/*.yaml) $(wildcard src/models/*.mmt) $(wildcard src/models/*.cellml)
	./$< $(dir $<) docs/models $@

src/core1/kernels.h src/core2/kernels.h: %/kernels.h: %/types.h %/states.h %/geometry.h
	printf '// AUTOMATICALLY GENERATED FILE\nstatic const char* KERNEL_HEADER = R"source(\n' > $@
	cat $*/types.h $*/states.h >> $@
	printf ')source";\n\nstatic const char* CORE_KERNELS = R"source(\n' >> $@
	cat $*/geometry.h >> $@
	printf ')source";\n' >> $@

src/pigreads/_%$(EXT): src/%/main.cpp src/%/geometry.h src/%/kernels.h src/%/opencl.hpp src/%/states.h src/%/types.h
	g++ $(FLAGS) -o $@ $<

clean:
	$(RM) $(TARGETS)
	$(RM) -r docs/models
