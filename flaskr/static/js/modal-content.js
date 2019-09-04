$(function(){
	$(".card-body #modal").click(function(){
		$("#detail-content").html($(this).find("#hidden-detail").html());
	})
	$('#sbox').keypress(function (e) {
  		if (e.which == 13) {
    		window.location.href = '/q/'+$("#sbox").val();
  		}
	})
})