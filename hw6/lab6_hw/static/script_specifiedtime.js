// Get the current date and time
var currentDate = new Date();

// Add 10 seconds to the current time to get the end time
var endTime = new Date(currentDate.getTime() + 10 * 1000); // 10 seconds in milliseconds

// Extract individual date and time components for the start time
var startYear = currentDate.getFullYear();
var startMonth = ('0' + (currentDate.getMonth() + 1)).slice(-2); // Adding leading zero if needed
var startDay = ('0' + currentDate.getDate()).slice(-2); // Adding leading zero if needed
var startHours = ('0' + currentDate.getHours()).slice(-2); // Adding leading zero if needed
var startMinutes = ('0' + currentDate.getMinutes()).slice(-2); // Adding leading zero if needed
var startSeconds = ('0' + currentDate.getSeconds()).slice(-2); // Adding leading zero if needed

// Extract individual date and time components for the end time
var endYear = endTime.getFullYear();
var endMonth = ('0' + (endTime.getMonth() + 1)).slice(-2); // Adding leading zero if needed
var endDay = ('0' + endTime.getDate()).slice(-2); // Adding leading zero if needed
var endHours = ('0' + endTime.getHours()).slice(-2); // Adding leading zero if needed
var endMinutes = ('0' + endTime.getMinutes()).slice(-2); // Adding leading zero if needed
var endSeconds = ('0' + endTime.getSeconds()).slice(-2); // Adding leading zero if needed

// Construct the formatted date and time strings for the start and end times
var startDateTime = startYear + '-' + startMonth + '-' + startDay + 'T' + startHours + ':' + startMinutes + ':' + startSeconds;
var endDateTime = endYear + '-' + endMonth + '-' + endDay + 'T' + endHours + ':' + endMinutes + ':' + endSeconds;


// Set the initial value of the input fields to the current date and time
// document.getElementById('startDateTime').value = startDateTime;
// document.getElementById('endDateTime').value = endDateTime;


document.addEventListener('DOMContentLoaded', function () {
    // Initialize Chart.js chart
    var ctx = document.getElementById('dataChart').getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Temperature',
                data: [],
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1,
                fill: false
            },
            {
                label: 'Humidity',
                data: [],
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
                fill: false
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Function to fetch data from the server and update the chart
    function fetchDataAndUpdateChart() {
        var startDateTime = document.getElementById('startDateTime').value;
        var endDateTime = document.getElementById('endDateTime').value;

        // Replace 'T' character with '%20' and add ':00' for the missing seconds
        startDateTime = startDateTime.replace(/T| /g, '%20') + ':00';
        endDateTime = endDateTime.replace(/T| /g, '%20') + ':00';

        // Log the startDateTime and endDateTime
        console.log("startDateTime:", startDateTime);
        console.log("endDateTime:", endDateTime);

        fetch(`/get_data?start_time=${startDateTime}&end_time=${endDateTime}`)
            .then(response => response.json())
            .then(data => {
                // Update chart labels and data with fetched data
                myChart.data.labels = data.map(entry => entry.timestamp);
                myChart.data.datasets[0].data = data.map(entry => entry.temperature);
                myChart.data.datasets[1].data = data.map(entry => entry.humidity);
                myChart.update();
            })
            .catch(error => console.error('Error fetching data:', error));
    }


    // Attach click event listener to the Fetch Data button
    document.getElementById('fetchDataBtn').addEventListener('click', fetchDataAndUpdateChart);
});