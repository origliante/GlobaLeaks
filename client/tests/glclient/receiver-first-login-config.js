// conf.js
exports.config = {
  seleniumAddress: 'http://localhost:4444/wd/hub',
  specs: [
    //'setup-wizard.js',
    'receiver-first-login.js',
  ],
  capabilities: {
    'browserName': 'firefox' // or 'safari'
  },
}

