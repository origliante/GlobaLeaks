

describe('globaLeaks receiver tip reading', function() {
  var login_receiver = function() {
      browser.get('http://127.0.0.1:8082/login');
      element(by.model('loginUsername')).sendKeys('recv1');
      element(by.model('loginPassword')).sendKeys('qwe2qwe2');
      var cp = element(by.tagName('button')).click();
      browser.sleep(2000);
      return cp;
  }

  it('should redirect to /tips upon successful authentication', function() {
    login_receiver().then(function () {
      expect(browser.getLocationAbsUrl()).toBe('http://127.0.0.1:8082/#/receiver/tips');
    });
  });

  it('should be able to access a tip', function() {
    login_receiver().then(function () {
      element(by.css('.btn-success')).click().then(function() {
        //TODO: check tip text
      });
    });
  });

});



