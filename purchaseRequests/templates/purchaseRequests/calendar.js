$("#startdate").daterangepicker({
    singleDatePicker: true,

    {% if submitted_filters.start %}
    startDate: "{{ submitted_filters.start }}",
    endDate: "{{ submitted_filters.start }}",
    {% else %}
    startDate: "{% now 'm/d/Y' %}",
    endDate: "{% now 'm/d/Y' %}",
    {% endif %}

    {% if submitted_filters.end %}
    maxDate: "{{ submitted_filters.end }}",
    {% else %}
    maxDate: "{% now 'm/d/Y' %}",
    {% endif %}

    autoUpdateInput: false,
    opens: "center",
    locale: {
        format: "MM/DD/YYYY",
    },
}, function(start, end, label){
    var ed = $("#enddate").data('daterangepicker');
    ed.minDate = start;
    ed.updateView();
    ed.updateCalendars();

    $("#startdate").val(start.format('MM/DD/YYYY'));
});
$("#enddate").daterangepicker({
    singleDatePicker: true,
    maxDate: "{% now 'm/d/Y' %}",

    {% if submitted_filters.end %}
    startDate: "{{ submitted_filters.end }}",
    endDate: "{{ submitted_filters.end }}",
    {% else %}
    startDate: "{% now 'm/d/Y' %}",
    endDate: "{% now 'm/d/Y' %}",
    {% endif %}

    {% if submitted_filters.start %}
    minDate: "{{ submitted_filters.start }}",
    {% endif %}

    autoUpdateInput: false,
    opens: "center",
    locale: {
        format: "MM/DD/YYYY",
    },
}, function(start, end, label){
    var sd = $("#startdate").data('daterangepicker');
    sd.maxDate = start;
    sd.updateView();
    sd.updateCalendars();

    $("#enddate").val(start.format('MM/DD/YYYY'));
});