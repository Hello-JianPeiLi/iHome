function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');
    // 页面加载好久获取城区信息
    $.get('/api/v1.0/areas', function (resp) {
        if (resp.errno == '0') {
            let areas = resp.data;
            let html = template('areas-tmp', {areas: areas});
            $('#area-id').html(html);
            // for (var i = 0; i < areas.length; i++) {
            //     let area = areas[i];
            //     $('#area-id').append("<option value="+area.aid+">"+area.aname+"</option>");
            // }
        } else {
            alert(resp.errmsg);
        }

    }, 'json');
    $('#form-house-info').submit(function (e) {
        e.preventDefault();
        // 处理表单数据
        let data = {};
        $('#form-house-info').serializeArray().map(function (x) {
            data[x.name] = x.value;
        });
        let facilities = [];
        $(':checked[name="facility"]').each(function (index, x) {
            facilities[index] = $(x).val();
        });
        data.facility = facilities;
        // 发送接口数据
        $.ajax({
            url: '/api/v1.0/houses/info',
            type: 'post',
            dataType: 'json',
            data: JSON.stringify(data),
            contentType: 'application/json',
            heasers: {'X-CSRFToken': getCookie('csrf_token')},
            success: function (resp) {
                if (resp.errno == '4101') {
                    // 用户未登录
                    location.href = '/login.html';
                } else if (resp.errno == '0') {
                    // 隐藏基本信息表单
                    $('#form-house-info').hide();
                    // 显示图片表单
                    $('#form-house-image').show();
                    // 设置图片表单中的house_id
                    $('#house-id').val(resp.data.house_id);
                }
            }
        });
        $('#form-house-image').submit(function (e) {
            e.preventDefault();
            $(this).ajaxSubmit({
                url: '/api/v1.0/houses/image',
                type: 'post',
                dataType: 'json',
                headers: {'X-CSRFToken': getCookie('csrf_token')},
                success: function (resp) {
                    if (resp.errno == '4101') {
                        location.href = '/login.html';
                    } else if (resp.errno == '0') {
                        $('.house-image-cons').append('<img src="' + resp.data.image_url + '">');
                    } else {
                        alert(resp.errmsg);
                    }
                }
            })
        })

    });
})