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

})