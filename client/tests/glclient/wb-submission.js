var path = require('path');

describe('globaLeaks wb submission', function() {
  var tip_text = 'test submission 1';
  var receipt = '';


  it('should redirect to /submission by clicking on the blow the whisle button', function() {
    browser.get('http://127.0.0.1:8082/#/'); element(by.css('[data-ng-click="goToSubmission()"]')).click().then(function () {
      element(by.css('.btn-warning')).click().then(function () {
        browser.sleep(2000);
        expect(browser.getLocationAbsUrl()).toBe('http://127.0.0.1:8082/#/submission');
      });
    });
  });


  it('should be able to submit a tip', function() {
    browser.get('http://127.0.0.1:8082/#/submission');

    element(by.id('receiver_checkbox_recv1')).click().then(function () {
      element(by.css('[data-ng-click="incrementStep()"]')).click().then(function () {

        element(by.tagName('textarea')).sendKeys( tip_text ).then(function () {

          var fileToUpload = './wb-submission.js',
          absolutePath = path.resolve(__dirname, fileToUpload);
          $('input[type="file"]').sendKeys(absolutePath);  

          element(by.css('[data-ng-click="incrementStep()"]')).click().then(function () {
            element(by.css('div.checkbox input')).click().then(function() {
              element(by.css('[data-ng-click="submit()"]')).click().then(function() {

                browser.sleep(15000);

                expect(browser.getLocationAbsUrl()).toBe('http://127.0.0.1:8082/#/receipt');

                element(by.id('KeyCode')).getText().then(function (txt) {
                  receipt = txt;
                });

              });
            });
          });
        });
      });
    });
  });


  it('should be able to access the submission', function() {
    browser.get('http://127.0.0.1:8082/#/');
    element(by.model('formatted_keycode')).sendKeys( receipt );
    element(by.css('[data-ng-click="view_tip(formatted_keycode)"]')).click().then(function () {
      browser.sleep(15000);
      expect(element( by.xpath("//*[contains(text(),'" + tip_text + "')]") ).getText()).toEqual(tip_text);
    });
  });


});



