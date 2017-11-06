$(document).ready(function() {

  function hideLoginButton() {
    $('#signinButton').hide();
    $('#userInfo').show();
  }

  function showLoginButton() {
    $('#signinButton').show();
    $('#userInfo').hide();
  }
  
  if (loggedIn=='null'||loggedIn=='') {
    showLoginButton();
  }
  else {
    hideLoginButton();
  }


});
