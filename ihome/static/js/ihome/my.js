function logout() {
    $.ajax({
        url: '/api/v1.0/sessions',
        type: 'delete',
        success: function (resp) {
            console.log(resp);
            if (resp.erron == '0') {
                console.log('清除成功');
                location.href = '/';
            } else {
                alert('退出错误');
            }
        }
    })
}

$(document).ready(function () {
})