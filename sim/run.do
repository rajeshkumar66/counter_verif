
#=============================================================================
# run.do - Questa simulation script
# Adds the top-level testbench signals to the waveform, runs the
# simulation to completion, and leaves the Questa GUI open so the
# waveform can be inspected immediately (no manual .wlf loading step).
#=============================================================================

# Don't stop the run on runtime errors/assertions; just resume
onerror {resume}

# Add only the top-level signals of the testbench (non-recursive)
add wave -noupdate /counter_tb/*

# Cosmetic waveform settings
configure wave -namecolwidth 200
configure wave -valuecolwidth 100
configure wave -signalnamewidth 1

# Run the simulation to completion
run -all

# Zoom the wave window to show the full run
wave zoom full

# Only auto-quit when invoked from `make regress` (BATCH_MODE=1 is set by
# the Makefile in that case). A plain interactive `make sim` leaves the
# Questa GUI open so you can inspect the waveform.
if {[info exists ::env(BATCH_MODE)] && $::env(BATCH_MODE) eq "1"} {
    quit -f
}
