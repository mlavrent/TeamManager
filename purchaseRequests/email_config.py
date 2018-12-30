send_to_person = "Robot Person"
send_to_emails = ["lavrema@outlook.com",
                  "lingyi19329@gmail.com",]
                  #"snernst@comcast.net",
                  #"bbach@mercyhigh.com",
                  #"kateseelig@gmail.com"]

template_simple_email = \
"""Hello %s,\n
%s added a request for the following item: %s on %s. Please review the following information about the request \
and decide whether the purchase will be made.

- Item: %s
- Cost per item: $%.2f
- Quantity: %d
- Total cost: $%.2f
- Link: %s

You can view the request here: %s
"""
template_html_email = \
"""Hello %s,<br>
%s added a request for the following item: <b>%s</b> on %s. Please review the following information about the request \
and decide whether the purchase will be made.
<ul>
    <li>Item: %s</li>
    <li>Cost per item: $%.2f</li>
    <li>Quantity: %d</li>
    <li>Total cost: $%.2f</li>
    <li>Link: <a href=%s>%s</a></li>
</ul>

You can view the request <a href="%s">here</a>.
"""