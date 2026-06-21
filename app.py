"""
Nassau Candy Distributor — Factory-to-Customer Shipping Route Efficiency Dashboard
"""
import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.express as px
import plotly.graph_objects as go
import os

# ---------------------------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Nassau Candy — Shipping Route Efficiency",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#1D3557"
BLUE = "#457B9D"
LIGHT = "#A8DADC"
GOLD = "#F4A261"
RED = "#E63946"
PALETTE = [NAVY, BLUE, GOLD, LIGHT, RED]

CUSTOM_CSS = f"""
<style>
    .stApp {{ background-color: #FAFBFC; }}
    h1, h2, h3 {{ color: {NAVY}; }}
    div[data-testid="stMetric"] {{
        background-color: white;
        border: 1px solid #E5E9EF;
        border-radius: 10px;
        padding: 14px 16px 8px 16px;
    }}
    div[data-testid="stMetricLabel"] {{ color: #6B7280; font-weight: 600; }}
    .callout {{
        background-color: #FFF4E5;
        border: 1px solid {GOLD};
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 14px;
        font-size: 0.92rem;
        color: #5C3A0E;
    }}
    .callout b {{ color: #8A4B0A; }}
    section[data-testid="stSidebar"] {{ background-color: #F1F5F9; }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# DATA LOADING
# ---------------------------------------------------------------------------
APP_DIR = os.path.dirname(__file__)

@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(APP_DIR, "clean_data.csv"))
    df["OrderDate"] = pd.to_datetime(df["OrderDate"])
    df["ShipDate"] = pd.to_datetime(df["ShipDate"])
    return df

@st.cache_data
def load_factory_coords():
    with open(os.path.join(APP_DIR, "factory_coords.json")) as f:
        return json.load(f)

US_STATE_CENTROIDS = {
'Alabama': (32.806671, -86.791130), 'Arizona': (33.729759, -111.431221),
'Arkansas': (34.969704, -92.373123), 'California': (36.116203, -119.681564),
'Colorado': (39.059811, -105.311104), 'Connecticut': (41.597782, -72.755371),
'Delaware': (39.318523, -75.507141), 'District of Columbia': (38.897438, -77.026817),
'Florida': (27.766279, -81.686783), 'Georgia': (33.040619, -83.643074),
'Idaho': (44.240459, -114.478828), 'Illinois': (40.349457, -88.986137),
'Indiana': (39.849426, -86.258278), 'Iowa': (42.011539, -93.210526),
'Kansas': (38.5266, -96.726486), 'Kentucky': (37.66814, -84.670067),
'Louisiana': (31.169546, -91.867805), 'Maine': (44.693947, -69.381927),
'Maryland': (39.063946, -76.802101), 'Massachusetts': (42.230171, -71.530106),
'Michigan': (43.326618, -84.536095), 'Minnesota': (45.694454, -93.900192),
'Mississippi': (32.741646, -89.678696), 'Missouri': (38.456085, -92.288368),
'Montana': (46.921925, -110.454353), 'Nebraska': (41.12537, -98.268082),
'Nevada': (38.313515, -117.055374), 'New Hampshire': (43.452492, -71.563896),
'New Jersey': (40.298904, -74.521011), 'New Mexico': (34.840515, -106.248482),
'New York': (42.165726, -74.948051), 'North Carolina': (35.630066, -79.806419),
'North Dakota': (47.528912, -99.784012), 'Ohio': (40.388783, -82.764915),
'Oklahoma': (35.565342, -96.928917), 'Oregon': (44.572021, -122.070938),
'Pennsylvania': (40.590752, -77.209755), 'Rhode Island': (41.680893, -71.51178),
'South Carolina': (33.856892, -80.945007), 'South Dakota': (44.299782, -99.438828),
'Tennessee': (35.747845, -86.692345), 'Texas': (31.054487, -97.563461),
'Utah': (40.150032, -111.862434), 'Vermont': (44.045876, -72.710686),
'Virginia': (37.769337, -78.169968), 'Washington': (47.400902, -121.490494),
'West Virginia': (38.491226, -80.954453), 'Wisconsin': (44.268543, -89.616508),
'Wyoming': (42.755966, -107.30249),
'Alberta': (53.9333, -116.5765), 'British Columbia': (53.7267, -127.6476),
'Manitoba': (53.7609, -98.8139), 'New Brunswick': (46.5653, -66.4619),
'Newfoundland and Labrador': (53.1355, -57.6604), 'Nova Scotia': (44.6820, -63.7443),
'Ontario': (51.2538, -85.3232), 'Prince Edward Island': (46.5107, -63.4168),
'Quebec': (52.9399, -73.5491), 'Saskatchewan': (52.9399, -106.4509),
}

df_raw = load_data()
FACTORY_COORDS = load_factory_coords()

SPEED_LABELS = {1: "Same Day", 2: "First Class", 3: "Second Class", 4: "Standard Class"}

# ---------------------------------------------------------------------------
# SIDEBAR — USER CAPABILITIES (filters)
# ---------------------------------------------------------------------------
st.sidebar.markdown("## 🍬 Nassau Candy Distributor")
st.sidebar.caption("Factory-to-Customer Shipping Route Efficiency Dashboard")
st.sidebar.divider()

st.sidebar.markdown("### Filters")

min_date, max_date = df_raw["OrderDate"].min().date(), df_raw["OrderDate"].max().date()
date_range = st.sidebar.date_input(
    "Order date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
elif isinstance(date_range, tuple) and len(date_range) == 1:
    start_date = end_date = date_range[0]
else:
    start_date, end_date = min_date, max_date

regions = sorted(df_raw["Region"].unique().tolist())
selected_regions = st.sidebar.multiselect("Region", regions, default=regions)

states = sorted(df_raw["State/Province"].unique().tolist())
selected_states = st.sidebar.multiselect("State / Province (optional)", states, default=[])

factories = sorted(df_raw["Factory"].unique().tolist())
selected_factories = st.sidebar.multiselect("Factory", factories, default=factories)

ship_modes = ["Same Day", "First Class", "Second Class", "Standard Class"]
selected_modes = st.sidebar.multiselect("Ship Mode", ship_modes, default=ship_modes)

st.sidebar.markdown("##### Speed-tier threshold")
speed_threshold = st.sidebar.slider(
    "Flag routes slower than this average speed rank (1=fastest mix, 4=slowest)",
    min_value=1.0, max_value=4.0, value=3.4, step=0.1,
    help="Used on the Route Drill-Down tab to highlight routes whose average ship-mode speed rank exceeds this threshold — i.e. routes leaning heavily on slower service tiers."
)

st.sidebar.divider()
st.sidebar.markdown(
    "<div class='callout'><b>Data note:</b> True day-level shipping lead time "
    "cannot be computed reliably from this dataset (Order Date / Ship Date are not "
    "consistently linked — see report §2.3). Ship Mode is used throughout as the "
    "delivery-speed proxy.</div>", unsafe_allow_html=True
)

# Apply filters
mask = (
    (df_raw["OrderDate"].dt.date >= start_date) &
    (df_raw["OrderDate"].dt.date <= end_date) &
    (df_raw["Region"].isin(selected_regions)) &
    (df_raw["Factory"].isin(selected_factories)) &
    (df_raw["Ship Mode"].isin(selected_modes))
)
if selected_states:
    mask &= df_raw["State/Province"].isin(selected_states)

df = df_raw[mask].copy()

if df.empty:
    st.warning("No shipments match the current filters. Try widening your selection.")
    st.stop()

# ---------------------------------------------------------------------------
# HEADER + KPI CARDS
# ---------------------------------------------------------------------------
st.markdown("# Factory-to-Customer Shipping Route Efficiency")
st.caption(
    f"Showing **{len(df):,}** of {len(df_raw):,} shipments &nbsp;|&nbsp; "
    f"**{df['Order ID'].nunique():,}** orders &nbsp;|&nbsp; "
    f"{start_date} to {end_date}"
)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Shipments", f"{len(df):,}")
k2.metric("Total Sales", f"${df['Sales'].sum():,.0f}")
k3.metric("Gross Profit", f"${df['Gross Profit'].sum():,.0f}")
k4.metric("Standard Class %", f"{(df['Ship Mode']=='Standard Class').mean()*100:.1f}%")
k5.metric("Expedited %", f"{df['IsExpedited'].mean()*100:.1f}%")

st.divider()

# ---------------------------------------------------------------------------
# TABS — DASHBOARD MODULES
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Route Efficiency Overview",
    "🗺️ Geographic Shipping Map",
    "🚚 Ship Mode Comparison",
    "🔎 Route Drill-Down",
])

# ===========================================================================
# TAB 1 — ROUTE EFFICIENCY OVERVIEW
# ===========================================================================
with tab1:
    st.markdown("### Average Speed Rank by Route")
    st.caption("Speed Rank: 1 = Same Day (fastest) … 4 = Standard Class (slowest). Lower is faster.")

    route_level = st.radio("Route granularity", ["Factory → State", "Factory → Region"], horizontal=True, key="route_gran")
    min_shipments = st.slider("Minimum shipments per route (filters out thin samples)", 1, 100, 5)

    if route_level == "Factory → State":
        grp_cols = ["Factory", "State/Province"]
    else:
        grp_cols = ["Factory", "Region"]

    route_agg = df.groupby(grp_cols, as_index=False).agg(
        shipments=("Row ID", "count"),
        total_sales=("Sales", "sum"),
        avg_speed_rank=("SpeedRank", "mean"),
        expedited_pct=("IsExpedited", lambda x: round(x.mean()*100, 1)),
        standard_pct=("IsStandard", lambda x: round(x.mean()*100, 1)),
    )
    route_agg = route_agg[route_agg["shipments"] >= min_shipments]
    if route_agg.empty:
        st.info("No routes meet this minimum shipment threshold. Lower the slider.")
    else:
        rmin, rmax = route_agg["avg_speed_rank"].min(), route_agg["avg_speed_rank"].max()
        if rmax > rmin:
            route_agg["efficiency_score"] = (100 * (rmax - route_agg["avg_speed_rank"]) / (rmax - rmin)).round(1)
        else:
            route_agg["efficiency_score"] = 50.0
        route_agg["route_label"] = route_agg[grp_cols[0]] + " → " + route_agg[grp_cols[1]]
        route_agg = route_agg.sort_values("efficiency_score", ascending=False)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### Top 10 Most Efficient Routes")
            top10 = route_agg.head(10)
            fig = px.bar(
                top10.sort_values("efficiency_score"), x="efficiency_score", y="route_label",
                orientation="h", color_discrete_sequence=[NAVY],
                labels={"efficiency_score": "Efficiency Score (0-100)", "route_label": ""},
            )
            fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.markdown("##### Bottom 10 Least Efficient Routes")
            bottom10 = route_agg.tail(10)
            fig = px.bar(
                bottom10.sort_values("efficiency_score", ascending=False), x="efficiency_score", y="route_label",
                orientation="h", color_discrete_sequence=[RED],
                labels={"efficiency_score": "Efficiency Score (0-100)", "route_label": ""},
            )
            fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("##### Route Performance Leaderboard")
        display_cols = grp_cols + ["shipments", "total_sales", "avg_speed_rank", "expedited_pct", "standard_pct", "efficiency_score"]
        st.dataframe(
            route_agg[display_cols].rename(columns={
                "shipments": "Shipments", "total_sales": "Total Sales ($)",
                "avg_speed_rank": "Avg Speed Rank", "expedited_pct": "Expedited %",
                "standard_pct": "Standard %", "efficiency_score": "Efficiency Score",
            }).style.format({"Total Sales ($)": "${:,.2f}", "Avg Speed Rank": "{:.2f}"}),
            use_container_width=True, height=350,
        )
        st.caption(
            f"⚠️ Routes below the {min_shipments}-shipment threshold are excluded from ranking to avoid drawing "
            "conclusions from statistically thin samples. Low-volume, remote, or cross-border routes naturally "
            "score lower since Standard Class is a more economical choice for them — this does not necessarily "
            "indicate a service failure."
        )

# ===========================================================================
# TAB 2 — GEOGRAPHIC SHIPPING MAP
# ===========================================================================
with tab2:
    st.markdown("### US/Canada Heatmap of Shipping Efficiency")

    geo_metric = st.selectbox(
        "Color states by",
        ["Avg Speed Rank (higher = slower mix)", "Standard Class %", "Shipment Volume", "Bottleneck Score"],
    )

    state_stats = df.groupby(["State/Province", "Region"], as_index=False).agg(
        shipments=("Row ID", "count"),
        total_sales=("Sales", "sum"),
        avg_speed_rank=("SpeedRank", "mean"),
        standard_pct=("IsStandard", lambda x: round(x.mean()*100, 1)),
        is_cross_border=("IsCrossBorder", "max"),
    )
    if len(state_stats) > 1:
        state_stats["volume_rank_pct"] = state_stats["shipments"].rank(pct=True)
        state_stats["slowness_rank_pct"] = state_stats["avg_speed_rank"].rank(pct=True)
        state_stats["bottleneck_score"] = ((state_stats["volume_rank_pct"]*0.5 + state_stats["slowness_rank_pct"]*0.5)*100).round(1)
    else:
        state_stats["bottleneck_score"] = 50.0

    state_stats["lat"] = state_stats["State/Province"].map(lambda s: US_STATE_CENTROIDS.get(s, (None, None))[0])
    state_stats["lon"] = state_stats["State/Province"].map(lambda s: US_STATE_CENTROIDS.get(s, (None, None))[1])
    state_stats = state_stats.dropna(subset=["lat", "lon"])

    metric_map = {
        "Avg Speed Rank (higher = slower mix)": "avg_speed_rank",
        "Standard Class %": "standard_pct",
        "Shipment Volume": "shipments",
        "Bottleneck Score": "bottleneck_score",
    }
    color_col = metric_map[geo_metric]

    col_map, col_factory = st.columns([2.2, 1])
    with col_map:
        fig = px.scatter_geo(
            state_stats, lat="lat", lon="lon",
            size="shipments", color=color_col,
            hover_name="State/Province",
            hover_data={"shipments": True, "avg_speed_rank": ":.2f", "standard_pct": True, "lat": False, "lon": False},
            color_continuous_scale=["#1D3557", "#A8DADC", "#F4A261", "#E63946"] if color_col != "shipments" else "Blues",
            size_max=38, scope="north america",
            labels={color_col: geo_metric},
        )
        fig.update_geos(showland=True, landcolor="#F5F7FA", showcountries=True, countrycolor="#CBD5E1", showlakes=False)
        fig.update_layout(height=520, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Bubble size = shipment volume. Color = selected metric. Hover for details.")

    with col_factory:
        st.markdown("##### Factory Locations")
        fac_df = pd.DataFrame([
            {"Factory": k, "lat": v[0], "lon": v[1]} for k, v in FACTORY_COORDS.items()
        ])
        fig2 = px.scatter_geo(
            fac_df, lat="lat", lon="lon", hover_name="Factory",
            color="Factory", color_discrete_sequence=PALETTE,
            scope="north america",
        )
        fig2.update_geos(showland=True, landcolor="#F5F7FA", showcountries=True, countrycolor="#CBD5E1")
        fig2.update_traces(marker=dict(size=14, symbol="star"))
        fig2.update_layout(height=420, margin=dict(l=0, r=0, t=10, b=0), legend=dict(font=dict(size=9)))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("##### Regional Bottleneck Candidates")
    st.caption("States combining high shipment volume with high Standard-Class share — the combination most likely to create visible, scaled delay.")
    bn = state_stats[state_stats["shipments"] >= 10].sort_values("bottleneck_score", ascending=False).head(10)
    st.dataframe(
        bn[["State/Province", "Region", "shipments", "standard_pct", "avg_speed_rank", "bottleneck_score", "is_cross_border"]].rename(columns={
            "shipments": "Shipments", "standard_pct": "Standard %", "avg_speed_rank": "Avg Speed Rank",
            "bottleneck_score": "Bottleneck Score", "is_cross_border": "Cross-Border",
        }),
        use_container_width=True, height=320,
    )

# ===========================================================================
# TAB 3 — SHIP MODE COMPARISON
# ===========================================================================
with tab3:
    st.markdown("### Ship Mode Performance Comparison")

    col1, col2 = st.columns([1, 1.4])
    with col1:
        mode_counts = df["Ship Mode"].value_counts().reindex(ship_modes).fillna(0)
        fig = px.pie(
            values=mode_counts.values, names=mode_counts.index, hole=0.45,
            color=mode_counts.index,
            color_discrete_map={"Same Day": GOLD, "First Class": LIGHT, "Second Class": BLUE, "Standard Class": NAVY},
        )
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
        st.markdown("##### Overall Ship Mode Mix")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("##### Ship Mode Mix by Region")
        ct = pd.crosstab(df["Region"], df["Ship Mode"], normalize="index").mul(100).round(2)
        ct = ct.reindex(columns=ship_modes, fill_value=0).reset_index()
        ct_melt = ct.melt(id_vars="Region", var_name="Ship Mode", value_name="Percent")
        fig = px.bar(
            ct_melt, x="Region", y="Percent", color="Ship Mode", barmode="group",
            color_discrete_map={"Same Day": GOLD, "First Class": LIGHT, "Second Class": BLUE, "Standard Class": NAVY},
        )
        fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="% of Shipments")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("##### Ship Mode Mix by Factory")
    ctf = pd.crosstab(df["Factory"], df["Ship Mode"], normalize="index").mul(100).round(2)
    ctf = ctf.reindex(columns=ship_modes, fill_value=0).reset_index()
    ctf_melt = ctf.melt(id_vars="Factory", var_name="Ship Mode", value_name="Percent")
    fig = px.bar(
        ctf_melt, x="Factory", y="Percent", color="Ship Mode", barmode="stack",
        color_discrete_map={"Same Day": GOLD, "First Class": LIGHT, "Second Class": BLUE, "Standard Class": NAVY},
    )
    fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="% of Shipments")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("##### Profit Margin by Ship Mode")
    margin_by_mode = df.groupby("Ship Mode", as_index=False)["ProfitMargin"].mean()
    margin_by_mode["ProfitMargin"] = (margin_by_mode["ProfitMargin"] * 100).round(1)
    margin_by_mode = margin_by_mode.set_index("Ship Mode").reindex(ship_modes).reset_index()
    fig = px.bar(
        margin_by_mode, x="Ship Mode", y="ProfitMargin", color="Ship Mode",
        color_discrete_map={"Same Day": GOLD, "First Class": LIGHT, "Second Class": BLUE, "Standard Class": NAVY},
        labels={"ProfitMargin": "Avg Profit Margin (%)"},
    )
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ===========================================================================
# TAB 4 — ROUTE DRILL-DOWN
# ===========================================================================
with tab4:
    st.markdown("### Route Drill-Down")

    dcol1, dcol2 = st.columns(2)
    with dcol1:
        drill_factory = st.selectbox("Select Factory", sorted(df["Factory"].unique()))
    with dcol2:
        avail_states = sorted(df[df["Factory"] == drill_factory]["State/Province"].unique())
        drill_state = st.selectbox("Select State/Province", avail_states)

    route_df = df[(df["Factory"] == drill_factory) & (df["State/Province"] == drill_state)]

    if route_df.empty:
        st.info("No shipments for this Factory → State combination under current filters.")
    else:
        avg_speed = route_df["SpeedRank"].mean()
        is_flagged = avg_speed >= speed_threshold

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Shipments", f"{len(route_df):,}")
        m2.metric("Total Sales", f"${route_df['Sales'].sum():,.2f}")
        m3.metric("Avg Speed Rank", f"{avg_speed:.2f}", help="1=fastest mix, 4=slowest mix")
        m4.metric("Standard Class %", f"{(route_df['Ship Mode']=='Standard Class').mean()*100:.1f}%")

        if is_flagged:
            st.markdown(
                f"<div class='callout'>⚠️ <b>Flagged route:</b> This route's average speed rank "
                f"({avg_speed:.2f}) meets or exceeds your threshold of {speed_threshold:.1f}, indicating "
                f"heavy reliance on slower service tiers.</div>", unsafe_allow_html=True
            )

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### Ship Mode Mix for this Route")
            mc = route_df["Ship Mode"].value_counts().reindex(ship_modes).fillna(0)
            fig = px.bar(
                x=mc.index, y=mc.values, color=mc.index,
                color_discrete_map={"Same Day": GOLD, "First Class": LIGHT, "Second Class": BLUE, "Standard Class": NAVY},
                labels={"x": "", "y": "Shipments"},
            )
            fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.markdown("##### Monthly Order Volume for this Route")
            monthly = route_df.groupby("OrderMonth").size().reset_index(name="Orders")
            fig = px.line(monthly, x="OrderMonth", y="Orders", markers=True, color_discrete_sequence=[NAVY])
            fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10), xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("##### Order-Level Shipment Timeline")
        timeline_cols = ["Order ID", "OrderDate", "Ship Mode", "Product Name", "Sales", "Units", "Gross Profit", "City"]
        st.dataframe(
            route_df[timeline_cols].sort_values("OrderDate", ascending=False).rename(columns={
                "OrderDate": "Order Date", "Product Name": "Product",
            }),
            use_container_width=True, height=350,
        )

st.divider()
st.caption(
    "Nassau Candy Distributor · Factory-to-Customer Shipping Route Efficiency Analysis · "
    "Data note: lead-time-in-days is not computed due to a data quality issue in source Order/Ship dates; "
    "Ship Mode is used as the delivery-speed proxy throughout. See the accompanying research paper for full methodology."
)
