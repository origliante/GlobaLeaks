
exports.config = {
  seleniumAddress: 'http://localhost:4444/wd/hub',

  troubleshoot: true,
  directConnect: true,

  specs: [
    'setup-node-devel.js',
    'setup-receivers.js',
  ],

  capabilities: {
    'browserName': 'chrome'
    //'browserName': 'firefox',
    // or 'safari'
  },

  framework: 'jasmine2',

  jasmineNodeOpts: {
   isVerbose: true,
   //defaultTimeoutInterval: 30000
  },

  baseUrl: 'http://127.0.0.1:8082/',

  onPrepare: function() {
     browser.driver.manage().window().setSize(1200, 600);
  },
}


