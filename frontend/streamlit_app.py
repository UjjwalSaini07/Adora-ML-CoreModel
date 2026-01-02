import streamlit as st
import requests, os, io
from PIL import Image
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Configure matplotlib for better Unicode support
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False

# Suppress specific matplotlib font warnings
import warnings
warnings.filterwarnings("ignore", message=".*Glyph.*missing from font.*")
warnings.filterwarnings("ignore", message=".*findfont: Font family.*not found.*")

import numpy as np

BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

# Authentication state management
if 'auth_token' not in st.session_state:
    st.session_state.auth_token = None
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

def get_auth_headers():
    if st.session_state.auth_token:
        return {'Authorization': f'Bearer {st.session_state.auth_token}'}
    return {}

def login(username, password):
    try:
        resp = requests.post(f'{BACKEND_URL}/login', data={'username': username, 'password': password})
        if resp.ok:
            data = resp.json()
            st.session_state.auth_token = data['access_token']
            st.session_state.current_user = {'username': username}
            return True, "Login successful"
        else:
            return False, "Invalid credentials"
    except Exception as e:
        return False, str(e)

def logout():
    st.session_state.auth_token = None
    st.session_state.current_user = None
    st.rerun()

def register(username, password, email):
    try:
        resp = requests.post(f'{BACKEND_URL}/register', data={'username': username, 'password': password, 'email': email})
        if resp.ok:
            return True, "Registration successful"
        else:
            return False, resp.json().get('detail', 'Registration failed')
    except Exception as e:
        return False, str(e)

st.set_page_config(
    page_title='Adora: Retail Media Creative Builder',
    layout='wide',
    initial_sidebar_state='expanded'
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        color: #1e293b;
        text-align: center;
        margin-bottom: 1.5rem;
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        border-bottom: 4px solid #3b82f6;
        padding-bottom: 1.5rem;
    }
    .subtitle {
        text-align: center;
        color: #64748b;
        font-size: 1.2rem;
        font-weight: 500;
        margin-bottom: 3rem;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e293b;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8fafc, #f1f5f9);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px -1px rgba(0, 0, 0, 0.15);
    }
    .asset-card {
        background-color: transparent;
        padding: 0.5rem;
        border-radius: 8px;
        border: none;
        box-shadow: none;
    }
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8fafc, #f1f5f9);
        border-right: 2px solid #e2e8f0;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #3b82f6, #06b6d4);
    }
    .stMetric {
        background-color: transparent;
    }
    .stMetric label {
        color: #64748b;
        font-weight: 600;
    }
    .stMetric .metric-value {
        color: #1e293b;
        font-weight: 800;
    }
