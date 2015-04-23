
function waitForPromiseTest(promiseFn, testFn) {
  browser.wait(function () {
    var deferred = protractor.promise.defer();
    promiseFn().then(function (data) {
      deferred.fulfill(testFn(data));
    });
    return deferred.promise;
  });
}

function writeScreenShot(data, filename) {
    var fs = require('fs');
    var stream = fs.createWriteStream(filename);

    stream.write(new Buffer(data, 'base64'));
    stream.end();
}


describe('globaLeaks setup first receiver login', function() {
  it('should redirect to /firstlogin upon successful authentication', function() {
      browser.get('http://127.0.0.1:8082/login');
      browser.driver.sleep(1000);

      element(by.model('loginUsername')).sendKeys('Beppa Pigga');
      element(by.model('loginPassword')).sendKeys('globaleaks');
      element(by.tagName('button')).click().then(function () {
        browser.driver.sleep(5000);
        expect(browser.getLocationAbsUrl()).toBe('http://127.0.0.1:8082/#/receiver/firstlogin');
      });
      //browser.takeScreenshot().then(function (png) { writeScreenShot(png, 'exception.png'); });

  });

  it('should change password from default globaleaks to qwe2qwe2', function() {
      browser.get('http://127.0.0.1:8082/login');
      browser.driver.sleep(1000);

      element(by.model('loginUsername')).sendKeys('Beppa Pigga');
      element(by.model('loginPassword')).sendKeys('globaleaks');
      element(by.tagName('button')).click().then(function () {
        browser.driver.sleep(5000);
        expect(browser.getLocationAbsUrl()).toBe('http://127.0.0.1:8082/#/receiver/firstlogin');
      });

      element(by.model('preferences.old_password')).sendKeys('globaleaks');
      element(by.model('preferences.password')).sendKeys('qwe2qwe2');
      element(by.model('preferences.check_password')).sendKeys('qwe2qwe2');
      element(by.tagName('button')).click().then(function () {
        browser.driver.sleep(5000);
        expect(browser.getLocationAbsUrl()).toBe('http://127.0.0.1:8082/#/receiver/tips');
      });

  });

});



