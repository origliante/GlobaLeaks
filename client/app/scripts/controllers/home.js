GLClient.controller('HomeCtrl', ['$scope', '$location', '$modal',
                    'Authentication',
                    'WBReceipt', 'Contexts', 'Receivers',
  function ($scope, $location, $modal, Authentication, WBReceipt, Contexts, Receivers) {
    $scope.keycode = '';
    $scope.configured = false;
    $scope.step = 1;
    $scope.answer = {value: null};
    $scope.answered = false;
    $scope.correctAnswer = false;
    $scope.showQuestions = false;

    var open_quiz = function () {
      var modalInstance = $modal.open({
        templateUrl: 'views/partials/security_awareness_quiz.html',
        controller: 'QuizCtrl',
        size: 'lg',
        scope: $scope
      });
    };

    $scope.goToSubmission = function () {
      if (!$scope.anonymous && !$scope.node.tor2web_submission) {
        return;
      }
      // Before showing the security awareness panel
      if ($scope.anonymous ||
          $scope.node.disable_security_awareness_badge) {
        $location.path("/submission");
      } else {
        open_quiz();
      }
    };
    
}]);


GLClient.controller('QuizCtrl', ['$scope', '$modalInstance', '$location',
                    function($scope, $modalInstance, $location) {
  $scope.goToSubmission = function() {
    // After showing the security awareness panel
    if ($scope.node.disable_security_awareness_questions ||
        $scope.answer.value === 'b') {
      $modalInstance.close();
      $location.path("/submission");
    }
  };

  $scope.cancel = function () {
    $modalInstance.close();
  };

}]);