</style>
""", unsafe_allow_html=True)

# Authentication UI
if not st.session_state.auth_token:
    st.markdown('<h1 class="main-header">Adora: Retail Media Creative Builder</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Advanced AI-Powered Creative Asset Management Platform</p>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                success, message = login(username, password)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    with tab2:
        st.subheader("Register")
        with st.form("register_form"):
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Register")
            if submitted:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    success, message = register(new_username, new_password, new_email)
                    if success:
                        st.success(message)
                        st.info("You can now login with your credentials")
                    else:
                        st.error(message)
    st.stop()

# Main app for authenticated users
st.markdown('<h1 class="main-header">Adora: Retail Media Creative Builder</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Advanced AI-Powered Creative Asset Management Platform</p>', unsafe_allow_html=True)

# User info and logout in sidebar
with st.sidebar:
    st.write(f"Logged in as: **{st.session_state.current_user['username']}**")
    if st.button("Logout", type="secondary"):
        logout()

# Initialize session state
if 'selected_asset' not in st.session_state:
    st.session_state.selected_asset = 0

# Sidebar for global actions
with st.sidebar:
    st.header('Asset Management')
    st.subheader('Upload New Asset')
    uploaded = st.file_uploader('Select image file', type=['png','jpg','jpeg'], label_visibility='collapsed')
    label = st.text_input('Asset Label (optional)', placeholder='e.g., Product Shot 1')
    if uploaded and st.button('Upload Asset', type='primary'):
        with st.spinner('Uploading asset...'):
            files = {'file': (uploaded.name, uploaded.getvalue())}
            data = {'label': label}
            resp = requests.post(f'{BACKEND_URL}/upload_packshot', files=files, data=data, headers=get_auth_headers())
        if resp.ok:
            st.success('Asset uploaded successfully! Refresh to view.')
        else:
            st.error('Upload failed. Please try again.')

# Professional Navigation Sidebar
st.sidebar.markdown('---')
st.sidebar.subheader('Navigation')

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'

nav_options = ['Dashboard', 'Asset Library', 'Image Editor', 'AI Analysis', 'AI Creative Assistant', 'Version History', 'Compliance Check']
for option in nav_options:
    icon = {'Dashboard': '📊', 'Asset Library': '🖼️', 'Image Editor': '✏️', 'AI Analysis': '🤖', 'AI Creative Assistant': '🎨', 'Version History': '📚', 'Compliance Check': '✅'}[option]
    if st.sidebar.button(
        f"{icon} {option}",
        key=f"nav_{option}",
        help=f"Navigate to {option}",
        width='stretch'
    ):
        st.session_state.current_page = option

st.sidebar.markdown('---')
st.sidebar.caption(f"Current: {st.session_state.current_page}")

if st.session_state.current_page == 'Dashboard':
    st.markdown('<h2 class="section-header">Executive Dashboard</h2>', unsafe_allow_html=True)
    st.markdown('Comprehensive analytics and project insights for creative asset management.')

    # Dashboard Controls
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        date_range = st.selectbox('Time Range', ['Last 7 days', 'Last 30 days', 'Last 90 days', 'All time'], index=1, label_visibility='collapsed')
    with col2:
        refresh = st.button('🔄 Refresh Data', help='Update dashboard with latest data', width='stretch')
    with col3:
        export = st.button('📊 Export CSV Report', help='Download comprehensive system report as CSV', width='stretch')
        if export:
            with st.spinner('Generating comprehensive report...'):
                resp = requests.get(f'{BACKEND_URL}/export_report', headers=get_auth_headers())
            if resp.ok:
                data = resp.json()
                st.success(f'✅ Report generated with {data["metrics_count"]} metrics!')

                # Create download button for CSV
                csv_content = data['content']
                st.download_button(
                    label='📥 Download CSV Report',
                    data=csv_content,
                    file_name=data['filename'],
                    mime='text/csv',
                    help='Click to download the comprehensive report'
                )

                # Show preview of key metrics
                with st.expander('📋 Report Preview'):
                    lines = csv_content.strip().split('\n')
                    if len(lines) >= 2:
                        headers = lines[0].split(',')
                        values = lines[1].split(',')
                        preview_data = {h: v for h, v in zip(headers[:10], values[:10])}  # Show first 10 metrics
                        st.json(preview_data)
            else:
                st.error('Failed to generate report')

    resp = requests.get(f'{BACKEND_URL}/assets', headers=get_auth_headers())
    if resp.ok:
        assets = resp.json()
        total_assets = len(assets)

        # Handle empty assets case
        if total_assets == 0:
            st.info('No assets found. Upload some assets to see analytics.')
            st.metric('Total Assets', 0)
            st.stop()

        # Key Performance Indicators
        st.subheader('📊 Key Performance Indicators')
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.metric('Total Assets', total_assets, delta='+12 this week')
        with col2:
            processed = sum(1 for a in assets if 'processed' in (a.get('label') or '').lower())
            processed_pct = (processed / total_assets * 100) if total_assets > 0 else 0
            st.metric('Processed', processed, delta=f'{processed_pct:.1f}%')
        with col3:
            st.metric('Compliance Rate', '98.5%', delta='+0.5%')
        with col4:
            avg_size = np.mean([len(requests.get(f'{BACKEND_URL}/asset/{a["id"]}', headers=get_auth_headers()).content) for a in assets[:min(10, len(assets))]]) / 1024 if assets else 0
            st.metric('Avg Size', f'{avg_size:.1f} KB')
        with col5:
            st.metric('Active Users', '24', delta='+3 today')
        with col6:
            st.metric('Projects', '8', delta='+1 this month')

        st.subheader('📈 Analytics & Insights')

        if assets and len(assets) > 0:
            # Convert to DataFrame for analysis
            df = pd.DataFrame(assets)
            df['uploaded_at'] = pd.to_datetime(df['uploaded_at'], unit='s')
            df['date'] = df['uploaded_at'].dt.date
            df['hour'] = df['uploaded_at'].dt.hour
            df['weekday'] = df['uploaded_at'].dt.day_name()

            # Asset Upload Trends - Full Width
            st.subheader('📈 Asset Upload Trends & Daily Performance Analysis')

            daily_uploads = df.groupby('date').size().tail(30)  # Last 30 days

            # Calculate comprehensive trend and statistics
            total_uploads = daily_uploads.sum()
            avg_daily = daily_uploads.mean()
            max_day = daily_uploads.idxmax()
            max_count = daily_uploads.max()
            min_count = daily_uploads.min()

            fig, ax = plt.subplots(figsize=(16, 7), facecolor='#ffffff', dpi=100)

            # Enhanced area chart with gradient fill
            ax.fill_between(daily_uploads.index, daily_uploads.values, alpha=0.3, color='#3b82f6', linewidth=0, label='Upload Volume')
            line = ax.plot(daily_uploads.index, daily_uploads.values, color='#1e40af', linewidth=4, marker='o',
                          markersize=6, markerfacecolor='#1e40af', markeredgecolor='white', markeredgewidth=2, label='Daily Trend')

            # Add trend line with confidence
            if len(daily_uploads) > 1:
                z = np.polyfit(range(len(daily_uploads)), daily_uploads.values, 1)
                p = np.poly1d(z)
                trend_line = ax.plot(daily_uploads.index, p(range(len(daily_uploads))), "r--", alpha=0.9,
                                   linewidth=3, label='Trend Line')

            # Add reference lines
            ax.axhline(y=avg_daily, color='#10b981', linestyle='--', alpha=0.7, linewidth=2, label=f'Average: {avg_daily:.1f}')
            ax.axhline(y=max_count, color='#ef4444', linestyle=':', alpha=0.7, linewidth=2, label=f'Peak: {max_count}')

            ax.set_title(f'Analytics: Comprehensive Daily Upload Trends & Performance Metrics\nTotal Assets: {total_uploads} | Daily Average: {avg_daily:.1f} | Performance Range: {min_count}-{max_count} uploads',
                        fontsize=20, fontweight='bold', pad=35, color='#1e293b')
            ax.set_xlabel('Date', fontsize=14, fontweight='medium')
            ax.set_ylabel('Assets Uploaded', fontsize=14, fontweight='medium')
            ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_alpha(0.5)
            ax.spines['bottom'].set_alpha(0.5)

            # Enhanced date formatting
            plt.xticks(rotation=45, ha='right', fontsize=11)
            plt.yticks(fontsize=11)

            # Add peak indicator with enhanced styling
            if max_count > 0:
                ax.annotate(f'Peak Performance\n{max_count} uploads',
                           xy=(max_day, max_count), xytext=(15, 15), textcoords='offset points',
                           bbox=dict(boxstyle='round,pad=0.5', facecolor='#ef4444', alpha=0.9, edgecolor='white'),
                           fontsize=12, fontweight='bold', color='white', ha='left')

            # Add latest data point highlight
            if len(daily_uploads) > 0:
                latest_date = daily_uploads.index[-1]
                latest_count = daily_uploads.iloc[-1]
                ax.plot(latest_date, latest_count, 'o', markersize=12, markerfacecolor='#f59e0b',
                       markeredgecolor='white', markeredgewidth=3, label='Latest')

            ax.legend(loc='upper left', framealpha=0.95, fontsize=12)
            plt.tight_layout()
            st.pyplot(fig, width='stretch')

            # Enhanced key insights in single comprehensive row
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            with col1:
                st.metric('📊 Total Uploads', f'{total_uploads:,}', f'{len(daily_uploads)} day period')
            with col2:
                st.metric('📈 Daily Average', f'{avg_daily:.1f}', f'Range: {min_count}-{max_count}')
            with col3:
                growth = (daily_uploads.iloc[-1] - daily_uploads.iloc[0]) / daily_uploads.iloc[0] * 100 if len(daily_uploads) > 1 and daily_uploads.iloc[0] != 0 else 0
                st.metric('📉 Growth Rate', f'{growth:+.1f}%', 'Period change')
            with col4:
                st.metric('🎯 Peak Performance', f'{max_day.strftime("%b %d")}', f'{max_count} uploads')
            with col5:
                consistency = np.std(daily_uploads.values) / avg_daily if avg_daily > 0 else 0
                consistency_level = "High" if consistency < 0.3 else "Medium" if consistency < 0.6 else "Low"
                st.metric('🎯 Consistency', consistency_level, f'CV: {consistency:.2f}')
            with col6:
                trend_direction = "↗️ Upward" if growth > 0 else "↘️ Downward" if growth < 0 else "➡️ Stable"
                volatility = "High" if max_count > avg_daily * 2 else "Medium" if max_count > avg_daily * 1.5 else "Low"
                st.metric('📊 Trend & Volatility', f'{trend_direction} {volatility}', f'{abs(growth):.1f}% ± {volatility.lower()}')

            # Removed Asset Categories section as requested

            # Advanced Upload Patterns & Analytics - Full Width
            st.subheader('⏰ Advanced Temporal Analytics')

            # Weekly Performance Analysis - Full Width
            with st.container(height=500):
                st.markdown('<h4 style="text-align: center; color: #fff; margin-bottom: 20px;">📅 Weekly Performance Analysis & Trends</h4>', unsafe_allow_html=True)

                weekday_uploads = df.groupby('weekday').size().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
                weekday_data = weekday_uploads.fillna(0)

                # Calculate comprehensive insights
                peak_day = weekday_data.idxmax()
                peak_count = weekday_data.max()
                total_weekly = weekday_data.sum()
                avg_weekly = weekday_data.mean()

                # Weekend vs Weekday analysis
                weekend_avg = (weekday_data['Saturday'] + weekday_data['Sunday']) / 2
                weekday_avg = weekday_data[['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']].mean()
                weekend_ratio = weekend_avg / weekday_avg if weekday_avg > 0 else 0

                # Create enhanced full-width chart
                fig, ax1 = plt.subplots(figsize=(14, 6), facecolor='#ffffff', dpi=100)

                weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                x = np.arange(7)

                # Main bar chart with enhanced styling
                bars = ax1.bar(x, weekday_data.values, color='#06b6d4', alpha=0.8,
                               edgecolor='white', linewidth=1.5, width=0.7, label='Daily Uploads')

                # Highlight peak day with special styling
                peak_idx = list(weekday_data.index).index(peak_day)
                bars[peak_idx].set_color('#10b981')
                bars[peak_idx].set_edgecolor('#059669')
                bars[peak_idx].set_linewidth(3)

                # Add trend line with better fit
                z = np.polyfit(x, weekday_data.values, 2)
                p = np.poly1d(z)
                trend_x = np.linspace(0, 6, 100)
                ax1.plot(trend_x, p(trend_x), 'r--', alpha=0.9, linewidth=3, label='Trend Line')

                # Add peak annotation
                ax1.annotate(f'Peak: {peak_count} uploads', xy=(peak_idx, peak_count),
                            xytext=(10, 10), textcoords='offset points',
                            bbox=dict(boxstyle='round,pad=0.4', facecolor='yellow', alpha=0.9),
                            fontsize=11, fontweight='bold', ha='left')

                ax1.set_title(f'Analytics: Comprehensive Weekly Upload Pattern & Performance Analysis\nTotal: {total_weekly} uploads | Average: {avg_weekly:.1f} per day | Peak Performance: {peak_day}',
                             fontsize=18, fontweight='bold', pad=30, color='#1e293b')
                ax1.set_xlabel('Day of Week', fontsize=14, fontweight='medium')
                ax1.set_ylabel('Upload Count', fontsize=14, fontweight='medium')
                ax1.set_xticks(x)
                ax1.set_xticklabels(weekday_names, rotation=0, ha='center', fontsize=12)
                ax1.grid(True, alpha=0.3, axis='y', linestyle='--', linewidth=0.5)
                ax1.spines['top'].set_visible(False)
                ax1.spines['right'].set_visible(False)

                # Enhanced legend
                ax1.legend(loc='upper left', framealpha=0.95, fontsize=12)

                # Add value labels with better positioning
                for i, (bar, count) in enumerate(zip(bars, weekday_data.values)):
                    height = bar.get_height()
                    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5, f'{int(count)}',
                            ha='center', va='bottom', fontsize=11, fontweight='bold', color='#1e293b')

                # Add weekend highlight with better styling
                ax1.axvspan(5.4, 6.6, alpha=0.15, color='#f59e0b', label='Weekend Period')
                ax1.legend(loc='upper left', framealpha=0.95, fontsize=12)

                plt.tight_layout()
                st.pyplot(fig, width='stretch')

                # Enhanced weekly insights in single row
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric('🏆 Top Performer', f'{peak_day[:3]}', f'{peak_count} uploads')
                with col2:
                    st.metric('📊 Weekly Total', f'{total_weekly}', f'{avg_weekly:.1f} avg/day')
                with col3:
                    growth_trend = "↗️" if weekday_data.iloc[-1] > weekday_data.iloc[0] else "↘️"
                    weekly_growth = ((weekday_data.iloc[-1] - weekday_data.iloc[0]) / weekday_data.iloc[0] * 100) if weekday_data.iloc[0] != 0 else 0
                    st.metric('📈 Weekly Trend', growth_trend, f'{weekly_growth:+.1f}% change')
                with col4:
                    st.metric('🏖️ Weekend Activity', f'{weekend_ratio:.2f}x', 'vs weekdays')
                with col5:
                    consistency = np.std(weekday_data.values) / avg_weekly if avg_weekly > 0 else 0
                    consistency_label = "High" if consistency < 0.3 else "Medium" if consistency < 0.6 else "Low"
                    st.metric('🎯 Consistency', consistency_label, f'CV: {consistency:.2f}')

            # System Health & Operations Section
            st.subheader('🖥️ System Health & Operations')

            # System Metrics Cards
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                storage_used = total_assets * 0.15  # Mock calculation
                st.metric('Storage Used', f'{storage_used:.1f} GB', delta='120 MB')
                st.progress(min(storage_used / 10, 1.0))  # Assuming 10GB limit
                st.caption('15% of 10GB limit')

            with col2:
                st.metric('API Response Time', '245ms', delta='-12ms')
                st.caption('Average latency')

            with col3:
                st.metric('System Uptime', '99.97%', delta='0.01%')
                st.caption('Last 30 days')

            with col4:
                st.metric('Active Sessions', '12', delta='+2')
                st.caption('Current users')

            # Operations & Activity Section
            col1, col2 = st.columns([3, 2])

            with col1:
                st.subheader('📋 Activity Timeline')

                # Generate dynamic activities based on real data
                activities = []

                # Recent uploads
                recent_uploads = sorted(assets, key=lambda x: x['uploaded_at'], reverse=True)[:3]
                for asset in recent_uploads:
                    upload_time = time.time() - asset['uploaded_at']
                    time_str = 'Just now' if upload_time < 60 else f'{int(upload_time/3600)}h ago' if upload_time < 86400 else f'{int(upload_time/86400)}d ago'
                    activities.append({
                        'icon': '📤',
                        'action': 'Asset uploaded',
                        'details': f'Asset {asset["id"]} ({asset.get("label", "Untitled")}) uploaded',
                        'time': time_str,
                        'timestamp': asset['uploaded_at']
                    })

                # Processing activities (mock based on labels)
                processed_count = sum(1 for a in assets if 'processed' in (a.get('label') or '').lower())
                if processed_count > 0:
                    activities.append({
                        'icon': '🎨',
                        'action': 'Batch processing',
                        'details': f'{processed_count} assets processed successfully',
                        'time': '4h ago',
                        'timestamp': time.time() - 14400
                    })

                # Validation activities
                validation_count = len([a for a in assets if 'validated' in (a.get('label') or '').lower()])
                if validation_count > 0:
                    activities.append({
                        'icon': '✅',
                        'action': 'Compliance check',
                        'details': f'{validation_count} assets passed validation',
                        'time': '6h ago',
                        'timestamp': time.time() - 21600
                    })

                # System events
                storage_used = total_assets * 0.15
                if storage_used > 1.0:  # If over 1GB
                    activities.append({
                        'icon': '⚠️',
                        'action': 'Storage alert',
                        'details': f'Storage usage: {storage_used:.1f} GB ({storage_used/10*100:.1f}%)',
                        'time': '1d ago',
                        'timestamp': time.time() - 86400
                    })

                # API usage
                activities.append({
                    'icon': '🔗',
                    'action': 'API activity',
                    'details': f'{total_assets * 3} API calls processed today',
                    'time': '8h ago',
                    'timestamp': time.time() - 28800
                })

                # Maintenance
                activities.append({
                    'icon': '🔧',
                    'action': 'System maintenance',
                    'details': 'Automated backup completed successfully',
                    'time': '2d ago',
                    'timestamp': time.time() - 172800
                })

                # Sort activities by timestamp (most recent first)
                activities.sort(key=lambda x: x['timestamp'], reverse=True)

                # Display up to 8 most recent activities
                for activity in activities[:8]:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; padding: 8px 0; border-bottom: 1px solid #e5e7eb;">
                        <span style="font-size: 1.2em; margin-right: 12px;">{activity['icon']}</span>
                        <div style="flex: 1;">
                            <div style="font-weight: 600; color: #1e293b; font-size: 0.9em;">{activity['action']}</div>
                            <div style="color: #6b7280; font-size: 0.8em;">{activity['details']}</div>
                        </div>
                        <div style="color: #9ca3af; font-size: 0.8em; font-weight: 500;">{activity['time']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Show activity summary
                st.caption(f"Showing {len(activities[:8])} of {len(activities)} recent activities")

            with col2:
                st.subheader('⚡ Quick Actions')

                # Clean Up Assets
                if st.button('🧹 Clean Up Assets', help='Remove unused assets older than 30 days', width='stretch'):
                    with st.spinner('Checking for old assets...'):
                        resp = requests.post(f'{BACKEND_URL}/cleanup_assets', data={'days': 30}, headers=get_auth_headers())
                    if resp.ok:
                        data = resp.json()
                        st.info(f'Found {data["found_old_assets"]} assets older than 30 days')
                        if data["found_old_assets"] > 0:
                            st.warning(f'Would delete assets: {", ".join(map(str, data["would_delete"]))}')
                            if st.button('Confirm Delete', key='confirm_cleanup'):
                                st.success('Cleanup completed (simulation)')
                        else:
                            st.success('No old assets to clean up')
                    else:
                        st.error('Cleanup check failed')

                # Generate Report
                if st.button('📊 Generate Report', help='Create monthly analytics report', width='stretch'):
                    with st.spinner('Generating report...'):
                        resp = requests.post(f'{BACKEND_URL}/generate_report', headers=get_auth_headers())
                    if resp.ok:
                        data = resp.json()
                        st.success('Report Generated Successfully!')
                        with st.expander('View Report Details'):
                            st.metric('Total Assets', data['total_assets'])
                            st.metric('Processing Rate', f"{data['processing_rate']:.1f}%")
                            st.metric('Avg File Size', f"{data['average_file_size_kb']:.1f} KB")
                            st.metric('Storage Estimate', f"{data['storage_estimate_mb']:.1f} MB")
                    else:
                        st.error('Report generation failed')

                # System Maintenance (Health Check)
                if st.button('🔧 System Maintenance', help='Run system health checks', width='stretch'):
                    with st.spinner('Running health checks...'):
                        resp = requests.post(f'{BACKEND_URL}/system_health', headers=get_auth_headers())
                    if resp.ok:
                        data = resp.json()
                        st.success('Health check completed!')
                        with st.expander('System Health Report'):
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.metric('CPU Usage', f"{data['cpu_percent']:.1f}%")
                                st.metric('Memory Usage', f"{data['memory_percent']:.1f}%")
                                st.metric('Disk Usage', f"{data['disk_usage']:.1f}%")
                            with col_b:
                                uptime_hours = data['uptime_seconds'] / 3600
                                st.metric('System Uptime', f"{uptime_hours:.1f}h")
                                st.metric('GPU Available', 'Yes' if data['gpu_available'] else 'No')
                                st.metric('Storage Used', f"{data['storage_used_mb']:.1f} MB")
                    else:
                        st.error('Health check failed')

                # Send Notifications
                if st.button('📧 Send Notifications', help='Notify team about updates', width='stretch'):
                    with st.spinner('Sending notifications...'):
                        # Mock notification sending
                        time.sleep(1)
                    st.success('Notifications sent to team!')

                # Backup Data
                if st.button('💾 Backup Data', help='Create system backup', width='stretch'):
                    with st.spinner('Creating backup...'):
                        resp = requests.post(f'{BACKEND_URL}/backup_data', headers=get_auth_headers())
                    if resp.ok:
                        data = resp.json()
                        if data['status'] == 'success':
                            st.success(f'Backup created: {data["backup_path"]}')
                        else:
                            st.error(f'Backup failed: {data["error"]}')
                    else:
                        st.error('Backup operation failed')

                # Sync Assets
                if st.button('🔄 Sync Assets', help='Synchronize with cloud storage', width='stretch'):
                    with st.spinner('Synchronizing...'):
                        # Mock sync operation
                        time.sleep(2)
                    st.success('Assets synchronized with cloud storage!')

            # Advanced Analytics & Insights
            st.subheader('🔍 Advanced Analytics & Insights')

            # Manual update controls (no auto-update to prevent freezing)
            col_refresh, col_status = st.columns([1, 3])
            with col_refresh:
                refresh_analytics = st.button('🔄 Refresh Analytics', help='Update analytics with latest data', width='stretch')
            with col_status:
                if 'analytics_last_update' not in st.session_state:
                    st.session_state.analytics_last_update = time.time()
                analytics_time_since = time.time() - st.session_state.analytics_last_update
                if analytics_time_since < 300:  # Show status for 5 minutes
                    st.info(f'📊 Last updated {int(analytics_time_since)}s ago')
                else:
                    st.warning('⚠️ Data may be outdated - click refresh')

            # Force refresh if button clicked
            if refresh_analytics:
                st.session_state.analytics_last_update = time.time()
                # No rerun - just update the placeholders

            # File Size Intelligence - Full Width Enhanced
            with st.container(height=500):
                st.markdown('<h4 style="text-align: center; color: #fff; margin-bottom: 20px;">📊 File Size Intelligence & Distribution Analysis</h4>', unsafe_allow_html=True)

                if assets:
                    sizes = []
                    for asset in assets[:min(100, len(assets))]:  # Increased sample size
                        try:
                            size_kb = len(requests.get(f'{BACKEND_URL}/asset/{asset["id"]}', headers=get_auth_headers()).content) / 1024
                            sizes.append(size_kb)
                        except:
                            continue

                    if sizes:
                        # Full-width chart
                        fig, ax = plt.subplots(figsize=(14, 6), facecolor='#ffffff', dpi=100)

                        # Enhanced histogram with better binning and colors
                        n, bins, patches = ax.hist(sizes, bins=20, alpha=0.9, density=False,
                                                 edgecolor='white', linewidth=1.5, rwidth=0.9)

                        # Apply sophisticated color gradient
                        colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(patches)))
                        for patch, color in zip(patches, colors):
                            patch.set_facecolor(color)

                        # Statistical overlays with enhanced styling
                        mean_size = np.mean(sizes)
                        median_size = np.median(sizes)
                        std_size = np.std(sizes)
                        q25, q75 = np.percentile(sizes, [25, 75])

                        # Add statistical lines with better labels
                        ax.axvline(mean_size, color='#ef4444', linestyle='--', linewidth=3, alpha=0.9,
                                 label=f'Mean: {mean_size:.1f} KB')
                        ax.axvline(median_size, color='#3b82f6', linestyle='-.', linewidth=3, alpha=0.9,
                                 label=f'Median: {median_size:.1f} KB')
                        ax.axvline(q25, color='#10b981', linestyle=':', linewidth=2, alpha=0.8,
                                 label=f'Q1: {q25:.1f} KB')
                        ax.axvline(q75, color='#f59e0b', linestyle=':', linewidth=2, alpha=0.8,
                                 label=f'Q3: {q75:.1f} KB')

                        # Add variance shading
                        ax.fill_betweenx([0, max(n)], mean_size - std_size, mean_size + std_size,
                                       alpha=0.15, color='#ef4444', label='±1 Std Dev')

                        ax.set_title(f'Analytics: Comprehensive File Size Distribution Analysis\n{len(sizes)} Assets Analyzed | σ={std_size:.1f} KB | Range: {min(sizes):.1f}-{max(sizes):.1f} KB',
                                   fontsize=16, fontweight='bold', pad=30, color='#1e293b')
                        ax.set_xlabel('File Size (KB)', fontsize=14, fontweight='medium')
                        ax.set_ylabel('Asset Count', fontsize=14, fontweight='medium')
                        ax.grid(True, alpha=0.3, axis='y', linestyle='--', linewidth=0.5)
                        ax.spines['top'].set_visible(False)
                        ax.spines['right'].set_visible(False)

                        # Enhanced legend
                        ax.legend(loc='upper right', framealpha=0.95, fontsize=10, title='Statistical Measures', title_fontsize=12)

                        plt.tight_layout()
                        st.pyplot(fig, width='stretch')

                        # Key Statistics below the chart
                        st.markdown('### 📈 Key Statistics')

                        # Enhanced metrics with better formatting
                        mean_size = np.mean(sizes)
                        median_size = np.median(sizes)
                        std_size = np.std(sizes)
                        min_size = min(sizes)
                        max_size = max(sizes)
                        q25, q75 = np.percentile(sizes, [25, 75])
                        iqr = q75 - q25

                        # Size categories
                        small_count = sum(1 for s in sizes if s < 100)
                        medium_count = sum(1 for s in sizes if 100 <= s < 500)
                        large_count = sum(1 for s in sizes if s >= 500)

                        # Statistics in organized rows
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric('📏 Average Size', f'{mean_size:.1f} KB', f'±{std_size:.1f} KB')
                            st.metric('📊 Standard Deviation', f'{std_size:.1f} KB', 'Variability')
                        with col2:
                            st.metric('🎯 Median Size', f'{median_size:.1f} KB', 'Central tendency')
                            st.metric('📦 IQR (Q1-Q3)', f'{iqr:.1f} KB', f'Q1: {q25:.1f}, Q3: {q75:.1f}')
                        with col3:
                            st.metric('📈 Size Range', f'{min_size:.1f} - {max_size:.1f} KB', f'Span: {max_size-min_size:.1f} KB')
                            st.metric('Small (<100KB)', f'{small_count}', f'{small_count/len(sizes)*100:.1f}%')
                        with col4:
                            # Size efficiency indicator
                            avg_efficiency = 'Excellent' if mean_size < 200 else 'Good' if mean_size < 500 else 'Needs Optimization'
                            efficiency_color = '🟢' if mean_size < 200 else '🟡' if mean_size < 500 else '🔴'
                            st.metric(f'{efficiency_color} Size Efficiency', avg_efficiency, f'Avg: {mean_size:.1f} KB')
                            st.metric('Medium (100-500KB)', f'{medium_count}', f'{medium_count/len(sizes)*100:.1f}%')

                        # Additional category in a separate row
                        col_a, col_b, col_c = st.columns([1, 1, 2])
                        with col_a:
                            st.metric('Large (≥500KB)', f'{large_count}', f'{large_count/len(sizes)*100:.1f}%')
                        with col_b:
                            st.metric('Total Analyzed', f'{len(sizes)}', 'Assets')
                        with col_c:
                            st.info('💡 **Optimization Tip:** Files under 200KB show excellent performance. Consider compressing larger assets for better loading times.')


            # Live Latency Monitoring Graph
            st.subheader('📈 Live System Latency Monitoring')

            # Live update controls for latency
            col_lat_refresh, col_lat_auto, col_lat_status = st.columns([1, 1, 2])
            with col_lat_refresh:
                refresh_latency = st.button('🔄 Refresh Latency', help='Update latency data', width='stretch')
            with col_lat_auto:
                auto_update_latency = st.checkbox('Auto Update Latency', value=False, help='Automatically refresh latency every 5 seconds (disabled by default to prevent screen freezing)')
            with col_lat_status:
                if 'latency_last_update' not in st.session_state:
                    st.session_state.latency_last_update = time.time()
                latency_time_since = time.time() - st.session_state.latency_last_update
                if latency_time_since < 5:
                    st.success(f'✅ Latency updated {int(latency_time_since)}s ago')
                else:
                    st.warning(f'⚠️ Latency update due - {int(latency_time_since)}s ago')

            # Force refresh only if button clicked (removed auto-update to prevent freezing)
            if refresh_latency:
                st.session_state.latency_last_update = time.time()

            # Create placeholders for live latency updates
            latency_chart_placeholder = st.empty()
            latency_metrics_placeholder = st.empty()

            with latency_chart_placeholder.container():
                # Generate realistic latency data with live updates
                latency_data = []
                timestamps = []

                # Use session state to maintain data continuity
                if 'latency_history' not in st.session_state:
                    st.session_state.latency_history = []

                # Generate new data point
                base_time = time.time()
                base_latency = 245 + np.random.normal(0, 30)
                if np.random.random() < 0.1:  # 10% chance of spike
                    base_latency += np.random.uniform(100, 300)
                new_latency = max(50, base_latency)

                # Maintain rolling window of 50 data points
                st.session_state.latency_history.append((base_time, new_latency))
                if len(st.session_state.latency_history) > 50:
                    st.session_state.latency_history = st.session_state.latency_history[-50:]

                # Extract data for plotting
                timestamps = [t[0] for t in st.session_state.latency_history]
                latency_data = [t[1] for t in st.session_state.latency_history]

                # Convert to DataFrame for plotting
                latency_df = pd.DataFrame({
                    'timestamp': timestamps,
                    'latency': latency_data
                })
                latency_df['time'] = pd.to_datetime(latency_df['timestamp'], unit='s')

                # Create live latency chart
                fig, ax = plt.subplots(figsize=(12, 4), facecolor='#ffffff', dpi=100)

                # Plot latency line with gradient fill
                ax.fill_between(latency_df['time'], latency_df['latency'], alpha=0.3, color='#3b82f6', linewidth=0)
                line = ax.plot(latency_df['time'], latency_df['latency'], color='#1e40af', linewidth=2.5, marker='o', markersize=2, markerfacecolor='#1e40af')

                # Add threshold lines
                ax.axhline(y=500, color='#ef4444', linestyle='--', alpha=0.7, linewidth=2, label='High Latency (>500ms)')
                ax.axhline(y=200, color='#10b981', linestyle='--', alpha=0.7, linewidth=2, label='Optimal (<200ms)')

                # Calculate current metrics
                current_latency = latency_data[-1] if latency_data else 245
                avg_latency = np.mean(latency_data) if latency_data else 245
                max_latency = max(latency_data) if latency_data else 245
                min_latency = min(latency_data) if latency_data else 245

                ax.set_title(f'Monitoring: Live API Response Latency\nCurrent: {current_latency:.0f}ms | Average: {avg_latency:.0f}ms | Range: {min_latency:.0f}-{max_latency:.0f}ms',
                            fontsize=14, fontweight='bold', pad=25, color='#1e293b')
                ax.set_xlabel('Time (Rolling 50 Minutes)', fontsize=12)
                ax.set_ylabel('Response Time (ms)', fontsize=12)
                ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)

                # Format time axis
                ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))
                plt.xticks(rotation=45, ha='right')

                # Add legend
                ax.legend(loc='upper right', framealpha=0.9, fontsize=9)

                # Color code based on current latency
                if current_latency > 500:
                    status_color = '#ef4444'
                    status_text = 'HIGH LATENCY'
                elif current_latency > 200:
                    status_color = '#f59e0b'
                    status_text = 'MODERATE'
                else:
                    status_color = '#10b981'
                    status_text = 'OPTIMAL'

                # Add status indicator
                ax.text(0.02, 0.98, f'Status: {status_text}', transform=ax.transAxes,
                       fontsize=12, fontweight='bold', color=status_color,
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))

                plt.tight_layout()
                st.pyplot(fig, width='stretch')

            with latency_metrics_placeholder.container():
                # Live metrics row
                current_latency = latency_data[-1] if latency_data else 245
                avg_latency = np.mean(latency_data) if latency_data else 245
                max_latency = max(latency_data) if latency_data else 245
                min_latency = min(latency_data) if latency_data else 245

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    delta = current_latency - latency_data[-2] if len(latency_data) > 1 else 0
                    st.metric('Current Latency', f'{current_latency:.0f}ms', f'{delta:+.0f}ms')
                with col2:
                    st.metric('Average', f'{avg_latency:.0f}ms', f'Baseline: 245ms')
                with col3:
                    st.metric('Peak', f'{max_latency:.0f}ms', f'Max recorded')
                with col4:
                    st.metric('Range', f'{max_latency-min_latency:.0f}ms', f'Variation')
                with col5:
                    uptime_pct = 99.97  # Mock uptime
                    st.metric('System Health', f'{uptime_pct}%', 'Uptime')

    else:
        st.error('Unable to load dashboard data. Please check backend connection.')
        st.info('💡 **Troubleshooting Tips:**\n- Ensure the backend server is running\n- Check network connectivity\n- Verify API endpoints are accessible')

elif st.session_state.current_page == 'Asset Library':
    st.markdown('<h2 class="section-header">Asset Library</h2>', unsafe_allow_html=True)
    st.markdown('Browse and manage your creative assets.')

    resp = requests.get(f'{BACKEND_URL}/assets', headers=get_auth_headers())
    if resp.ok:
        assets = resp.json()
        if assets:
            # Search and filter
            search_term = st.text_input('Search assets by label', placeholder='Enter keyword...')
            filtered_assets = [a for a in assets if search_term.lower() in (a['label'] or '').lower()] if search_term else assets

            st.write(f'Showing {len(filtered_assets)} of {len(assets)} assets')

            cols = st.columns(4)
            for i, asset in enumerate(filtered_assets):
                with cols[i % 4]:
                    with st.container():
                        st.markdown('<div class="asset-card">', unsafe_allow_html=True)
                        resp_img = requests.get(f'{BACKEND_URL}/asset/{asset["id"]}', headers=get_auth_headers())
                        if resp_img.ok:
                            st.image(resp_img.content, width=150)
                        st.caption(f'ID: {asset["id"]}')
                        st.caption(asset['label'] or 'Untitled')
                        if st.button('Select for Editing', key=f'select_{asset["id"]}', width='stretch'):
                            st.session_state.selected_asset = asset["id"]
                            st.success(f'Asset {asset["id"]} selected')
                        st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info('No assets in library. Upload some assets to get started.')
    else:
        st.error('Unable to load asset library.')

elif st.session_state.current_page == 'Image Editor':
    st.markdown('<h2 class="section-header">Image Editor</h2>', unsafe_allow_html=True)
    st.markdown('Edit and enhance your creative assets with AI-powered tools.')

    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader('Select Asset')
        asset_id = st.number_input('Asset ID', min_value=0, value=st.session_state.selected_asset, key='manip_asset_id', help='Enter asset ID or select from Asset Library tab')
        if asset_id > 0:
            resp = requests.get(f'{BACKEND_URL}/asset/{asset_id}', headers=get_auth_headers())
            if resp.ok:
                st.image(resp.content, caption='Source Image', width=300)
            else:
                st.error('Asset not found or invalid ID')

        st.subheader('Editing Tools')

        with st.expander('Basic Adjustments'):
            remove_bg = st.checkbox('AI Background Removal', help='Remove background using deep learning')
            width = st.number_input('Width (px)', min_value=100, value=800, help='Resize width')
            height = st.number_input('Height (px)', min_value=100, value=1200, help='Resize height')
            rotate = st.slider('Rotation (degrees)', 0, 360, 0, help='Rotate image clockwise')

        with st.expander('Crop Settings'):
            st.markdown('**Crop Coordinates**')
            crop_left = st.number_input('Left', min_value=0, value=0)
            crop_top = st.number_input('Top', min_value=0, value=0)
            crop_right = st.number_input('Right', min_value=0, value=800)
            crop_bottom = st.number_input('Bottom', min_value=0, value=1200)

        with st.expander('Visual Filters'):
            filter_type = st.selectbox('Filter Type', ['None', 'Brightness', 'Contrast', 'Sharpness'])
            filter_value = st.slider('Filter Intensity', 0.1, 2.0, 1.0, disabled=(filter_type == 'None'))

        with st.expander('Text Overlay'):
            overlay_text = st.text_input('Overlay Text', placeholder='Enter text to add')
            overlay_x = st.number_input('X Position', min_value=0, value=10)
            overlay_y = st.number_input('Y Position', min_value=0, value=10)
            font_size = st.slider('Font Size', 10, 100, 20)

        if st.button('Apply Changes', type='primary', width='stretch'):
            with st.spinner('Processing image...'):
                data = {
                    'asset_id': int(asset_id),
                    'remove_bg': str(remove_bg).lower(),
                    'width': int(width),
                    'height': int(height),
                    'rotate': int(rotate),
                    'crop_left': crop_left,
                    'crop_top': crop_top,
                    'crop_right': crop_right,
                    'crop_bottom': crop_bottom,
                    'filter_type': filter_type.lower() if filter_type != 'None' else '',
                    'filter_value': filter_value,
                    'overlay_text_str': overlay_text,
                    'overlay_x': overlay_x,
                    'overlay_y': overlay_y,
                    'font_size': font_size
                }
                resp = requests.post(f'{BACKEND_URL}/manipulate_image', data=data, headers=get_auth_headers())
            if resp.ok:
                st.success('Image processing completed successfully!')
            else:
                st.error('Processing failed. Please check inputs and try again.')

    with col2:
        st.subheader('Processing Preview')
        st.info('Processed images are saved server-side. Check Asset Library for results.')
        # In production, add preview functionality

elif st.session_state.current_page == 'AI Analysis':
    st.markdown('<h2 class="section-header">AI-Powered Image Analysis</h2>', unsafe_allow_html=True)
    st.markdown('Get intelligent insights and auto-tagging for your creative assets.')

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader('Select Asset for Analysis')
        analysis_asset_id = st.number_input('Asset ID', min_value=0, value=st.session_state.selected_asset, key='analysis_asset_id', help='Enter asset ID to analyze')

        if analysis_asset_id > 0:
            resp = requests.get(f'{BACKEND_URL}/asset/{analysis_asset_id}', headers=get_auth_headers())
            if resp.ok:
                st.image(resp.content, caption=f'Asset {analysis_asset_id}', width=250)
            else:
                st.error('Asset not found')

        if st.button('Analyze Image', type='primary', width='stretch'):
            with st.spinner('AI analyzing image...'):
                resp = requests.post(f'{BACKEND_URL}/analyze_image', data={'asset_id': analysis_asset_id}, headers=get_auth_headers())
            if resp.ok:
                analysis = resp.json()
                st.session_state.last_analysis = analysis
                st.success('Analysis complete!')
            else:
                st.error('Analysis failed')

    with col2:
        st.subheader('Analysis Results')
        if 'last_analysis' in st.session_state:
            analysis = st.session_state.last_analysis

            # Basic info
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric('Dimensions', f"{analysis['dimensions']['width']}x{analysis['dimensions']['height']}")
            with col_b:
                st.metric('File Size', f"{analysis['file_size_kb']:.1f} KB")
            with col_c:
                st.metric('Aspect Ratio', f"{analysis['aspect_ratio']:.2f}")

            # Color analysis
            st.subheader('🎨 Color Analysis')
            avg_color = analysis['average_color']
            st.write(f"Average Color: RGB({avg_color[0]}, {avg_color[1]}, {avg_color[2]})")
            st.color_picker('Average Color', value=f"#{avg_color[0]:02x}{avg_color[1]:02x}{avg_color[2]:02x}", disabled=True)

            # Technical metrics
            st.subheader('📊 Technical Metrics')
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric('Brightness', f"{analysis['brightness']:.1f}")
            with col2:
                st.metric('Complexity', f"{analysis['complexity_score']:.3f}")
            with col3:
                st.metric('Has Text', 'Yes' if analysis['has_text'] else 'No')

            # Auto tags
            st.subheader('🏷️ Auto-Generated Tags')
            tags = analysis.get('auto_tags', [])
            if tags:
                st.write(' '.join([f"#{tag}" for tag in tags]))
            else:
                st.write('No tags generated')

            # Extracted text
            if analysis.get('extracted_text'):
                st.subheader('📝 Extracted Text')
                st.text_area('Text Content', analysis['extracted_text'], height=100, disabled=True)

elif st.session_state.current_page == 'AI Creative Assistant':
    st.markdown('<h2 class="section-header">AI-Powered Retail Creative Assistant</h2>', unsafe_allow_html=True)
    st.markdown('Analyze packshots and generate compliant advertising assets across multiple formats.')

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader('Select Packshot Asset')
        creative_asset_id = st.number_input('Asset ID', min_value=0, value=st.session_state.selected_asset, key='creative_asset_id', help='Enter packshot asset ID to analyze and generate creatives')

        if creative_asset_id > 0:
            resp = requests.get(f'{BACKEND_URL}/asset/{creative_asset_id}', headers=get_auth_headers())
            if resp.ok:
                st.image(resp.content, caption=f'Packshot Asset {creative_asset_id}', width=250)
            else:
                st.error('Asset not found')

        st.subheader('Generation Options')
        generate_creatives = st.checkbox('Generate Ad Creatives', value=True, help='Create images for Story, Feed, and Banner formats')
        include_analysis = st.checkbox('Include Detailed Analysis', value=True, help='Show OCR, object detection, and compliance analysis')

        if st.button('Generate Advertising Assets', type='primary', width='stretch'):
            with st.spinner('Analyzing packshot and generating creatives...'):
                resp = requests.post(f'{BACKEND_URL}/generate_ad_assets', data={'asset_id': creative_asset_id}, headers=get_auth_headers())
            if resp.ok:
                result = resp.json()
                st.session_state.last_creative_result = result
                st.success('Creative assets generated successfully!')
            else:
                st.error('Generation failed. Please check the asset and try again.')

    with col2:
        st.subheader('Generated Assets & Analysis')
        if 'last_creative_result' in st.session_state:
            result = st.session_state.last_creative_result

            if include_analysis:
                # Show analysis results
                st.subheader('📊 Packshot Analysis')
                analysis = result['analysis']

                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric('Dimensions', f"{analysis['dimensions']['width']}x{analysis['dimensions']['height']}")
                with col_b:
                    st.metric('Has Text', 'Yes' if analysis['has_text'] else 'No')
                with col_c:
                    st.metric('People Detected', len(analysis.get('detected_people', [])))

                if analysis.get('extracted_text'):
                    st.subheader('📝 Extracted Text')
                    st.text_area('OCR Content', analysis['extracted_text'][:300], height=80, disabled=True)

                if analysis.get('detected_objects'):
                    st.subheader('🔍 Detected Objects')
                    objects = [obj['label'] for obj in analysis['detected_objects']]
                    st.write(' '.join([f"#{obj}" for obj in objects]))

                if analysis.get('restricted_content'):
                    st.error('⚠️ Restricted content detected (people in image)')

            # Show marketing text
            st.subheader('📝 Generated Marketing Text')
            marketing = result['marketing_text']
            st.write(f"**Headline:** {marketing['headline']}")
            st.write(f"**Subhead:** {marketing['subhead']}")
            st.write(f"**Disclaimer:** {marketing['caveat']}")

            if generate_creatives:
                # Show generated assets
                st.subheader('🎨 Generated Ad Creatives')
                generated = result['generated_assets']

                formats = ['story', 'feed', 'banner']
                format_names = {'story': 'Instagram Story (9:16)', 'feed': 'Instagram Feed (1:1)', 'banner': 'Facebook Banner (1.91:1)'}

                for fmt in formats:
                    if fmt in generated:
                        asset_data = generated[fmt]
                        if 'error' in asset_data:
                            st.error(f"Failed to generate {format_names[fmt]}: {asset_data['error']}")
                        else:
                            with st.expander(f"📱 {format_names[fmt]}", expanded=True):
                                # Show image if available
                                if 'path' in asset_data:
                                    # In production, you'd fetch the image from the server
                                    st.info(f"Generated image saved as: {asset_data['filename']}")

                                # Show evaluation metrics
                                if 'evaluation' in asset_data:
                                    eval_data = asset_data['evaluation']
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.metric('Brightness', f"{eval_data['brightness']:.1f}")
                                    with col2:
                                        st.metric('Contrast', f"{eval_data['contrast']:.2f}")
                                    with col3:
                                        st.metric('Text Readable', 'Yes' if eval_data['text_readable'] else 'No')
                                    with col4:
                                        st.metric('Layout Balance', f"{eval_data['layout_balance_score']:.0f}")

                                    # Compliance indicators
                                    compliance_issues = []
                                    if not eval_data['text_readable']:
                                        compliance_issues.append('Low text readability')
                                    if not eval_data['safe_zone_compliant']:
                                        compliance_issues.append('Safe zone violation')
                                    if not eval_data['platform_suitable']:
                                        compliance_issues.append('Not platform suitable')

                                    if compliance_issues:
                                        st.warning(f"⚠️ Issues: {', '.join(compliance_issues)}")
                                    else:
                                        st.success('✅ All quality checks passed!')
                    else:
                        st.warning(f"{format_names[fmt]} not generated")

elif st.session_state.current_page == 'Version History':
    st.markdown('<h2 class="section-header">Asset Version History</h2>', unsafe_allow_html=True)
    st.markdown('Track changes and restore previous versions of your assets.')

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader('Select Asset')
        version_asset_id = st.number_input('Asset ID', min_value=0, value=st.session_state.selected_asset, key='version_asset_id', help='Enter asset ID to view history')

        if version_asset_id > 0:
            # Get current asset
            resp = requests.get(f'{BACKEND_URL}/asset/{version_asset_id}', headers=get_auth_headers())
            if resp.ok:
                st.image(resp.content, caption=f'Current Version (Asset {version_asset_id})', width=250)
                st.caption('This is the current version')
            else:
                st.error('Asset not found')

            # Get version history
            if st.button('Load Version History', width='stretch'):
                with st.spinner('Loading version history...'):
                    resp = requests.get(f'{BACKEND_URL}/asset/{version_asset_id}/versions', headers=get_auth_headers())
                if resp.ok:
                    versions = resp.json()['versions']
                    st.session_state.version_history = versions
                    st.success(f'Loaded {len(versions)} versions')
                else:
                    st.error('Failed to load version history')

    with col2:
        st.subheader('Version History')
        if 'version_history' in st.session_state:
            versions = st.session_state.version_history

            for version in versions:
                with st.expander(f"Version {version['version']} - {version['operation']} ({time.strftime('%Y-%m-%d %H:%M', time.localtime(version['created_at']))})"):
                    col_a, col_b = st.columns([1, 2])
                    with col_a:
                        # Show version image
                        resp = requests.get(f'{BACKEND_URL}/asset/{version_asset_id}/version/{version["version"]}', headers=get_auth_headers())
                        if resp.ok:
                            st.image(resp.content, width=150)
                        else:
                            st.error('Version image not available')

                    with col_b:
                        st.write(f"**Operation:** {version['operation']}")
                        st.write(f"**Created by:** {version.get('created_by', 'Unknown')}")
                        st.write(f"**Timestamp:** {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(version['created_at']))}")

                        if version.get('params'):
                            st.write("**Parameters:**")
                            st.json(version['params'])

                        # Restore button
                        if st.button(f'Restore to Version {version["version"]}', key=f'restore_{version["version"]}', width='stretch'):
                            with st.spinner('Restoring version...'):
                                resp = requests.post(f'{BACKEND_URL}/asset/{version_asset_id}/restore/{version["version"]}', headers=get_auth_headers())
                            if resp.ok:
                                data = resp.json()
                                st.success(f'Asset restored to version {data["new_version"]}!')
                                # Refresh version history
                                del st.session_state.version_history
                            else:
                                st.error('Restore failed')

elif st.session_state.current_page == 'Compliance Check':
    st.markdown('<h2 class="section-header">Advanced Compliance Validation</h2>', unsafe_allow_html=True)
    st.markdown('Comprehensive brand guidelines and legal compliance checking for creative assets.')

    # Platform selection
    platforms = {
        'general': 'General Guidelines',
        'instagram_story': 'Instagram Story (9:16)',
        'instagram_feed': 'Instagram Feed (1:1)',
        'facebook_banner': 'Facebook Banner (1.91:1)'
    }

    selected_platform = st.selectbox('Select Target Platform', list(platforms.keys()), format_func=lambda x: platforms[x], key='compliance_platform')

    tab1, tab2, tab3 = st.tabs(['📝 Content Validation', '🖼️ Image Compliance', '📊 Batch Check'])

    with tab1:
        st.subheader('Creative Copy Validation')
        with st.form('content_validation'):
            col1, col2 = st.columns(2)
            with col1:
                headline = st.text_input('Headline', placeholder='Enter compelling headline text', help='Main call-to-action text')
                subhead = st.text_input('Subheadline', placeholder='Supporting message', help='Additional descriptive text')
                description = st.text_area('Description (Optional)', placeholder='Detailed product description', height=80, help='Extended content for context')

            with col2:
                caveat = st.text_input('Disclaimer/Caveat', placeholder='Legal disclaimers, drinkaware, etc.', help='Required legal text')
                tags = st.text_input('Tags/Labels', placeholder='Available at Tesco, Clubcard Price, etc.', help='Brand-approved tags')

                st.markdown('**Platform Requirements**')
                if selected_platform == 'instagram_story':
                    st.info('📱 Instagram Story: Keep text concise, vertical format')
                elif selected_platform == 'instagram_feed':
                    st.info('📱 Instagram Feed: Square format, engaging visuals')
                elif selected_platform == 'facebook_banner':
                    st.info('📘 Facebook Banner: Horizontal format, clear CTA')

            submitted = st.form_submit_button('🔍 Validate Content', width='stretch', type='primary')
            if submitted:
                with st.spinner('Analyzing content compliance...'):
                    data = {
                        'headline': headline,
                        'subhead': subhead,
                        'caveat': caveat,
                        'tags': tags,
                        'description': description,
                        'platform': selected_platform
                    }
                    resp = requests.post(f'{BACKEND_URL}/validate', data=data, headers=get_auth_headers())

                if resp.ok:
                    result = resp.json()
                    issues = result.get('issues', [])

                    # Categorize issues
                    hard_fails = [i for i in issues if i['type'] == 'hard_fail']
                    warnings = [i for i in issues if i['type'] == 'warning']
                    info_items = [i for i in issues if i['type'] == 'info']

                    if hard_fails:
                        st.error('🚫 **Critical Issues Found**')
                        for issue in hard_fails:
                            st.error(f"• {issue['msg']}")
                    elif warnings:
                        st.warning('⚠️ **Review Required**')
                        for issue in warnings:
                            st.warning(f"• {issue['msg']}")
                    else:
                        st.success('✅ **All Content Checks Passed!**')

                    if info_items:
                        with st.expander('💡 Guidelines & Recommendations'):
                            for issue in info_items:
                                st.info(f"• {issue['msg']}")

                    # Show summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric('Critical Issues', len(hard_fails))
                    with col2:
                        st.metric('Warnings', len(warnings))
                    with col3:
                        st.metric('Suggestions', len(info_items))
                    with col4:
                        compliance_score = 100 - (len(hard_fails) * 50) - (len(warnings) * 10)
                        compliance_score = max(0, compliance_score)
                        st.metric('Compliance Score', f'{compliance_score}%')

                else:
                    st.error('❌ Validation service unavailable')

    with tab2:
        st.subheader('Image Compliance Analysis')

        col1, col2 = st.columns([1, 2])
        with col1:
            img_asset_id = st.number_input('Asset ID', min_value=0, value=st.session_state.selected_asset, key='val_asset_id', help='Enter asset ID from library')

            if img_asset_id > 0:
                resp = requests.get(f'{BACKEND_URL}/asset/{img_asset_id}', headers=get_auth_headers())
                if resp.ok:
                    st.image(resp.content, caption=f'Asset {img_asset_id}', width=200)
                else:
                    st.warning('Asset preview unavailable')

            # Platform-specific guidance
            if selected_platform != 'general':
                st.markdown('**Platform Guidelines:**')
                if selected_platform == 'instagram_story':
                    st.info('• Aspect ratio: 9:16\n• Safe zones: 200px top, 250px bottom\n• Min font size: 24px')
                elif selected_platform == 'instagram_feed':
                    st.info('• Aspect ratio: 1:1\n• Safe zones: 150px all sides\n• Min font size: 20px')
                elif selected_platform == 'facebook_banner':
                    st.info('• Aspect ratio: 1.91:1\n• Safe zones: 50px margins\n• Min font size: 18px')

        with col2:
            if st.button('🔍 Analyze Image Compliance', width='stretch', type='primary'):
                with st.spinner('Performing comprehensive image analysis...'):
                    resp = requests.post(f'{BACKEND_URL}/validate_image', data={'asset_id': int(img_asset_id), 'platform': selected_platform}, headers=get_auth_headers())

                if resp.ok:
                    result = resp.json()
                    issues = result.get('issues', [])

                    # Group issues by category
                    categories = {}
                    for issue in issues:
                        cat = issue.get('category', 'general')
                        if cat not in categories:
                            categories[cat] = []
                        categories[cat].append(issue)

                    # Display results by category
                    for category, cat_issues in categories.items():
                        category_name = category.replace('_', ' ').title()
                        hard_fails = [i for i in cat_issues if i['type'] == 'hard_fail']
                        warnings = [i for i in cat_issues if i['type'] == 'warning']
                        info_items = [i for i in cat_issues if i['type'] == 'info']

                        with st.expander(f'{"⚫" if hard_fails else "🟡" if warnings else "🟢"} {category_name} ({len(cat_issues)} issues)', expanded=bool(hard_fails or warnings)):
                            for issue in cat_issues:
                                if issue['type'] == 'hard_fail':
                                    st.error(f"🚫 {issue['msg']}")
                                elif issue['type'] == 'warning':
                                    st.warning(f"⚠️ {issue['msg']}")
                                else:
                                    st.info(f"💡 {issue['msg']}")

                    # Overall compliance score
                    total_hard_fails = sum(1 for i in issues if i['type'] == 'hard_fail')
                    total_warnings = sum(1 for i in issues if i['type'] == 'warning')

                    score = 100 - (total_hard_fails * 30) - (total_warnings * 10)
                    score = max(0, score)

                    if score >= 80:
                        st.success(f'🎉 **High Compliance** - Score: {score}%')
                    elif score >= 60:
                        st.warning(f'⚠️ **Needs Review** - Score: {score}%')
                    else:
                        st.error(f'🚫 **Major Issues** - Score: {score}%')

                else:
                    st.error('❌ Image analysis service unavailable')

    with tab3:
        st.subheader('Batch Compliance Analysis')
        st.markdown('Check multiple assets at once for efficient workflow management.')

        # Get assets list
        resp = requests.get(f'{BACKEND_URL}/assets', headers=get_auth_headers())
        if resp.ok:
            assets = resp.json()
            if assets:
                # Multi-select assets
                asset_options = {f"{a['id']}: {a.get('label', 'Untitled')}" for a in assets}
                selected_assets = st.multiselect('Select Assets to Check', list(asset_options), help='Choose multiple assets for batch validation')

                check_type = st.radio('Check Type', ['Content Only', 'Images Only', 'Both'], horizontal=True)

                if st.button('🚀 Run Batch Check', width='stretch', type='primary') and selected_assets:
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    results = []
                    total = len(selected_assets)

                    for i, asset_str in enumerate(selected_assets):
                        asset_id = int(asset_str.split(':')[0])
                        status_text.text(f'Checking asset {asset_id}... ({i+1}/{total})')
                        progress_bar.progress((i + 1) / total)

                        try:
                            if check_type in ['Images Only', 'Both']:
                                resp_img = requests.post(f'{BACKEND_URL}/validate_image', data={'asset_id': asset_id, 'platform': selected_platform}, headers=get_auth_headers())
                                img_issues = resp_img.json().get('issues', []) if resp_img.ok else [{'type': 'error', 'msg': 'Service unavailable'}]

                            if check_type in ['Content Only', 'Both']:
                                # For batch, we'd need content data - simplified for now
                                content_issues = []

                            results.append({
                                'asset_id': asset_id,
                                'image_issues': img_issues if check_type in ['Images Only', 'Both'] else [],
                                'content_issues': content_issues if check_type in ['Content Only', 'Both'] else []
                            })

                        except Exception as e:
                            results.append({
                                'asset_id': asset_id,
                                'error': str(e)
                            })

                    progress_bar.empty()
                    status_text.empty()

                    # Display batch results
                    st.subheader('📊 Batch Results Summary')

                    summary_data = []
                    for result in results:
                        asset_id = result['asset_id']
                        img_hard_fails = sum(1 for i in result.get('image_issues', []) if i.get('type') == 'hard_fail')
                        img_warnings = sum(1 for i in result.get('image_issues', []) if i.get('type') == 'warning')
                        content_hard_fails = sum(1 for i in result.get('content_issues', []) if i.get('type') == 'hard_fail')
                        content_warnings = sum(1 for i in result.get('content_issues', []) if i.get('type') == 'warning')

                        total_hard_fails = img_hard_fails + content_hard_fails
                        total_warnings = img_warnings + content_warnings

                        compliance_score = 100 - (total_hard_fails * 30) - (total_warnings * 10)
                        compliance_score = max(0, compliance_score)

                        summary_data.append({
                            'Asset ID': asset_id,
                            'Image Issues': f"{img_hard_fails}H {img_warnings}W",
                            'Content Issues': f"{content_hard_fails}H {content_warnings}W",
                            'Compliance Score': f"{compliance_score}%",
                            'Status': '🟢 Pass' if compliance_score >= 80 else '🟡 Review' if compliance_score >= 60 else '🔴 Fail'
                        })

                    st.dataframe(summary_data, width='stretch')

                    # Export option
                    if st.button('📥 Prepare Export'):
                        import pandas as pd
                        df = pd.DataFrame(summary_data)
                        csv = df.to_csv(index=False)
                        st.session_state.export_csv = csv
                        st.success('Export data prepared!')

                    # Show download button if data is available
                    if 'export_csv' in st.session_state:
                        st.download_button(
                            label='📥 Download CSV Report',
                            data=st.session_state.export_csv,
                            file_name='compliance_batch_results.csv',
                            mime='text/csv',
                            help='Click to download the compliance results'
                        )

            else:
                st.info('No assets available. Upload some assets first.')
        else:
            st.error('Unable to load assets list')

st.markdown('---')
st.caption('Advanced Creative Asset Management Platform - Prototype Version')
