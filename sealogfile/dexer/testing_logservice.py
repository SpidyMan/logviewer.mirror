import re
data = ''
# Sample data from result.txt
with open('sample_log.txt','rb') as f:
    data = f.readlines()

# Parse the data into a nested dictionary
def parse_data(data):
    result = {}
    current_table = None
    current_subtable = None

    for line in data.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.endswith(':'):
            if line.startswith('TABLE_'):
                current_table = line[:-1]
                result[current_table] = {}
            elif current_table:
                current_subtable = line[:-1]
                result[current_table][current_subtable] = []
        elif current_table:
            if current_subtable:
                result[current_table][current_subtable].append(line)
            else:
                result[current_table][line] = []

    return result

parsed_data = parse_data(data)

# Generate HTML content
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Collapsible Table Navigation</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
        }
        .nav {
            width: 20%;
            padding: 20px;
            border-right: 1px solid #ddd;
        }
        .content {
            width: 80%;
            padding: 20px;
            overflow-y: auto;
            height: 100vh;
        }
        .collapsible {
            background-color: #f1f1f1;
            cursor: pointer;
            padding: 10px;
            width: 100%;
            border: none;
            text-align: left;
            outline: none;
            font-size: 18px;
            margin-bottom: 5px;
        }
        .active, .collapsible:hover {
            background-color: #ccc;
        }
        .collapsible:after {
            content: '\\002B';
            color: white;
            font-weight: bold;
            float: right;
            margin-left: 5px;
        }
        .active:after {
            content: "\\2212";
        }
        .content-section {
            display: none;
            padding-left: 20px;
        }
    </style>
</head>
<body>
    <div class="nav">
"""

# Add navigation items
for table, subtables in parsed_data.items():
    html_content += f'<button class="collapsible">{table}</button>\n'
    html_content += '<div class="content-section">\n'
    for subtable, items in subtables.items():
        html_content += f'<p><a href="#{subtable}">{subtable}</a></p>\n'
    html_content += '</div>\n'

html_content += """
    </div>
    <div class="content">
"""

# Add content sections
for table, subtables in parsed_data.items():
    html_content += f'<h2 id="{table}">{table}</h2>\n'
    for subtable, items in subtables.items():
        html_content += f'<h3 id="{subtable}">{subtable}</h3>\n'
        html_content += '<ul>\n'
        for item in items:
            html_content += f'<li>{item}</li>\n'
        html_content += '</ul>\n'

html_content += """
    </div>

    <script>
        var coll = document.getElementsByClassName("collapsible");
        for (var i = 0; i < coll.length; i++) {
            coll[i].addEventListener("click", function() {
                this.classList.toggle("active");
                var content = this.nextElementSibling;
                if (content.style.display === "block") {
                    content.style.display = "none";
                } else {
                    content.style.display = "block";
                }
            });
        }
    </script>
</body>
</html>
"""

# Save the generated HTML to a file
with open('output.html', 'w') as f:
    f.write(html_content)

print("HTML file generated successfully!")
