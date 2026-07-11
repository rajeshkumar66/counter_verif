#=============================================================================
# Makefile - Questa simulation flow for counter design
# Location: sim/  (paths below are relative to this directory)
#=============================================================================

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
LIB         := work
TOP         := counter_tb
OPT_NAME    := counter_opt

RTL_DIR     := ../rtl
TB_DIR      := ../tb
LOG_DIR     := ../logs
REPORT_DIR  := ../reports
CONFIG_DIR  := ../config

RTL_SRC     := $(RTL_DIR)/counter.sv
TB_SRC      := $(TB_DIR)/counter_tb.sv
TEST_CONFIG := $(CONFIG_DIR)/test_config.yaml

# Command-line overridable variables, e.g.:
#   make sim TESTNAME=test1 SEED=1
#   make compile DEFINE=+define+DEBUG
TESTNAME    ?= test1
SEED        ?= 1
DEFINE      ?=
VERBOSITY   ?= UVM_MEDIUM
TIMEOUT_NS  ?= 10000

# BATCH_MODE=1 is set internally by `regress` (see below) so that `sim`
# runs headless (-c, no GUI) and auto-quits after each test, instead of
# opening the interactive Questa waveform viewer used by a plain
# `make sim`.
BATCH_MODE  ?=
ifeq ($(BATCH_MODE),1)
  VSIM_FLAGS := -c
  VSIM_ENV   := BATCH_MODE=1
else
  VSIM_FLAGS :=
  VSIM_ENV   :=
endif

# Questa tool binaries (assumed to be on PATH)
VLIB        := vlib
VMAP        := vmap
VLOG        := vlog
VOPT        := vopt
VSIM        := vsim

.PHONY: all lib compile opt sim regress clean

all: sim

# ---------------------------------------------------------------------------
# 1. lib - create the working library
# ---------------------------------------------------------------------------
lib:
	@echo "==> [lib] Creating work library: $(LIB)"
	$(VLIB) $(LIB)
	$(VMAP) $(LIB) $(LIB)

# ---------------------------------------------------------------------------
# 2. compile - compile RTL + TB with vlog, log to logs/compile.log
# ---------------------------------------------------------------------------
compile: lib
	@mkdir -p $(LOG_DIR)
	@echo "==> [compile] Compiling sources (DEFINE=$(DEFINE))"
	$(VLOG) -work $(LIB) $(DEFINE) \
		$(RTL_SRC) \
		$(TB_SRC) \
		-l $(LOG_DIR)/compile.log

# ---------------------------------------------------------------------------
# 3. opt - optimize compiled design with vopt into a named snapshot
# ---------------------------------------------------------------------------
opt: compile
	@echo "==> [opt] Optimizing $(LIB).$(TOP) -> $(OPT_NAME)"
	$(VOPT) -work $(LIB) $(LIB).$(TOP) -o $(OPT_NAME) +acc

# ---------------------------------------------------------------------------
# 4. sim - run the optimized snapshot with vsim, driven by run.do.
#    Accepts TESTNAME, SEED, VERBOSITY and TIMEOUT_NS from the command
#    line, and passes VERBOSITY/TIMEOUT_NS through as plusargs.
#    By default Questa opens in GUI mode (no -c) and stays open after
#    the run so the waveform is already there for you to inspect.
#    When invoked with BATCH_MODE=1 (done internally by `regress`),
#    it instead runs headless and quits automatically after each test.
# ---------------------------------------------------------------------------
sim: opt
	@mkdir -p $(LOG_DIR)
	@echo "==> [sim] Running TESTNAME=$(TESTNAME) SEED=$(SEED) VERBOSITY=$(VERBOSITY) TIMEOUT_NS=$(TIMEOUT_NS)"
	$(VSIM_ENV) $(VSIM) $(VSIM_FLAGS) -lib $(LIB) $(OPT_NAME) \
		-sv_seed $(SEED) \
		+TESTNAME=$(TESTNAME) \
		+UVM_VERBOSITY=$(VERBOSITY) \
		+TIMEOUT_NS=$(TIMEOUT_NS) \
		-l $(LOG_DIR)/sim_$(TESTNAME)_$(SEED).log \
		-wlf /tmp/vsim_$(TESTNAME)_$(SEED).wlf \
		-do "do run.do"
	@rm -f /tmp/vsim_$(TESTNAME)_$(SEED).wlf

# ---------------------------------------------------------------------------
# 5. regress - reads config/test_config.yaml and runs `sim` (headless,
#    no waveform GUI) for every test listed there, then writes a
#    pass/fail summary to reports/regression_summary.log
# ---------------------------------------------------------------------------
regress:
	@mkdir -p $(REPORT_DIR)
	@rm -f $(REPORT_DIR)/regression_summary.log
	@python3 -c "\
import yaml; \
data = yaml.safe_load(open('$(TEST_CONFIG)')); \
[print(f\"{t['name']}:{t['seed']}:{t['verbosity']}:{t['timeout_ns']}\") for t in data['tests']]" \
	| while IFS=: read -r name seed verbosity timeout_ns; do \
		echo "==> [regress] Running $$name (seed=$$seed, verbosity=$$verbosity, timeout_ns=$${timeout_ns}ns)"; \
		$(MAKE) sim TESTNAME=$$name SEED=$$seed VERBOSITY=$$verbosity TIMEOUT_NS=$$timeout_ns BATCH_MODE=1; \
		logfile=$(LOG_DIR)/sim_$${name}_$${seed}.log; \
		if grep -q "RESULT : PASSED" $$logfile; then \
			echo "$$name (seed=$$seed, verbosity=$$verbosity, timeout_ns=$${timeout_ns}ns) : PASSED" >> $(REPORT_DIR)/regression_summary.log; \
		else \
			echo "$$name (seed=$$seed, verbosity=$$verbosity, timeout_ns=$${timeout_ns}ns) : FAILED" >> $(REPORT_DIR)/regression_summary.log; \
		fi; \
	done
	@echo "==> [regress] Summary:"
	@cat $(REPORT_DIR)/regression_summary.log

# ---------------------------------------------------------------------------
# 6. clean - remove work library, logs and transcript/wlf files
# ---------------------------------------------------------------------------
clean:
	@echo "==> [clean] Removing library, logs, transcripts"
	rm -rf $(LIB)
	rm -f $(LOG_DIR)/*.log
	rm -f $(REPORT_DIR)/*.log
	rm -f transcript *.wlf vsim.wlf
	rm -rf modelsim.ini.bak
