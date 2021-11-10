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
    $.ajax({
        url: '/api/v1.0/users/auth',
        type: 'get',
        dataType: 'json',
        success: function (resp) {
            if (resp.errno == '0' && resp.data.real_name !== null && resp.data.id_card !== null) {
                $('#real-name').attr('disabled', 'disabled').val(resp.data.real_name);
                $('#id-card').attr('disabled', 'disabled').val(resp.data.id_card);
                $('.btn-success').attr('disabled', 'true');
            }
        }
    });
    $('#form-auth').submit(function (e) {
        e.preventDefault();
        let real_name = $('#real-name').val();
        let id_card = $('#id-card').val();
        let req_data = {
            real_name: real_name,
            id_card: id_card
        }
        let req_json = JSON.stringify(req_data);
        console.log(req_data);
        // 设置实名信息
        $.ajax({
            url: '/api/v1.0/users/auth',
            type: 'patch',
            data: req_json,
            dataType: 'json',
            contentType: 'application/json',
            headers: {'X-CSRFToken': getCookie('csrf_token')},
            success: function (resp) {
                if (resp.errno == '0') {
                    alert(resp.errmsg);
                    window.location.reload();
                }
            }
        })
    })
});