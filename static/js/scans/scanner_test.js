/**
 * Scanner Test - Debug tool for camera and ZXing functionality
 */

(function() {
    'use strict';
    
    console.log('Scanner Test loaded');
    
    // Test ZXing library loading
    function testZXing() {
        console.log('Testing ZXing library...');
        
        const ZX = window.ZXing || (typeof ZXing !== 'undefined' ? ZXing : null);
        console.log('ZXing object:', ZX);
        
        if (ZX && ZX.BrowserMultiFormatReader) {
            console.log('✅ ZXing library loaded successfully');
            try {
                const reader = new ZX.BrowserMultiFormatReader();
                console.log('✅ ZXing reader created successfully');
                return true;
            } catch (err) {
                console.error('❌ Error creating ZXing reader:', err);
                return false;
            }
        } else {
            console.error('❌ ZXing library not loaded');
            return false;
        }
    }
    
    // Test camera access
    async function testCamera() {
        console.log('Testing camera access...');
        
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            console.error('❌ Camera API not supported');
            return false;
        }
        
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            console.log('✅ Camera access granted');
            
            // List available devices
            const devices = await navigator.mediaDevices.enumerateDevices();
            const videoDevices = devices.filter(device => device.kind === 'videoinput');
            console.log('Available cameras:', videoDevices);
            
            // Stop the stream
            stream.getTracks().forEach(track => track.stop());
            return true;
        } catch (err) {
            console.error('❌ Camera access denied:', err);
            return false;
        }
    }
    
    // Test DOM elements
    function testDOMElements() {
        console.log('Testing DOM elements...');
        
        const elements = {
            'startBtn': document.getElementById('start-scan'),
            'stopBtn': document.getElementById('stop-scan'),
            'videoElem': document.getElementById('video-preview'),
            'barcodeInput': document.getElementById('barcode'),
            'scanForm': document.getElementById('scan-form'),
            'submitBtn': document.getElementById('submit-btn')
        };
        
        let allFound = true;
        for (const [name, element] of Object.entries(elements)) {
            if (element) {
                console.log(`✅ ${name} found`);
            } else {
                console.error(`❌ ${name} not found`);
                allFound = false;
            }
        }
        
        return allFound;
    }
    
    // Run all tests
    async function runTests() {
        console.log('=== SCANNER TESTS ===');
        
        const tests = [
            { name: 'DOM Elements', test: testDOMElements },
            { name: 'ZXing Library', test: testZXing },
            { name: 'Camera Access', test: testCamera }
        ];
        
        const results = {};
        
        for (const test of tests) {
            console.log(`\n--- Testing ${test.name} ---`);
            try {
                results[test.name] = await test.test();
            } catch (err) {
                console.error(`Error in ${test.name}:`, err);
                results[test.name] = false;
            }
        }
        
        console.log('\n=== TEST RESULTS ===');
        for (const [name, result] of Object.entries(results)) {
            console.log(`${result ? '✅' : '❌'} ${name}: ${result ? 'PASS' : 'FAIL'}`);
        }
        
        const allPassed = Object.values(results).every(result => result);
        console.log(`\nOverall: ${allPassed ? '✅ ALL TESTS PASSED' : '❌ SOME TESTS FAILED'}`);
        
        return results;
    }
    
    // Make test function globally available
    window.runScannerTests = runTests;
    
    // Auto-run tests when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(runTests, 1000); // Wait 1 second for everything to load
        });
    } else {
        setTimeout(runTests, 1000);
    }
    
})();
