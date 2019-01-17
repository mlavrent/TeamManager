$("#startdate").daterangepicker({
    singleDatePicker: true,

    {% if filters.start %}
    startDate: "{{ filters.start }}",
    endDate: "{{ filters.start }}",
    {% else %}
    startDate: "{% now 'm/d/Y' %}",
    endDate: "{% now 'm/d/Y' %}",
    {% endif %}

    {% if filters.end %}
    maxDate: "{{ filters.end }}",
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

    {% if filters.end %}
    startDate: "{{ filters.end }}",
    endDate: "{{ filters.end }}",
    {% else %}
    startDate: "{% now 'm/d/Y' %}",
    endDate: "{% now 'm/d/Y' %}",
    {% endif %}

    {% if filters.start %}
    minDate: "{{ filters.start }}",
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