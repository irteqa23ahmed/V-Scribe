$(document).ready(function(){
  $("*").click(function(event){
    event.stopPropagation();
    window.location.href="{{url_for('verify',post=1)}}";
    })
  });
