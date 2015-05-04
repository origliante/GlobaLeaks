function writeScreenShot(data, filename) {
    var fs = require('fs');
    var stream = fs.createWriteStream(filename);

    stream.write(new Buffer(data, 'base64'));
    stream.end();
}



describe('globaLeaks setup', function() {

  it('should allow the user to setup the wizard', function() {
      browser.get('http://127.0.0.1:8082/');
 
      // English is ok - Go to step 2
      element(by.css('[data-ng-click="step=step+1"]')).click().then(function() {

        // Fill out the form
        element(by.model('admin.node.name')).sendKeys('My Node');
        element(by.model('admin.node.description')).sendKeys('My Description');

        element(by.model('admin.node.email')).sendKeys('info@globaleaks.org');

        element(by.model('admin.node.password')).sendKeys('qwe2qwe2');
        element(by.model('admin.node.check_password')).sendKeys('qwe2qwe2');

        element(by.model('receiver.name')).sendKeys('recv1');
        element(by.model('receiver.mail_address')).sendKeys('info@globaleaks.org');

        // Disable encryption for receiver
        element(by.model('admin.node.allow_unencrypted')).click();
        element(by.css('[data-ng-click="ok()"]')).click();

        element(by.model('context.name')).sendKeys('My Context');

        // Complete the form
        element.all(by.css('[data-ng-click="step=step+1"]')).get(1).click();

        // Make sure the congratulations text is present
        expect(element(by.css('.congratulations')).isPresent()).toBe(true) 

        element(by.css('[data-ng-click="finish()"]')).click().then(function() {
        });

      });

    });

    it('should grant access to the admin interface', function() {
      browser.get('http://127.0.0.1:8082/admin');

      element(by.model('loginPassword')).sendKeys('qwe2qwe2');
      element(by.css('button')).click().then(function () {

        // Edit the advanced settings for development
        browser.setLocation('admin/advanced_settings');
        browser.waitForAngular(); browser.sleep(2000);

        element(by.model('admin.node.disable_privacy_badge')).click();
        element(by.model('admin.node.disable_security_awareness_questions')).click();
        element(by.cssContainingText("a", "Tor2web Settings")).click();
        element(by.model('admin.node.tor2web_receiver')).click();
        element(by.model('admin.node.tor2web_submission')).click();
        element(by.css('[data-ng-click="updateNode(admin.node)"]')).click();

      });
    });

});


