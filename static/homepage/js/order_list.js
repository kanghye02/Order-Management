$(document).ready(function () {
    var currentUrl = window.location.href;

    if (currentUrl.endsWith('/yourorder/') || currentUrl.endsWith('/admin/order/')) {
        var separator = currentUrl.includes('?') ? '&' : '?';
        var newUrl = currentUrl + separator + 'status=all';
        window.location.href = newUrl;
    }
});

function isDateFormatInvalid(dateString) {
    var dateFormatRegex = /^(\d{2})\/(\d{2})\/(\d{4})$/;
    if (dateFormatRegex.test(dateString)) {
        return false;
    } else {
        return true;
    }
}

$(document).ready(function () {
    var orderItems = $(".order-details");
    var startDateInput = $("#start-date");
    var endDateInput = $("#end-date");
    var minPriceInput = $("#min-price");
    var maxPriceInput = $("#max-price");
    var refreshFilterButton = $("#refresh-filter");
    var applyFilterButton = $("#apply-filter");

    applyFilterButton.click(function () {
        var startDate = startDateInput.val();
        var endDate = endDateInput.val();
        var minPrice = parseFloat(minPriceInput.val());
        var maxPrice = parseFloat(maxPriceInput.val());
        var errorMessage = "";

        if (isNaN(minPrice) && isNaN(maxPrice) && startDate === '' && endDate === '') {
            errorMessage += "Please enter a value for at least one field.\n";
        }

        if (isDateFormatInvalid(startDate) && startDate !== '') {
            errorMessage += "Start Date format is wrong.\n";
        }

        if (isDateFormatInvalid(endDate) && endDate !== '') {
            errorMessage += "End Date format is wrong.\n";
        }

        if (minPrice > maxPrice) {
            errorMessage += "Min Price cannot be greater than Max Price.\n";
        }

        if (startDate > endDate && startDate !== '' && endDate !== '') {
            errorMessage += "Start Date cannot be greater than End Date\n";
        }

        if (errorMessage !== "") {
            alert(errorMessage);
        } else {
            orderItems.each(function () {
                var orderItem = $(this);
                var orderDateElement = orderItem.find(".cus-left");
                var totalPriceElement = orderItem.find(".cus-right");
                var orderPrice = parseFloat(totalPriceElement.data("totalPrice"));
                var orderDateStr = orderDateElement.data("formattedDate");
                var orderDateParts = orderDateStr.split(' ');
                var dateParts = orderDateParts[1].split('/');
                var orderDateObj = new Date(dateParts[2], dateParts[1] - 1, dateParts[0]);
                var formattedOrderDate = orderDateObj.toLocaleDateString('en-GB');
                var shouldShow = true;

                if (startDate != '' && formattedOrderDate < startDate) shouldShow = false;
                if (endDate != '' && formattedOrderDate > endDate) shouldShow = false;
                if (minPrice != '' && orderPrice < minPrice) shouldShow = false;
                if (maxPrice != '' && orderPrice > maxPrice) shouldShow = false;

                if (shouldShow) {
                    orderItem.css("display", "block");
                } else {
                    orderItem.css("display", "none");
                }
            });
            alert("Đã lọc");
        }
    });

    refreshFilterButton.click(function () {
        startDateInput.val("");
        endDateInput.val("");
        minPriceInput.val("");
        maxPriceInput.val("");
        orderItems.css("display", "block");
    });
});
