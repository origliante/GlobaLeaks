/*
===============================================================================
Ultra-High Entropy Pseudo Random Number Generator implementation for WINDOWS

This is a Windows scripting version of GRC's web-based uheprng.js code. It
has been simplified and augmented to generate a file (named "uheprng.bin")
of pseudo-random numbers.

To specify the size of the file, set the "MegabytesToGenerate" variable.

To execute this script, launch a Windows command prompt and give the command:

> cscript uheprng.js

The script will continuously show its progress as the pseudo-random numbers
are being generated and accumulated.

Note that the ENTIRE BUFFER of pseudo-random numbers is accumulated in RAM
while the program is running.  This means that the Windows process running
this script will grow in size, consuming memory as needed, until the entire
block of memory has been filled with random numbers, after which it will be
written to the output file, the memory will be released and the script will
terminate.
===============================================================================
*/

"use strict";


//=====================================================================================================================
function uheprng() {
	return (function() {
  		var o = 48;				// set the 'order' number of ENTROPY-holding 32-bit values
		var c = 1;				// init the 'carry' used by the multiply-with-carry (MWC) algorithm
		var p = o;              // init the 'phase' of the intermediate variable pointer
		var s = new Array(o);   // declare our intermediate variables array
		var i, j;                // general purpose locals
		var base64chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

		var mash = uheMash();		// get a pointer to our high-performance "Mash" hash
		for (i = 0; i < o; i++) s[i] = mash( Math.random() );	// fill the array with initial mash hash values
        mash = null;            // release our mash instance of the "Mash" hash

        //=====================================================================================================================		
        var random = function( range ) {
			return Math.floor(range * (rawprng() + (rawprng() * 0x200000 | 0) * 1.1102230246251565e-16)); // 2^-53
		}
        
        //=====================================================================================================================
		function rawprng() {
			if (++p >= o) p = 0;
			var t = 1768863 * s[p] + c * 2.3283064365386963e-10; // 2^-32
      	return s[p] = t - (c = t | 0);
		}
		
		return random;          // when invoked we return a pointer to the anonymous PRNG generator
  }());
};

function uheMash() {
	var n = 0xefc8249d;
	var mash = function(data) {
		if ( data ) {
			data = data.toString();
			for (var i = 0; i < data.length; i++) {
				n += data.charCodeAt(i);
				var h = 0.02519603282416938 * n;
				n = h >>> 0;
				h -= n;
				h *= n;
				n = h >>> 0;
				h -= n;
				n += h * 0x100000000; // 2^32
			}
			return (n >>> 0) * 2.3283064365386963e-10; // 2^-32
		} else n = 0xefc8249d;
	};
  return mash;
}


function generate_receipt() {
    // grab a random number and concatenate it onto the "dataBlock"
    var prng = uheprng();   // instantiate our uheprng for requesting PRNs
    var rnum = '';
    //while (rnum.length < 16) {
    while (rnum.length < 8) {
        //var rnum = prng( 10000000000000000 ).toString();
        var rnum = prng( 100000000 ).toString();
    }
    return rnum;
}

var runs = 100000000 / 5;

while (runs) {
    var r = generate_receipt();
    print(r);
    runs -= 1;
}

