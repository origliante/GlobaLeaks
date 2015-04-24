describe('globaLeaks setup receiver(s)', function() {
  it('should allow the user to setup the wizard', function() {
      browser.get('http://127.0.0.1:8082/admin');
      
      // Go to step 2
      //element(by.css('[data-ng-click="step=step+1"]')).click();
      
      // Fill out the form
      //element(by.model('loginUsername')).sendKeys('admin');
      element(by.model('loginPassword')).sendKeys('Antani1234');

      element(by.css('button')).submit();
      browser.driver.sleep(5000);

      browser.setLocation('admin/receivers');

      element(by.model('new_receiver.name')).sendKeys('altro');
      element(by.model('new_receiver.email')).sendKeys('altro@altro.xxx');

      element(by.css('button')).submit();
      //browser.driver.sleep(5000);

    });
});
