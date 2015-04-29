

describe('globaLeaks setup receiver(s)', function() {
  it('should allow the admin to add a new receiver', function() {
      browser.get('http://127.0.0.1:8082/admin');
 
      //element(by.model('loginUsername')).sendKeys('admin');
      element(by.model('loginPassword')).sendKeys('qwe2qwe2');
      element(by.css('button')).click().then(function() {
        //TODO: expect admin is logged by checking LoginStatusBox

        browser.setLocation('admin/receivers');
        browser.waitForAngular(); browser.sleep(2000);

        element(by.model('new_receiver.name')).sendKeys('altro');
        element(by.model('new_receiver.email')).sendKeys('altro@altro.xxx');

        element(by.css('[data-ng-click="add_receiver()"]')).click().then(function() {
        });
      });

    });
});
