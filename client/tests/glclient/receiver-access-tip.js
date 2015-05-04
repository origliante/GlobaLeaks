

describe('globaLeaks receiver tip reading', function() {
  it('should redirect to /tips upon successful authentication', function() {
      browser.get('http://127.0.0.1:8082/login');

      element(by.model('loginUsername')).sendKeys('recv1');
      element(by.model('loginPassword')).sendKeys('qwe2qwe2');
      element(by.tagName('button')).click().then(function () {
        browser.sleep(2000);
        expect(browser.getLocationAbsUrl()).toBe('http://127.0.0.1:8082/#/receiver/tips');
      });
  });

  it('should be able to access a tip', function() {
      browser.get('http://127.0.0.1:8082/login');

      element(by.model('loginUsername')).sendKeys('recv1');
      element(by.model('loginPassword')).sendKeys('qwe2qwe2');
      element(by.tagName('button')).click().then(function () {
        browser.sleep(2000);
        //element(by.id('tipListTableBody')).element(by.tagName('a')).click().then(function() {
        //FIXME
        element(by.css('tip_open')).click().then(function() {
          browser.pause();
        });
      });

  });

});



