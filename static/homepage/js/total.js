  function action(cart_id, action_name) {
      $.ajax({
      url: $('#row_' + cart_id).attr("data-url"), 
      method: 'POST',
      data: {
        cart_item_id: cart_id,
        action: action_name,
        csrfmiddlewaretoken: $('#row_' + cart_id).attr("data-csrf"), 
      },
      success: function(data) {
        if (data.status === 2) {
          alert('Xóa sản phẩm thành công');          
          $('#row_' + cart_id).remove();
          total_price = data.total_price
          var total =  Number(data.total_price)
          var formattedTotalPrice = formatCurrency(total)   
          $('#total_price').text(formattedTotalPrice);
          return
        }
        if (data.status === 1) {
          // Cập nhật số lượng sản phẩm trên giao diện người dùng
          $('#quantity_' + cart_id).text(data.quantity);
          var total =  Number(data.total_price)
          var formattedTotalPrice = formatCurrency(total)   
          $('#total_price').text( formattedTotalPrice);

        } else {
          // Hiển thị thông báo lỗi nếu cần
          alert('Cập nhật không thành công: ' + data.message);
        }
      },
      error: function(error) {
        alert('Đã xảy ra lỗi: ' + error.responseText);
      }
    });
}
function formatCurrency(amount, currency = 'VND') {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: currency }).format(amount);
}
