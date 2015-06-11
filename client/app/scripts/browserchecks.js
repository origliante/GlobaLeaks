
var isBrowserCompatible = function() {
  return !(bowser.msie && bowser.version <= 8);
};

var isBrowserSupported = function() {
  if (typeof window !== 'undefined' && window.crypto) {
    return !!(window.crypto.subtle || window.crypto.webkitSubtle);
  }
  return false;
}

