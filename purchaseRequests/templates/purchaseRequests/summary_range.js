
$(function() {
    var start = moment("{{ start_date }}");
    var end = moment("{{ end_date }}").subtract(1, 'days');

    function update(start, end) {
        $("#daterange").val(start.format('MMM D, YYYY') + ' - ' + end.format('MMM D, YYYY'));
        $("#ts-form").submit()
    }
    $("#daterange").val(start.format('MMM D, YYYY') + ' - ' + end.format('MMM D, YYYY'));

    $("#range-input").daterangepicker({
        startDate: start,
        endDate: end,
        maxDate: moment(),
        ranges: {
            'Today': [moment(), moment()],
            'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
            'Last 7 Days': [moment().subtract(6, 'days'), moment()],
            'Last 30 Days': [moment().subtract(29, 'days'), moment()],
            'This Month': [moment().startOf('month'), moment()],
            'This Year': [moment().startOf('year'), moment()],
            'All Time': [moment("{{ earliest_req }}"), moment()]
        }
    }, update);

});