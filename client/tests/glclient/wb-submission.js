
describe('globaLeaks wb submission', function() {
  var findByText = function() {
      var using = arguments[0] || document;
      var text = arguments[1];
      var matches = [];
      function addMatchingLeaves(element) {
        if (element.children) {
          if (element.children.length === 0 && element.textContent.match(text)) {
            matches.push(element);
          }
          for (var i = 0; i < element.children.length; ++i) {
            addMatchingLeaves(element.children[i]);
          }
        }
      }
      addMatchingLeaves(using);
      return matches;
  };
  by.addLocator('text', findByText);

  var tip_text = 'test submission 1';
  var receipt = '';


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

  it('should be able to submit a tip', function() {
    browser.get('http://127.0.0.1:8082/#/submission');
    element(by.id('receiver_checkbox_recv1')).click().then(function () {
      element(by.css('[data-ng-click="incrementStep()"]')).click().then(function () {
        element(by.tagName('textarea')).sendKeys( tip_text ).then(function () {
          element(by.css('[data-ng-click="incrementStep()"]')).click().then(function () {
            element(by.css('div.checkbox input')).click().then(function() {
              element(by.css('[data-ng-click="submit()"]')).click().then(function() {

                browser.sleep(7000);
                expect(browser.getLocationAbsUrl()).toBe('http://127.0.0.1:8082/#/receipt');
                receipt = element(by.id('KeyCode')).getText();
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
      browser.sleep(7000);
      //FIXME: by.text custom implementation does not find it
      expect(element(by.text( tip_text )).isPresent()).toBeTruthy();
    });
  });

});



