

describe('globaLeaks wb submission', function() {
  it('should redirect to /submission by clicking on the blow the whisle button', function() {
    browser.get('http://127.0.0.1:8082/#/');

    element(by.css('[data-ng-click="goToSubmission()"]')).click().then(function () {
      browser.sleep(1000);
      element(by.css('.btn-warning')).click().then(function () {
        browser.sleep(2000);
        expect(browser.getLocationAbsUrl()).toBe('http://127.0.0.1:8082/#/submission');
      });
    });
     
  });

  it('should change password from default globaleaks to qwe2qwe2', function() {
    browser.get('http://127.0.0.1:8082/#/submission');

    element(by.id('receiver_checkbox_recv1')).click().then(function () {
      element(by.css('[data-ng-click="incrementStep()"]')).click().then(function () {
        element(by.tagName('textarea')).sendKeys('test submission 1').then(function () {
          element(by.css('[data-ng-click="incrementStep()"]')).click().then(function () {
            element(by.css('div.checkbox input')).click().then(function() {
              element(by.css('[data-ng-click="submit()"]')).click().then(function() {

                browser.sleep(5000);
                expect(browser.getLocationAbsUrl()).toBe('http://127.0.0.1:8082/#/receipt');

              });
            });
          });

        });

      });

    });

  });

});



