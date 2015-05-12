var path = require('path');


describe('globaLeaks gl process', function() {
  var tip_text = 'test GL process';
  var receipt = '';
  var test_message = 'test message';
  var test_message_response = 'test message response';
  var scrypt_sleep = 15000;


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
                browser.sleep(scrypt_sleep);
                expect(browser.getLocationAbsUrl()).toBe('http://127.0.0.1:8082/#/receipt');
                receipt = element(by.id('KeyCode')).getText();
              });
            });
          });
        });
      });
    });
  });

  it('WB should be able to access the submitted tip', function() {
    browser.get('http://127.0.0.1:8082/#/');
    element(by.model('formatted_keycode')).sendKeys( receipt ); element(by.css('[data-ng-click="view_tip(formatted_keycode)"]')).click().then(function () {
      browser.sleep(scrypt_sleep);
      expect(element( by.xpath("//*[contains(text(),'" + tip_text + "')]") ).getText()).toEqual(tip_text);
    });
  });

  it('RECEIVER should be able to access the submitted tip', function() {
    login_receiver().then(function () {
      element(by.css('.btn-success')).click().then(function() {
        expect(element(by.xpath("//*[contains(text(),'" + tip_text + "')]") ).getText()).toEqual(tip_text);
      });
    });
  });

  it('RECEIVER should be able to send a private message to the WB', function() {
    login_receiver().then(function () {
      element(by.css('.btn-success')).click().then(function() {
        element(by.model('tip.newMessageContent')).sendKeys(test_message);
        element(by.css('[data-ng-click="newMessage()"]')).click().then(function() {
          element(by.css('.preformatted')).getText().then(function(newMsg) {
            expect(newMsg).toContain('-----BEGIN PGP MESSAGE-----');
          });
        });
      });
    });
  });

  it('WB should be able to read the private message from the RECEIVER and respond', function() {
    login_wb().then(function () {
      element(by.id('recv_message_content')).getText().then(function(message) {
        expect(message).toEqual(test_message);
      });
      element(by.model('tip.newMessageContent')).sendKeys(test_message_response);
      element(by.css('[data-ng-click="newMessage()"]')).click().then(function() {
        element(by.css('.preformatted')).getText().then(function(newMsg) {
          expect(newMsg).toContain('-----BEGIN PGP MESSAGE-----');
        });
      });
    });
  });

  it('WB should be able to attach a new file to the tip', function() {
    login_wb().then(function () {
      var fileToUpload = './glprocess.js',
      absolutePath = path.resolve(__dirname, fileToUpload);
      $$('input[type="file"]').sendKeys(absolutePath); 
      browser.sleep(2000);
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
        element(by.css('[data-ng-show="tip.can_postpone_expiration"]')).element(by.tagName('i')).click().then(function () {
          element(by.css('.modal-footer')).element(by.css('.btn-danger')).click().then(function() {
            //TODO: check new date
          });
        });
      });
    });
  });

  it('RECEIVER should be able to delete a tip', function() {
    login_receiver().then(function () {
      element(by.css('.btn-success')).click().then(function() {
        element(by.css('[data-ng-show="tip.can_delete_submission"]')).element(by.tagName('span')).click().then(function () {
          element(by.css('.modal-footer')).element(by.css('.btn-danger')).click().then(function() {
            //TODO: check if list is shorter
          });
        });
      });
    });
  });
});


