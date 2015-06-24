$(function(){
    var account_id;
    var service;
    var e = $("#auth-launch");

    Kloudless.authenticator(
        e,
        {'app_id': app_id},
        function(err, result) {
            if (err) {
                console.error('An error occurred: ', err);
                return;
            }
            account_id = result.id;
            service = result.service;
            $("#auth-form [name='account_id']").val(account_id);
            $("#auth-form").submit();
            console.log('Yay! I now have a newly authenticated', service, 'account with id: ', account_id);
        }
    );

    $("#auth-launch").click(function(){
        console.log('Auth button was clicked.');
    });

    $("#search-launch").click(function(){
        console.log('Search button was clicked.');
    });

});