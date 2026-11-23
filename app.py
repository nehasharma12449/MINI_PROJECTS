import streamlit as st
import csv
import io

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Intelligent Disk I/O Analyzer",
    page_icon="💽",
    layout="wide"
)


# =====================================================
# CUSTOM DASHBOARD DESIGN
# =====================================================

st.markdown("""
<style>

.stApp {
    background-color: #0F172A;
    color: white;
}

section[data-testid="stSidebar"] {
    background-color: #172033;
}

h1, h2, h3 {
    color: #38BDF8 !important;
}

p, label {
    color: #E2E8F0;
}

div[data-testid="stMetric"] {
    background-color: #1C2333;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #334155;
}

.stButton > button {
    background-color: #2563EB;
    color: white;
    border-radius: 8px;
    border: none;
    height: 45px;
    font-weight: bold;
}

.stButton > button:hover {
    background-color: #1D4ED8;
    color: white;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# DISK MOVEMENT CALCULATION
# =====================================================

def calculate_movement(path):

    movement = 0

    for i in range(len(path) - 1):
        movement += abs(path[i + 1] - path[i])

    return movement


# =====================================================
# FCFS ALGORITHM
# =====================================================

def fcfs(requests, head):

    path = [head]

    for request in requests:
        path.append(request)

    return path


# =====================================================
# SSTF ALGORITHM
# =====================================================

def sstf(requests, head):

    pending = requests.copy()
    path = [head]
    current = head

    while pending:

        nearest = min(
            pending,
            key=lambda x: abs(x - current)
        )

        path.append(nearest)

        pending.remove(nearest)

        current = nearest

    return path


# =====================================================
# SCAN ALGORITHM
# =====================================================

def scan(requests, head, disk_size, direction):

    left = sorted(
        [r for r in requests if r < head],
        reverse=True
    )

    right = sorted(
        [r for r in requests if r > head]
    )

    equal = [r for r in requests if r == head]

    path = [head] + equal

    if direction == "Right":

        path.extend(right)

        if left:
            if path[-1] != disk_size - 1:
                path.append(disk_size - 1)

            path.extend(left)

    else:

        path.extend(reversed(left))

        if right:
            if path[-1] != 0:
                path.append(0)

            path.extend(right)

    return path


# =====================================================
# C-SCAN ALGORITHM
# =====================================================

def c_scan(requests, head, disk_size, direction):

    left = sorted(
        [r for r in requests if r < head]
    )

    right = sorted(
        [r for r in requests if r > head]
    )

    equal = [r for r in requests if r == head]

    path = [head] + equal

    if direction == "Right":

        path.extend(right)

        if left:

            if path[-1] != disk_size - 1:
                path.append(disk_size - 1)

            path.append(0)

            path.extend(left)

    else:

        path.extend(reversed(left))

        if right:

            if path[-1] != 0:
                path.append(0)

            path.append(disk_size - 1)

            path.extend(reversed(right))

    return path


# =====================================================
# LOOK ALGORITHM
# =====================================================

def look(requests, head, direction):

    left = sorted(
        [r for r in requests if r < head],
        reverse=True
    )

    right = sorted(
        [r for r in requests if r > head]
    )

    equal = [r for r in requests if r == head]

    path = [head] + equal

    if direction == "Right":

        path.extend(right)
        path.extend(left)

    else:

        path.extend(left)
        path.extend(reversed(right))

    return path


# =====================================================
# C-LOOK ALGORITHM
# =====================================================

def c_look(requests, head, direction):

    left = sorted(
        [r for r in requests if r < head]
    )

    right = sorted(
        [r for r in requests if r > head]
    )

    equal = [r for r in requests if r == head]

    path = [head] + equal

    if direction == "Right":

        path.extend(right)
        path.extend(left)

    else:

        path.extend(reversed(left))
        path.extend(reversed(right))

    return path


# =====================================================
# SVG GRAPH FUNCTION
# =====================================================

def display_graph(path, disk_size):

    width = 700
    height = 350
    padding = 50

    points = []

    for i, cylinder in enumerate(path):

        x = padding + (
            i / max(len(path) - 1, 1)
        ) * (width - 2 * padding)

        y = height - padding - (
            cylinder / max(disk_size - 1, 1)
        ) * (height - 2 * padding)

        points.append((x, y))

    point_string = " ".join(
        f"{x},{y}" for x, y in points
    )

    circles = ""

    for x, y in points:

        circles += (
            f'<circle cx="{x}" cy="{y}" '
            f'r="5" fill="#F59E0B"/>'
        )

    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg"
         viewBox="0 0 {width} {height}"
         width="100%" height="350">

        <line x1="{padding}" y1="{padding}"
              x2="{padding}" y2="{height-padding}"
              stroke="white" stroke-width="2"/>

        <line x1="{padding}" y1="{height-padding}"
              x2="{width-padding}" y2="{height-padding}"
              stroke="white" stroke-width="2"/>

        <polyline points="{point_string}"
                  fill="none"
                  stroke="#38BDF8"
                  stroke-width="3"/>

        {circles}

        <text x="10" y="20"
              fill="white" font-size="13">
            Cylinder Position
        </text>

        <text x="{width/2}" y="{height-10}"
              fill="white" font-size="13"
              text-anchor="middle">
            Movement Steps
        </text>

    </svg>
    """

    st.components.v1.html(
        svg,
        height=370,
        scrolling=False
    )


# =====================================================
# SIDEBAR INPUTS
# =====================================================

st.sidebar.title("⚙️ Disk Configuration")

disk_size = st.sidebar.number_input(
    "Total Disk Cylinders",
    min_value=2,
    max_value=10000,
    value=200
)

head_position = st.sidebar.number_input(
    "Initial Head Position",
    min_value=0,
    max_value=int(disk_size) - 1,
    value=min(53, int(disk_size) - 1)
)

request_input = st.sidebar.text_input(
    "Disk Request Queue",
    value="98, 183, 37, 122, 14, 124, 65, 67"
)

direction = st.sidebar.selectbox(
    "Initial Direction",
    ["Right", "Left"]
)


# =====================================================
# MAIN DASHBOARD
# =====================================================

st.title("💽 Intelligent Disk I/O Scheduling Analyzer")

st.write(
    "An interactive system for analyzing and comparing "
    "different disk scheduling algorithms."
)

st.markdown("---")


# =====================================================
# DASHBOARD OVERVIEW
# =====================================================

st.subheader("📊 Dashboard Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Disk Cylinders",
        disk_size
    )

with col2:
    st.metric(
        "Initial Head Position",
        head_position
    )

with col3:
    st.metric(
        "Scheduling Algorithms",
        "6"
    )


# =====================================================
# AVAILABLE ALGORITHMS
# =====================================================

st.markdown("---")

st.subheader("⚙️ Available Scheduling Algorithms")

algorithms = [
    ("FCFS", "First Come First Serve"),
    ("SSTF", "Shortest Seek Time First"),
    ("SCAN", "Elevator Algorithm"),
    ("C-SCAN", "Circular SCAN"),
    ("LOOK", "Optimized SCAN"),
    ("C-LOOK", "Circular LOOK")
]

for i in range(0, 6, 3):

    cols = st.columns(3)

    for j in range(3):

        name, description = algorithms[i + j]

        with cols[j]:

            st.markdown(
                f"""
                <div style="
                    background-color: #1C2333;
                    padding: 25px;
                    border-radius: 12px;
                    border: 1px solid #38BDF8;
                    text-align: center;
                    margin-bottom: 20px;
                ">

                    <h2 style="color: #38BDF8;">
                        {name}
                    </h2>

                    <p style="color: white;">
                        {description}
                    </p>

                </div>
                """,
                unsafe_allow_html=True
            )


# =====================================================
# START DISK ANALYSIS
# =====================================================

st.markdown("---")

st.subheader("🚀 Start Disk Analysis")


if st.button("Start Analysis", use_container_width=True):

    try:

        requests = [
            int(x.strip())
            for x in request_input.split(",")
            if x.strip()
        ]

        if not requests:

            st.error(
                "Please enter at least one disk request."
            )

        elif any(
            r < 0 or r >= disk_size
            for r in requests
        ):

            st.error(
                f"All requests must be between 0 and {disk_size - 1}."
            )

        else:

            # RUN ALL SIX ALGORITHMS

            results = {

                "FCFS": fcfs(
                    requests,
                    head_position
                ),

                "SSTF": sstf(
                    requests,
                    head_position
                ),

                "SCAN": scan(
                    requests,
                    head_position,
                    disk_size,
                    direction
                ),

                "C-SCAN": c_scan(
                    requests,
                    head_position,
                    disk_size,
                    direction
                ),

                "LOOK": look(
                    requests,
                    head_position,
                    direction
                ),

                "C-LOOK": c_look(
                    requests,
                    head_position,
                    direction
                )

            }

            st.success(
                "Disk scheduling analysis completed successfully!"
            )


            # =================================================
            # PERFORMANCE COMPARISON
            # =================================================

            comparison = []

            for name, path in results.items():

                movement = calculate_movement(path)

                average = movement / len(requests)

                comparison.append({

                    "Algorithm": name,

                    "Total Movement": movement,

                    "Average Movement": round(
                        average, 2
                    )

                })


            st.markdown("---")

            st.subheader("📊 Performance Comparison")


            table_html = """
            <table style="
                width:100%;
                border-collapse:collapse;
                color:white;
            ">

            <tr style="background-color:#2563EB;">

                <th style="padding:12px;">
                    Algorithm
                </th>

                <th style="padding:12px;">
                    Total Head Movement
                </th>

                <th style="padding:12px;">
                    Average Movement
                </th>

            </tr>
            """

            for item in comparison:

                table_html += f"""
                <tr style="
                    background-color:#1C2333;
                    text-align:center;
                ">

                    <td style="padding:12px;">
                        {item['Algorithm']}
                    </td>

                    <td style="padding:12px;">
                        {item['Total Movement']}
                    </td>

                    <td style="padding:12px;">
                        {item['Average Movement']}
                    </td>

                </tr>
                """

            table_html += "</table>"

            st.markdown(
                table_html,
                unsafe_allow_html=True
            )


            # =================================================
            # INTELLIGENT RECOMMENDATION
            # =================================================

            best = min(
                comparison,
                key=lambda x: x["Total Movement"]
            )

            st.markdown("---")

            st.subheader("🏆 Intelligent Recommendation")

            st.success(
                f"{best['Algorithm']} gives the lowest total "
                f"head movement of {best['Total Movement']} cylinders."
            )

            st.write(
                "The recommendation is based on the lowest "
                "total head movement for the current request queue."
            )

            st.info(
                "This is a rule-based recommendation system. "
                "It compares the calculated movement of all "
                "six algorithms and selects the lowest value."
            )


            # =================================================
            # INDIVIDUAL ALGORITHM DETAILS
            # =================================================

            st.markdown("---")

            st.subheader(
                "🔍 Individual Algorithm Details"
            )

            for name, path in results.items():

                with st.expander(
                    f"View {name} Results"
                ):

                    movement = calculate_movement(path)

                    average = round(
                        movement / len(requests), 2
                    )

                    st.write(
                        "**Head Movement Path:**"
                    )

                    st.write(
                        " → ".join(map(str, path))
                    )

                    st.write(
                        "**Total Head Movement:**",
                        movement
                    )

                    st.write(
                        "**Average Head Movement:**",
                        average
                    )

                    st.write(
                        "### 📈 Disk Head Movement Graph"
                    )

                    display_graph(
                        path,
                        disk_size
                    )


            # =================================================
            # CSV REPORT DOWNLOAD
            # =================================================

            st.markdown("---")

            st.subheader("📥 Download Analysis Report")

            csv_buffer = io.StringIO()

            writer = csv.writer(csv_buffer)

            writer.writerow([
                "Algorithm",
                "Total Head Movement",
                "Average Movement",
                "Head Movement Path"
            ])

            for name, path in results.items():

                movement = calculate_movement(path)

                average = round(
                    movement / len(requests), 2
                )

                writer.writerow([

                    name,

                    movement,

                    average,

                    " -> ".join(map(str, path))

                ])

            st.download_button(
                label="Download CSV Report",
                data=csv_buffer.getvalue(),
                file_name="disk_analysis_report.csv",
                mime="text/csv"
            )


    except ValueError:

        st.error(
            "Please enter valid cylinder numbers "
            "separated by commas."
        )


# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.markdown(
    """
    <center>
        Intelligent Disk I/O Scheduling Analyzer
        <br>
        MCA Project
    </center>
    """,
    unsafe_allow_html=True
)
