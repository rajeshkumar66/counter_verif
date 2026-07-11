
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

# NOTE: no `quit` here on purpose - Questa's GUI stays open afterwards
# so you can view the waveform. Close the window yourself when done,
# or type `quit -f` at the Questa command prompt.
