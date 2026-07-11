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

RTL_SRC     := $(RTL_DIR)/counter.sv
TB_SRC      := $(TB_DIR)/counter_tb.sv

# Command-line overridable variables, e.g.:
#   make sim TESTNAME=test1 SEED=1
#   make compile DEFINE=+define+DEBUG
TESTNAME    ?= test1
SEED        ?= 1
DEFINE      ?=

# Regression test list (name:seed). Replace/extend as needed.
# (YAML-driven regression intentionally left out for now.)
TESTS       := test1:1 test2:2 test3:3

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
#    Accepts TESTNAME and SEED from the command line. Questa opens in
#    GUI mode (no -c) and stays open after the run so the waveform
#    is already there for you to inspect - no manual "open .wlf" step.
# ---------------------------------------------------------------------------
sim: opt
	@mkdir -p $(LOG_DIR)
	@echo "==> [sim] Running TESTNAME=$(TESTNAME) SEED=$(SEED)"
	$(VSIM) -lib $(LIB) $(OPT_NAME) \
		-sv_seed $(SEED) \
		+TESTNAME=$(TESTNAME) \
		-l $(LOG_DIR)/sim_$(TESTNAME)_$(SEED).log \
		-wlf /tmp/vsim_$(TESTNAME)_$(SEED).wlf \
		-do "do run.do"
	@rm -f /tmp/vsim_$(TESTNAME)_$(SEED).wlf

# ---------------------------------------------------------------------------
# 5. regress - run sim for every test in TESTS (YAML parsing deferred)
# ---------------------------------------------------------------------------
regress:
	@mkdir -p $(REPORT_DIR)
	@rm -f $(REPORT_DIR)/regression_summary.log
	@for t in $(TESTS); do \
		name=$${t%%:*}; \
		seed=$${t##*:}; \
		echo "==> [regress] Running $$name (seed=$$seed)"; \
		$(MAKE) sim TESTNAME=$$name SEED=$$seed; \
		logfile=$(LOG_DIR)/sim_$${name}_$${seed}.log; \
		if grep -q "RESULT : PASSED" $$logfile; then \
			echo "$$name (seed=$$seed) : PASSED" >> $(REPORT_DIR)/regression_summary.log; \
		else \
			echo "$$name (seed=$$seed) : FAILED" >> $(REPORT_DIR)/regression_summary.log; \
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
