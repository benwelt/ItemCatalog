$(document).ready(function() {

  function showLoggedInButtons() {
    $('#signinButton').hide();
    $('#userInfo').show();
    $('.newBikeButton').show();
    $('.editBikeButton').show();
    $('.deleteBikeButton').show();
  }

  function showLoggedOutButtons() {
    $('#signinButton').show();
    $('#userInfo').hide();
    $('.newBikeButton').hide();
    $('.editBikeButton').hide();
    $('.deleteBikeButton').hide();
  }

  if (loggedIn=='null'||loggedIn=='') {
    showLoggedOutButtons();
  }
  else {
    showLoggedInButtons();
  }

  window.setTimeout(function() {
    $('.flask-alert').delay(2000).fadeOut(800, function() {
      $(this).alert('close');
    });
  })

});
