function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function () {
        setTimeout(function () {
            $('.popup_con').fadeOut('fast', function () {
            });
        }, 1000)
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    $("#form-avatar").submit(function (e) {
        // 阻止表单默认行为
        e.preventDefault();
        // 利用jquery.form.min.js 提供的ajaxSubmit对表单进行异步提交
        $(this).ajaxSubmit({
            url: '/api/v1.0/users/avatar',
            type: 'post',
            dataType: 'json',
            headers: {'X-CSRFToken': getCookie('csrf_token')},
            success: function (resp) {
                if (resp.errno == '0') {
                    // 上传成功
                    let avatarUrl = resp.data.avatar_url;
                    $('#user-avatar').attr('src', avatarUrl);
                } else {
                    alert(resp.errmsg);
                }
            }
        })
    });
    $('#form-name').submit(function (e) {
        // 阻止表单默认提交行为
        e.preventDefault();
        let name = $('#user-name').val();
        var req_data = {name: name};
        var req_json = JSON.stringify(req_data);
        $.ajax({
            url: '/api/v1.0/users/name',
            type: 'put',
            data: req_json,
            dataType: 'json',
            contentType: 'application/json',
            headers: {'X-CSRFToken': getCookie('csrf_token')},
            success: function (resp) {
                if (resp.errno == '0') {
                    let ret = resp.errmsg;
                    console.log(ret);
                } else {
                    alert('修改失败');
                }
            }
        })
    })
    $.ajax({
        url: '/api/v1.0/user',
        type: 'get',
        dataType: 'json',
        success: function (resp) {
            console.log(resp.data.name);
            if (resp.errno == '0') {
                ;
                $('#user-name').val(resp.data.name);
                $('#user-avatar').attr('src', resp.data.avatar);
            }
        }
    });
})