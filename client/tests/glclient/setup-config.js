exports.config = {
  seleniumAddress: 'http://localhost:4444/wd/hub',
  specs: [
    'setup-wizard.js',
    //'setup-receivers.js',
    //'receiver-first-login.js',
  ],
  capabilities: {
    'browserName': 'chrome' // or 'safari'
  },
  framework: 'jasmine',
  jasmineNodeOpts: {
    defaultTimeoutInterval: 30000
  },

  onPrepare: function() {
     browser.driver.manage().window().setSize(1200, 600);
  },
}

