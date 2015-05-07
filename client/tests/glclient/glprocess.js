
describe('globaLeaks gl process', function() {
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

  var tip_text = 'test GL process';
  var receipt = '';

  var login_wb = function() {
    browser.get('http://127.0.0.1:8082/#/');
    element(by.model('formatted_keycode')).sendKeys( receipt );
    var cp = element(by.css('[data-ng-click="view_tip(formatted_keycode)"]')).click();
    return cp;
  }

  var login_receiver = function() {
    browser.get('http://127.0.0.1:8082/login');
    element(by.model('loginUsername')).sendKeys('recv1');
    element(by.model('loginPassword')).sendKeys('qwe2qwe2');
    var cp = element(by.tagName('button')).click();
    browser.sleep(2000);
    return cp;
  }


  it('WB should be able to submit a tip', function() {
    browser.get('http://127.0.0.1:8082/#/submission');
    element(by.id('receiver_checkbox_recv1')).click().then(function () {
      element(by.css('[data-ng-click="incrementStep()"]')).click().then(function () {
        element(by.tagName('textarea')).sendKeys( tip_text ).then(function () {
          element(by.css('[data-ng-click="incrementStep()"]')).click().then(function () {
            element(by.css('div.checkbox input')).click().then(function() {
              element(by.css('[data-ng-click="submit()"]')).click().then(function() {
                browser.sleep(10000);
                expect(browser.getLocationAbsUrl()).toBe('http://127.0.0.1:8082/#/receipt');
                receipt = element(by.id('KeyCode')).getText();
              });
            });
          });
        });
      });
    });
  });

  it('WB should be able to access the submission', function() {
    login_wb().then(function () {
      browser.sleep(7000);
      //FIXME: by.text custom implementation does not find it
      expect(element(by.text( tip_text )).isPresent()).toBeTruthy();
    });
  });

  it('RECEIVER should be able to access the submitted tip', function() {
    login_receiver().then(function () {
      element(by.css('.btn-success')).click().then(function() {
        //TODO: check tip text
        expect(1).toBe(0);
      });
    });
  });

  it('RECEIVER should be able to send a private message to the WB', function() {
    login_receiver().then(function () {
      element(by.css('.btn-success')).click().then(function() {
        //TODO: send priv message
        expect(1).toBe(0);
      });
    });
  });

  it('WB should be able to read the private message from the RECEIVER and respond', function() {
    login_wb().then(function () {
      //TODO: read priv mess and send it
      expect(1).toBe(0);
    });
  });

  it('WB should be able to attach a new file to the tip', function() {
    login_wb().then(function () {
      //TODO: attach new file
      expect(1).toBe(0);
    });
  });

  it('RECEIVER should be able to download the new attached file', function() {
    login_receiver().then(function () {
      element(by.css('.btn-success')).click().then(function() {
        //TODO: download new file
        expect(1).toBe(0);
      });
    });
  });

  it('RECEIVER should be able to postpone a tip', function() {
    login_receiver().then(function () {
      element(by.css('.btn-success')).click().then(function() {
        //TODO: postpone a tip
        expect(1).toBe(0);
      });
    });
  });

  it('RECEIVER should be able to delete a tip', function() {
    login_receiver().then(function () {
      element(by.css('.btn-success')).click().then(function() {
        //TODO: delete a tip
        expect(1).toBe(0);
      });
    });
  });
});


