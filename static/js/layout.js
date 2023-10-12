document.addEventListener('DOMContentLoaded', function() {
    countdown()
});

function countdown() {

    // Set the date we're counting down to
    var DownDate = new Date("2023-11-03T18:30:00.000+02:00").getTime();
    var countDownDate = new Date(DownDate);

    // Update the count down every 1 second
    var x = setInterval(function() {

      // Get today's date and time
      var rnow = new Date().getTime();
      var now = new Date(rnow);

      // Find the distance between now and the count down date
      var distance = countDownDate - now;

      // Time calculations for days, hours, minutes and seconds
      var days = Math.floor(distance / (1000 * 60 * 60 * 24));
      var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
      var seconds = Math.floor((distance % (1000 * 60)) / 1000);

      // Output the result in an element with id="countdown"
      document.getElementById("countdown").innerHTML = days + "d " + hours + "h "
      + minutes + "m " + seconds + "s ";

      // If the count down is over, write some text
      if (distance < 0) {
        clearInterval(x);
        document.getElementById("countdown").innerHTML = "It's reveal time!";
      }
    }, 1000);
    };
