describe('globaLeaks setup receiver(s)', function() {
  it('should allow the user to setup the wizard', function() {
      browser.get('http://127.0.0.1:8082/login');
      
      // Go to step 2
      //element(by.css('[data-ng-click="step=step+1"]')).click();
      
      // Fill out the form
      element(by.model('loginUsername')).sendKeys('Beppa Pigga');
      element(by.model('loginPassword')).sendKeys('globaleaks');

      element(by.css('[data-ng-click="login(loginUsername, loginPassword, loginRole)"]')).submit();

      expect(browser.getLocationAbsUrl())
        .toBe('http://127.0.0.1:8082/#/receiver/firstlogin');

      /*
      // Complete the form
      element.all(by.css('[data-ng-click="step=step+1"]')).get(1).click();
      // Make sure the congratulations text is present
      expect(element(by.css('.congratulations')).isPresent()).toBe(true) 
      // Go to admin interface
      element(by.css('[data-ng-click="finish()"]')).click();
      element(by.css('[data-ng-click="updateNode(admin.node)"]')).click();
      */
    });
});
