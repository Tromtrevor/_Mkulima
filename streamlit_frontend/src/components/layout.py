import streamlit as st


def apply_app_style():
    st.markdown(
        """
        <style>
        :root {
          --mkulima-forest: #10251d;
          --mkulima-leaf: #b8e34b;
          --mkulima-muted: #718078;
          --mkulima-border: #e7ebe6;
        }
        .stApp {
          background: #f7f8f5;
          color: #1c2520;
        }
        [data-testid="stSidebar"] {
          background: var(--mkulima-forest);
        }
        [data-testid="stSidebar"] * {
          color: #f3f8f3;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
          color: #c3d2c7;
        }
        [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {
          border-radius: 12px;
        }
        [data-testid="stSidebar"] [aria-current="page"] {
          background: var(--mkulima-leaf);
          color: var(--mkulima-forest);
        }
        [data-testid="stSidebar"] [aria-current="page"] * {
          color: var(--mkulima-forest);
        }
        .mkulima-brand {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 10px 8px 24px;
        }
        .mkulima-brand-mark {
          display: grid;
          width: 42px;
          height: 42px;
          place-items: center;
          border-radius: 13px;
          background: var(--mkulima-leaf);
          color: var(--mkulima-forest);
          font-size: 23px;
        }
        .mkulima-brand-name {
          margin: 0;
          color: white;
          font-size: 20px;
          font-weight: 700;
        }
        .mkulima-brand-caption {
          margin: 2px 0 0;
          color: #a9bdb0;
          font-size: 11px;
        }
        .mkulima-hero {
          padding: 30px;
          border-radius: 22px;
          background: linear-gradient(120deg, #10251d, #1d4934);
          color: white;
        }
        .mkulima-hero-kicker {
          color: #c4e78a;
          font-size: 12px;
          font-weight: 700;
          letter-spacing: .12em;
          text-transform: uppercase;
        }
        .mkulima-hero h1 {
          margin: 12px 0 8px;
          color: white;
          font-size: clamp(30px, 4vw, 42px);
          letter-spacing: -.04em;
        }
        .mkulima-hero p {
          max-width: 650px;
          margin: 0;
          color: #d3e2d7;
          line-height: 1.7;
        }
        [data-testid="stMetric"] {
          min-height: 120px;
          padding: 18px;
          border: 1px solid var(--mkulima-border);
          border-radius: 16px;
          background: white;
          box-shadow: 0 2px 8px #10251d08;
        }
        [data-testid="stMetricLabel"] {
          color: var(--mkulima-muted);
        }
        div.stButton > button,
        div.stFormSubmitButton > button {
          min-height: 42px;
          border: 0;
          border-radius: 11px;
          background: var(--mkulima-forest);
          color: white;
          font-weight: 600;
        }
        div.stButton > button:hover,
        div.stFormSubmitButton > button:hover {
          border: 0;
          background: #1d4934;
          color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand():
    with st.sidebar:
        st.markdown(
            """
            <div class="mkulima-brand">
              <div class="mkulima-brand-mark">🌱</div>
              <div>
                <p class="mkulima-brand-name">Mkulima</p>
                <p class="mkulima-brand-caption">Agricultural intelligence</p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Turn farm data into informed decisions.")
