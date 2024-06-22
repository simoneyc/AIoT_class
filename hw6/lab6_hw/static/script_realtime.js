var startDate = new Date(new Date().toLocaleString("en-US", {timeZone: "Asia/Taipei"}));
startDate.setHours(startDate.getHours() + 8);
var startDateTime = startDate.toISOString().slice(0, 19).replace('T', ' ');

const MAX_DATA_NUM = 8;
const UPDATE_CHART_SEC = 5;

document.addEventListener('DOMContentLoaded', function () {
    // Initialize Chart.js chart
    var ctx = document.getElementById('dataChart').getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'line', data: {
            labels: [], datasets: [{
                label: 'Temperature',
                data: [],
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1,
                fill: false
            }, {
                label: 'Humidity',
                data: [],
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
                fill: false
            }]
        }, options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // 取得資料並更新圖表
    function fetchDataAndUpdateChart() {

        var currentDate = new Date(new Date().toLocaleString("en-US", {timeZone: "Asia/Taipei"}));


        var endTime = new Date(currentDate.getTime() + (UPDATE_CHART_SEC * 2) * 1000);
        endTime.setHours(endTime.getHours() + 8);
        var endDateTime = endTime.toISOString().slice(0, 19).replace('T', ' ');

        // console.log("startDateTime:", startDateTime);
        // console.log("endDateTime:", endDateTime);

        console.log(`/get_data?start_time=${startDateTime}&end_time=${endDateTime}`)

        fetch(`/get_data?start_time=${startDateTime}&end_time=${endDateTime}`)
            .then(response => response.json())
            .then(data => {

                // 最大資料數
                const Entries = data.slice(-MAX_DATA_NUM);

                console.log("-->", Entries)
                // 保留 時:分:秒
                myChart.data.labels = Entries.map(entry => {
                    const timestampParts = entry.timestamp.split(' ');
                    const timeParts = timestampParts[1].split(':');
                    return `${timeParts[0]}:${timeParts[1]}:${timeParts[2]}`;
                });
                myChart.data.datasets[0].data = Entries.map(entry => entry.temperature);
                myChart.data.datasets[1].data = Entries.map(entry => entry.humidity);
                myChart.update();
            })
            .catch(error => console.error('Error fetching data:', error));
    }


    fetchDataAndUpdateChart();
    setInterval(fetchDataAndUpdateChart, UPDATE_CHART_SEC * 1000 + 10);

    document.getElementById('fetchAutoDataBtn').addEventListener('click', fetchDataAndUpdateChart);
});