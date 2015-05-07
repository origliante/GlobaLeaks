

describe('globaLeaks first receiver login', function() {
  it('should redirect to /firstlogin upon successful authentication', function() {
      browser.get('http://127.0.0.1:8082/login');
      element(by.model('loginUsername')).sendKeys('recv1');
      element(by.model('loginPassword')).sendKeys('globaleaks');
      element(by.tagName('button')).click().then(function () {
        browser.sleep(2000);
        expect(browser.getLocationAbsUrl()).toBe('http://127.0.0.1:8082/#/receiver/firstlogin');
      });
  });

  it('should be able to change password from default globaleaks to qwe2qwe2', function() {
    browser.get('http://127.0.0.1:8082/login');
    element(by.model('loginUsername')).sendKeys('recv1');
    element(by.model('loginPassword')).sendKeys('globaleaks');
    element(by.tagName('button')).click().then(function () {
        browser.sleep(2000);
        expect(browser.getLocationAbsUrl()).toBe('http://127.0.0.1:8082/#/receiver/firstlogin');
    });

    element(by.model('preferences.old_password')).sendKeys('globaleaks');
    element(by.model('preferences.password')).sendKeys('qwe2qwe2');
    element(by.model('preferences.check_password')).sendKeys('qwe2qwe2');
    element(by.css('[data-ng-click="pass_save()"]')).click().then(function () {
      browser.sleep(2000);
      expect(browser.getLocationAbsUrl()).toBe('http://127.0.0.1:8082/#/receiver/tips');
      //TODO: check for existence of e2e pgp keys
      //element(by.id('tipList')).evaluate('ww_gl_passphrase').then(function(val) {
    });
  });

  it('should be able to login with the new password', function() {
    browser.get('http://127.0.0.1:8082/login');
    element(by.model('loginUsername')).sendKeys('recv1');
    element(by.model('loginPassword')).sendKeys('qwe2qwe2');
    element(by.tagName('button')).click().then(function () {
      browser.sleep(2000);
      expect(browser.getLocationAbsUrl()).toBe('http://127.0.0.1:8082/#/receiver/tips');
    });
  });
});



