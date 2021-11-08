function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    $("#mobile").focus(function () {
        $("#mobile-err").hide();
    });
    $("#password").focus(function () {
        $("#password-err").hide();
    });
    $(".form-login").submit(function (e) {
        e.preventDefault();
        mobile = $("#mobile").val();
        password = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        }
        if (!password) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        let data = {
            mobile: mobile,
            password: password
        }
        let jsonData = JSON.stringify(data);
        $.ajax({
            url: '/api/v1.0/sessions',
            type: 'post',
            data: jsonData,
            contentType: 'application/json',
            dataType: 'json',
            headers: {
                'X-CSRFToken': getCookie('csrf_token')
            },
            success: function (data) {
                if (data.errno == '0') {
                    location.href = '/';
                } else {
                    // 其他错误信息，在页面展示
                    $('#password-err span').html(data.errmsg);
                    $('#password-err').show();
                }
            }
        })
    });
})