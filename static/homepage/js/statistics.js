// Tệp chart.js

var ctx = document.getElementById('myChart').getContext('2d');
var orderDates = [];
var totalPrices = [];
var orderCounts = [];

// Hàm để thiết lập dữ liệu từ một nguồn bên ngoài (trong tệp HTML)
function setData(dates, prices, counts) {
    orderDates = dates;
    totalPrices = prices;
    orderCounts = counts;

    var chart = new Chart(ctx, {
        type: 'line', // Loại biểu đồ đường
        data: {
            labels: orderDates, // Trục hoành là ngày
            datasets: [
                {
                    label: 'Tổng tiền', // Nhãn cho dữ liệu tổng tiền
                    data: totalPrices, // Trục tung cho tổng tiền
                    borderColor: 'rgba(75, 192, 192, 1)', // Màu viền cho đường tổng tiền
                    borderWidth: 2, // Độ rộng viền
                    fill: false, // Không điền màu dưới đường tổng tiền
                    yAxisID: 'y',
                },
                {
                    label: 'Số đơn hàng', // Nhãn cho dữ liệu số đơn hàng
                    data: orderCounts, // Trục tung cho số đơn hàng
                    borderColor: 'rgba(255, 99, 132, 1)', // Màu viền cho đường số đơn hàng
                    borderWidth: 2, // Độ rộng viền
                    fill: false, // Không điền màu dưới đường số đơn hàng
                    yAxisID: 'y1',
                }
            ]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true, // Bắt đầu từ giá trị 0 trên trục tung
                    type: 'linear',
                    display: true,
                    position: 'left'
                },
                y1: {
                    beginAtZero: true, // Bắt đầu từ giá trị 0 trên trục tung
                    type: 'linear',
                    display: true,
                    position: 'right',
                    ticks: {
                        stepSize: 1, // Khoảng cách giữa các giá trị trên trục tung
                        callback: function(value, index, values) {
                            return parseInt(value); // Hiển thị số đơn hàng là số nguyên
                        }
                    },
                    // grid line settings
                    grid: {
                      drawOnChartArea: false, // only want the grid lines for one axis to show up
                    },
        }
    }
}
}
);
}
