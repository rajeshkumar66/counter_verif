`timescale 1ns/1ps

module counter_tb;

  logic clk;
  logic rst_n;
  logic en;
  logic up_down;
  logic [3:0] count;
  logic [3:0] exp_count;
  int error_count = 0;

  counter dut(
    .clk(clk),
	.rst_n(rst_n),
	.en(en),
	.up_down(up_down),
	.count(count)
  );

  initial clk = 0;

  always #5 clk = ~clk; 

  initial begin
    rst_n     = 0;
	en        = 0;
	up_down   = 0;
	exp_count = 0;

	#20 rst_n     = 1;       
	en        = 1;
	repeat(5) begin
	  @(posedge clk);
	  #1;
	  if(up_down) exp_count = exp_count + 1'b1;
	  else 	      exp_count = exp_count - 1'b1;

	  `ifdef DEBUG
	    $display("UVM_INFO: [DEBUG] time=%t clk=%b rst_n=%b en=%b count=%d", $time, clk, rst_n, en, count);
      `endif 

	  if(count==exp_count) begin      
	    $display("UVM_INFO: Match count=%d exp=%d time=%0t", count, exp_count, $time);
	  end
	  else begin
	    $display("UVM_ERROR: Mismatch count=%d exp=%d time=%t", count, exp_count, $time);
		error_count;
	  end 
	end 

	if(error_count == 0)
	  $display("TEST_CASE: counter_test RESULT : PASSED");
	else
	  $display("TEST_CASE: counter_test RESULT : FAILED");

	$display("UVM_WARNING: End of test reached, review waveform for timing.");
	$finish;
  end

endmodule  
