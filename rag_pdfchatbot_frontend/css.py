import streamlit as st

def apply_theme_css():
    """
    Injects premium-level CSS styles into the Streamlit UI with a neon-themed aesthetic.
    Features vibrant neon elements, smooth animations, strategic emoji/icons, 
    and a premium product experience designed specifically for the AAI team.
    Includes a fully functional theme toggle and enhanced developer section.
    """
    # Set default theme if not exists
    if "theme" not in st.session_state:
        st.session_state.theme = "neon-dark"
    
    theme = st.session_state.theme
    
    # --- Premium Neon Color Scheme for AAI Team ---
    if theme == "neon-dark":
        # --- Core Neon Colors ---
        primary_color = "#00F3FF"        # Electric Cyan (Main Accent)
        secondary_color = "#FF00FF"      # Magenta (Secondary Accent)
        tertiary_color = "#00FF87"       # Electric Green (Tertiary Accent)
        background_color = "#0A0E17"     # Deep Space Blue
        secondary_background_color = "#1A1F30" # Slightly lighter space blue
        card_background = "rgba(10, 14, 23, 0.85)" # Semi-transparent space blue
        text_color = "#E6F0FF"           # Light Blue-White text
        subtle_text_color = "#A3B8D9"    # Muted Blue text
        border_color = "#2D3E5A"         # Dark blue border
        hover_color = "#00C8FF"          # Slightly darker cyan for hover
        selection_color = "#0066FF"      # Blue for text selections
        success_color = "#00FF87"        # Neon Green
        info_color = "#00F3FF"           # Bright Cyan
        info_glow = "0 0 15px rgba(0, 243, 255, 0.4)"
        warning_color = "#FFAA00"        # Amber
        error_color = "#FF0055"          # Neon Red
        
        # --- Neon Gradients ---
        body_gradient = "linear-gradient(135deg, #0A0E17 0%, #1A1F30 100%)"
        button_gradient = "linear-gradient(45deg, #FF00FF 0%, #00F3FF 100%)"
        button_hover_gradient = "linear-gradient(45deg, #00F3FF 0%, #FF00FF 100%)"
        sidebar_gradient = "linear-gradient(180deg, #1A1F30 0%, #0A0E17 100%)"
        tab_list_gradient = "linear-gradient(to right, #1A1F30, #0A0E17)"
        tab_active_gradient = "linear-gradient(to right, #FF00FF, #00F3FF)"
        card_glow = "0 0 15px rgba(0, 243, 255, 0.3), 0 0 30px rgba(255, 0, 255, 0.2)"
        user_message_bg = "rgba(10, 47, 74, 0.15)"
        assistant_message_bg = "rgba(26, 10, 42, 0.15)"
        user_message_border = "rgba(0, 243, 255, 0.3)"
        assistant_message_border = "rgba(255, 0, 255, 0.3)"
        
        # --- RGB Values for opacity ---
        primary_color_rgb = "0, 243, 255"
        secondary_color_rgb = "255, 0, 255"
        tertiary_color_rgb = "0, 255, 135"
        text_color_rgb = "230, 240, 255"
        info_color_rgb = "0, 243, 255"
        success_color_rgb = "0, 255, 135"
        warning_color_rgb = "255, 170, 0"
        error_color_rgb = "255, 0, 85"
    else:
        # --- Light Theme (Fallback) ---
        primary_color = "#0088FF"        # Electric Blue
        secondary_color = "#FF00AA"      # Pink
        tertiary_color = "#00CC66"       # Green
        background_color = "#F0F5FF"     # Light Blue
        secondary_background_color = "#E0EBFF" # Slightly darker blue
        card_background = "rgba(255, 255, 255, 0.9)"
        text_color = "#1A1F30"           # Dark Blue
        subtle_text_color = "#7B8794"    # Muted Blue text
        border_color = "#C2D1E5"         # Light blue border
        hover_color = "#0066CC"          # Slightly darker blue for hover
        selection_color = "#B3D7FF"      # Light blue for text selections
        success_color = "#00CC66"        # Green
        info_color = "#0088FF"           # Blue
        warning_color = "#FF8800"        # Orange
        error_color = "#FF0055"          # Red
        
        body_gradient = "linear-gradient(135deg, #F0F5FF 0%, #E0EBFF 100%)"
        button_gradient = "linear-gradient(45deg, #0088FF 0%, #00C6FF 100%)"
        button_hover_gradient = "linear-gradient(45deg, #00C6FF 0%, #0088FF 100%)"
        sidebar_gradient = "linear-gradient(180deg, #E0EBFF 0%, #F0F5FF 100%)"
        tab_list_gradient = "linear-gradient(to right, #f0f5ff, #e0ebff)"
        tab_active_gradient = "linear-gradient(to right, #0088FF, #FF00AA)"
        card_glow = "0 4px 12px rgba(0, 0, 0, 0.08)"
        user_message_bg = "rgba(230, 242, 255, 0.1)"
        assistant_message_bg = "rgba(240, 230, 255, 0.1)"
        user_message_border = "rgba(0, 136, 255, 0.3)"
        assistant_message_border = "rgba(255, 0, 170, 0.3)"
        
        primary_color_rgb = "0, 136, 255"
        secondary_color_rgb = "255, 0, 170"
        tertiary_color_rgb = "0, 204, 102"
        text_color_rgb = "26, 31, 48"
        info_color_rgb = "0, 136, 255"
        success_color_rgb = "0, 204, 102"
        warning_color_rgb = "255, 136, 0"
        error_color_rgb = "255, 0, 85"

    # Google Fonts for premium futuristic typography
    font_url = (
        "https://fonts.googleapis.com/css2?"
        "family=Orbitron:wght@400;500;600;700&"
        "family=Exo+2:wght@300;400;500;600;700&"
        "family=Roboto+Mono:wght@300;400;500&display=swap"
    )
    
    css = f"""
    <link href="{font_url}" rel="stylesheet">
    <style>
        :root {{
            /* --- Neon Color Variables --- */
            --primary-color: {primary_color};
            --secondary-color: {secondary_color};
            --tertiary-color: {tertiary_color};
            --background-color: {background_color};
            --secondary-background-color: {secondary_background_color};
            --card-background: {card_background};
            --text-color: {text_color};
            --subtle-text-color: {subtle_text_color};
            --border-color: {border_color};
            --hover-color: {hover_color};
            --selection-color: {selection_color};
            --success-color: {success_color};
            --info-color: {info_color};
            --warning-color: {warning_color};
            --error-color: {error_color};
            
            /* --- Neon Gradient Variables --- */
            --body-gradient: {body_gradient};
            --button-gradient: {button_gradient};
            --button-hover-gradient: {button_hover_gradient};
            --sidebar-gradient: {sidebar_gradient};
            --tab-list-gradient: {tab_list_gradient};
            --tab-active-gradient: {tab_active_gradient};
            --card-glow: {card_glow};
            --user-message-bg: {user_message_bg};
            --assistant-message-bg: {assistant_message_bg};
            --user-message-border: {user_message_border};
            --assistant-message-border: {assistant_message_border};
            
            /* --- RGB equivalents for opacity --- */
            --primary-color-rgb: {primary_color_rgb};
            --secondary-color-rgb: {secondary_color_rgb};
            --tertiary-color-rgb: {tertiary_color_rgb};
            --text-color-rgb: {text_color_rgb};
            --info-color-rgb: {info_color_rgb};
            --success-color-rgb: {success_color_rgb};
            --warning-color-rgb: {warning_color_rgb};
            --error-color-rgb: {error_color_rgb};
            
            /* --- Font Families --- */
            --font-family-body: 'Exo 2', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-family-heading: 'Orbitron', sans-serif;
            --font-family-mono: 'Roboto Mono', monospace;
            
            /* --- Responsive Font Sizes --- */
            --font-size-base: 16px;
            --font-size-sm: 0.875rem; /* 14px */
            --font-size-md: 1rem;     /* 16px */
            --font-size-lg: 1.125rem; /* 18px */
            --font-size-xl: 1.25rem;  /* 20px */
            --font-size-h1: 2.6rem;   /* ~42px */
            --font-size-h2: 2.1rem;   /* ~34px */
            --font-size-h3: 1.7rem;   /* ~27px */
            --font-size-h4: 1.4rem;   /* ~22px */
            --font-size-h5: 1.2rem;   /* ~19px */
            --font-size-h6: 1rem;     /* 16px */
            
            /* --- Spacing & Layout --- */
            --spacing-xs: 0.25rem; /* 4px */
            --spacing-sm: 0.5rem;  /* 8px */
            --spacing-md: 1rem;    /* 16px */
            --spacing-lg: 1.5rem;  /* 24px */
            --spacing-xl: 2rem;    /* 32px */
            --spacing-xxl: 3rem;   /* 48px */
            --border-radius-container: 16px;
            --border-radius-element: 12px;
            --border-radius-pill: 30px;
            --border-radius-message: 20px;
            
            /* --- Shadows for Depth --- */
            --box-shadow-light: 0 4px 12px rgba(0, 0, 0, 0.15);
            --box-shadow-medium: 0 6px 20px rgba(0, 0, 0, 0.2);
            --box-shadow-hover: 0 8px 25px rgba({primary_color_rgb}, 0.3);
            --neon-glow: 0 0 10px rgba({primary_color_rgb}, 0.4);
        }}
        
        /* --- RAG Background Theme Elements --- */
        body {{
            font-family: var(--font-family-body);
            color: var(--text-color);
            background: var(--body-gradient);
            line-height: 1.65;
            transition: background 0.4s ease, color 0.4s ease;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            overflow-x: hidden;
            position: relative;
            min-height: 100vh;
        }}
        
        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -2;
            pointer-events: none;
            opacity: 0.08;
            background-image: 
                radial-gradient(circle at 10% 20%, rgba({primary_color_rgb}, 0.1) 0px, transparent 2%),
                radial-gradient(circle at 90% 80%, rgba({secondary_color_rgb}, 0.1) 0px, transparent 2%),
                radial-gradient(circle at 50% 50%, rgba({primary_color_rgb}, 0.05) 0px, transparent 3%),
                radial-gradient(circle at 30% 70%, rgba({secondary_color_rgb}, 0.05) 0px, transparent 2%);
        }}
        
        /* --- RAG Network Particles Background --- */
        .rag-network-bg {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            pointer-events: none;
        }}
        
        /* --- RAG-Specific Icons --- */
        .rag-icon {{
            display: inline-block;
            font-size: 1.2em;
            margin: 0 var(--spacing-xs);
            opacity: 0.6;
            transition: all 0.3s ease;
        }}
        
        .rag-icon:hover {{
            opacity: 1;
            transform: scale(1.1);
        }}
        
        .rag-icon-pdf {{
            color: var(--primary-color);
        }}
        
        .rag-icon-url {{
            color: var(--secondary-color);
        }}
        
        .rag-icon-ai {{
            color: var(--tertiary-color);
        }}
        
        /* --- Welcome Animation / Initial Page Load Effect --- */
        .stApp.initial-load {{
            opacity: 0;
            transform: translateY(10px);
            transition: opacity 1s ease-out, transform 1s ease-out;
        }}
        .stApp.fade-in-complete {{
            opacity: 1;
            transform: translateY(0);
        }}
        
        /* --- Global Body & HTML Styles --- */
        h1, h2, h3, h4, h5, h6 {{
            font-family: var(--font-family-heading);
            margin-bottom: var(--spacing-sm);
            margin-top: var(--spacing-lg);
            line-height: 1.25;
            letter-spacing: -0.01em;
            text-shadow: 0 0 10px rgba({primary_color_rgb}, 0.2);
        }}
        
        h1 {{ 
            font-size: var(--font-size-h1); 
            font-weight: 700; 
            color: var(--primary-color);
            background: linear-gradient(to right, var(--primary-color), var(--secondary-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        h2 {{ 
            font-size: var(--font-size-h2); 
            font-weight: 600; 
            color: var(--secondary-color);
        }}
        
        h3 {{ 
            font-size: var(--font-size-h3); 
            font-weight: 600; 
            color: var(--primary-color);
        }}
        
        h4 {{ 
            font-size: var(--font-size-h4); 
            font-weight: 500; 
            color: var(--text-color);
        }}
        
        h5 {{ 
            font-size: var(--font-size-h5); 
            font-weight: 500;
        }}
        
        h6 {{ 
            font-size: var(--font-size-h6); 
            font-weight: 500;
        }}
        
        .stApp {{
            background-color: transparent;
        }}
        
        /* --- Streamlit Header (top bar) --- */
        .stApp > header {{
            background-color: var(--background-color);
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
            padding: var(--spacing-md) var(--spacing-lg);
            border-bottom: 1px solid var(--border-color);
            transition: all 0.4s ease;
            backdrop-filter: blur(10px);
        }}
        
        /* --- SIDEBAR ENHANCEMENTS - COMPLETE OVERHAUL --- */
        .stSidebar {{
            background: var(--sidebar-gradient);
            padding: var(--spacing-lg) var(--spacing-md);
            border-right: 1px solid var(--border-color);
            box-shadow: var(--box-shadow-light);
            transition: all 0.4s ease;
            backdrop-filter: blur(10px);
            position: relative;
        }}
        
        /* --- RAG Sidebar Icons --- */
        .stSidebar .rag-icon-sidebar {{
            position: absolute;
            opacity: 0.15;
            font-size: 3rem;
            z-index: 0;
        }}
        
        .stSidebar .rag-icon-sidebar.pdf {{
            top: 20%;
            right: 10%;
            color: var(--primary-color);
            transform: rotate(15deg);
        }}
        
        .stSidebar .rag-icon-sidebar.url {{
            bottom: 20%;
            left: 10%;
            color: var(--secondary-color);
            transform: rotate(-10deg);
        }}
        
        /* --- AAI Branding Header in Sidebar --- */
        .sidebar-header {{
            text-align: center;
            padding: var(--spacing-lg) 0;
            margin-bottom: var(--spacing-md);
            position: relative;
            z-index: 1;
        }}
        
        .sidebar-header::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 80%;
            height: 1px;
            background: linear-gradient(to right, transparent, var(--primary-color), transparent);
        }}
        
        .aai-logo {{
            font-family: 'Orbitron', sans-serif;
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 10px rgba({primary_color_rgb}, 0.2);
            margin-bottom: var(--spacing-xs);
            letter-spacing: 2px;
        }}
        
        .aai-tagline {{
            font-family: 'Exo 2', sans-serif;
            font-size: var(--font-size-sm);
            color: var(--subtle-text-color);
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        /* --- Enhanced Section Headers --- */
        .sidebar-section-header {{
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);
            margin: var(--spacing-xl) 0 var(--spacing-md);
            padding-bottom: var(--spacing-xs);
            position: relative;
            color: var(--primary-color);
            font-weight: 600;
            font-size: var(--font-size-lg);
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .sidebar-section-header::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 40px;
            height: 2px;
            background: var(--primary-color);
            border-radius: 1px;
        }}
        
        /* --- Enhanced Buttons with Icons --- */
        .stSidebar .stButton > button {{
            background: var(--button-gradient);
            color: white;
            border-radius: var(--border-radius-pill);
            border: none;
            padding: var(--spacing-sm) var(--spacing-md);
            font-weight: 500;
            transition: all 0.3s cubic-bezier(.25,.8,.25,1);
            box-shadow: var(--neon-glow);
            font-size: var(--font-size-sm);
            width: 100%;
            margin-bottom: var(--spacing-xs);
            text-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);
        }}
        
        .stSidebar button {{
            background: linear-gradient(45deg, #0088FF, #FF00AA) !important;
            color: white !important;
            border-radius: 25px !important;
            box-shadow: 0 0 10px rgba(0, 136, 255, 0.4), 0 0 10px rgba(255, 0, 170, 0.3) !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }}

        .stSidebar button:hover {{
            background: linear-gradient(45deg, #FF00AA, #0088FF) !important;
            box-shadow: 0 0 15px rgba(0, 136, 255, 0.6), 0 0 15px rgba(255, 0, 170, 0.5) !important;
            cursor: pointer;
        }}

        
        .stSidebar .stButton > button::before {{
            content: '✨';
            font-size: 1.2em;
        }}
        
        .stSidebar .stButton > button.upload-btn::before {{
            content: '📁';
        }}
        
        .stSidebar .stButton > button.refresh-btn::before {{
            content: '🔄';
        }}
        
        .stSidebar .stButton > button.summary-btn::before {{
            content: '📝';
        }}
        
        .stSidebar .stButton > button.manage-btn::before {{
            content: '🗑️';
        }}
        
        .stSidebar .stButton > button.clear-btn::before {{
            content: '🧹';
        }}
        
        .stSidebar .stButton > button.download-btn::before {{
            content: '📥';
        }}
        
        .stSidebar .stButton > button::after {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: 0.6s;
        }}
        
        .stSidebar .stButton > button:hover::after {{
            left: 100%;
        }}
        
        .stSidebar .stButton > button:hover {{
            background: var(--button-hover-gradient);
            transform: translateY(-2px);
            box-shadow: 0 0 15px rgba({primary_color_rgb}, 0.5), 0 0 25px rgba({secondary_color_rgb}, 0.3);
            cursor: pointer;
        }}
        
        .stSidebar .stButton > button:active {{
            transform: translateY(0);
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.25);
        }}
        
        /* --- Special Action Buttons (Clear Chat & Remove Vectors) --- */
        .stSidebar .stButton > button.clear-chat-btn {{
            background: linear-gradient(45deg, #00FF87, #00CC6B) !important;
            box-shadow: 0 0 10px rgba(0, 255, 135, 0.4) !important;
        }}
        
        .stSidebar .stButton > button.clear-chat-btn::before {{
            content: '🧹';
        }}
        
        .stSidebar .stButton > button.clear-chat-btn:hover {{
            background: linear-gradient(45deg, #00CC6B, #00FF87) !important;
            box-shadow: 0 0 15px rgba(0, 255, 135, 0.6) !important;
        }}
        
        .stSidebar .stButton > button.remove-vectors-btn {{
            background: linear-gradient(45deg, #FF0055, #CC0044) !important;
            box-shadow: 0 0 10px rgba(255, 0, 85, 0.4) !important;
        }}
        
        .stSidebar .stButton > button.remove-vectors-btn::before {{
            content: '🗑️';
        }}
        
        .stSidebar .stButton > button.remove-vectors-btn:hover {{
            background: linear-gradient(45deg, #CC0044, #FF0055) !important;
            box-shadow: 0 0 15px rgba(255, 0, 85, 0.6) !important;
        }}
        
        /* --- Enhanced File Uploader with Icons --- */
        .stSidebar .stFileUploader label {{
            color: var(--text-color);
            font-size: var(--font-size-sm);
            margin-bottom: var(--spacing-xs);
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);
        }}
        
        .stSidebar .stFileUploader label::before {{
            content: '📁';
        }}
        
        .stSidebar .stFileUploader div[data-testid="stFileUploaderDropzone"] {{
            border: 2px dashed var(--border-color);
            border-radius: var(--border-radius-element);
            padding: var(--spacing-md);
            transition: all 0.3s ease;
            cursor: pointer;
            background-color: var(--card-background);
            box-shadow: var(--card-glow);
        }}
        
        .stSidebar .stFileUploader div[data-testid="stFileUploaderDropzone"]:hover {{
            border-color: var(--primary-color);
            background-color: rgba(10, 14, 23, 0.9);
            box-shadow: 0 0 15px rgba({primary_color_rgb}, 0.3);
        }}
        
        .stSidebar .stFileUploader div[data-testid="stFileUploaderDropzone"]::before {{
            content: '📁 Upload PDFs';
            display: block;
            text-align: center;
            font-size: var(--font-size-md);
            margin-bottom: var(--spacing-sm);
            color: var(--primary-color);
        }}
        
        /* --- Enhanced Document Browser --- */
        .stSidebar .document-browser {{
            background-color: var(--card-background);
            border-radius: var(--border-radius-element);
            padding: var(--spacing-md);
            margin-top: var(--spacing-md);
            box-shadow: var(--card-glow);
            border: 1px solid var(--border-color);
            backdrop-filter: blur(8px);
            position: relative;
            z-index: 1;
        }}
        
        .stSidebar .document-browser::before {{
            content: '📄';
            position: absolute;
            top: 10px;
            right: 10px;
            font-size: 2rem;
            opacity: 0.1;
            color: var(--primary-color);
            z-index: 0;
        }}
        
        .stSidebar .document-browser .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--spacing-sm);
        }}
        
        .stSidebar .document-browser .header h4 {{
            margin: 0;
            font-size: var(--font-size-sm);
            color: var(--primary-color);
        }}
        
        .stSidebar .document-browser .document-item {{
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);
            padding: var(--spacing-xs) 0;
            border-bottom: 1px solid var(--border-color);
            transition: all 0.2s ease;
        }}
        
        .stSidebar .document-browser .document-item:last-child {{
            border-bottom: none;
        }}
        
        .stSidebar .document-browser .document-item:hover {{
            background-color: rgba({primary_color_rgb}, 0.05);
            transform: translateX(2px);
        }}
        
        .stSidebar .document-browser .document-item::before {{
            content: '📄';
            color: var(--primary-color);
        }}
        
        .stSidebar .document-browser .document-item .filename {{
            font-size: var(--font-size-sm);
            color: var(--text-color);
            flex: 1;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        .stSidebar .document-browser .document-item .page-count {{
            background: rgba({primary_color_rgb}, 0.1);
            color: var(--primary-color);
            padding: 0 var(--spacing-xs);
            border-radius: 10px;
            font-size: var(--font-size-xs);
            font-weight: 600;
        }}
        
        /* --- Enhanced Section Dividers --- */
        .stSidebar hr {{
            border: none;
            height: 1px;
            background: linear-gradient(to right, transparent, var(--border-color), transparent);
            margin: var(--spacing-lg) 0;
        }}
        
        /* --- Main Content Area Layout --- */
        .main .block-container {{
            padding-top: var(--spacing-xl);
            padding-bottom: var(--spacing-xl);
            padding-left: var(--spacing-xxl);
            padding-right: var(--spacing-xxl);
            max-width: 1200px;
            margin: auto;
            position: relative;
        }}
        
        /* --- RAG Main Content Icons --- */
        .main .block-container::before {{
            content: '🔗';
            position: absolute;
            top: 10%;
            right: 5%;
            font-size: 1.5rem;
            opacity: 0.1;
            color: var(--secondary-color);
            transform: rotate(-15deg);
            z-index: 0;
        }}
        
        .main .block-container::after {{
            content: '🧠';
            position: absolute;
            bottom: 10%;
            left: 5%;
            font-size: 1.5rem;
            opacity: 0.1;
            color: var(--tertiary-color);
            transform: rotate(10deg);
            z-index: 0;
        }}
        
        /* --- Main Title Glow Effect --- */
        .main-title {{
            font-family: var(--font-family-heading);
            text-align: center;
            margin-bottom: var(--spacing-sm);
            position: relative;
            padding-bottom: var(--spacing-md);
        }}
        
        .main-title::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 3px;
            background: linear-gradient(to right, var(--primary-color), var(--secondary-color));
            border-radius: 3px;
        }}
        
        /* --- CHAT AREA ENHANCEMENTS - COMPLETE OVERHAUL --- */
        .chat-container {{
            background-color: var(--card-background);
            border-radius: var(--border-radius-container);
            padding: var(--spacing-md);
            box-shadow: var(--card-glow);
            border: 1px solid var(--border-color);
            backdrop-filter: blur(8px);
            position: relative;
            overflow: hidden;
        }}
        
        .chat-container::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(to right, var(--primary-color), var(--secondary-color));
        }}
        
        /* --- RAG Chat Header Icons --- */
        .chat-header {{
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);
            padding-bottom: var(--spacing-md);
            margin-bottom: var(--spacing-md);
            border-bottom: 1px solid var(--border-color);
        }}
        
        .chat-header::after {{
            content: '💬';
            font-size: 1.5em;
            color: var(--primary-color);
        }}
        
        .chat-header .rag-icons {{
            display: flex;
            gap: var(--spacing-xs);
            margin-left: auto;
        }}
        
        .chat-header .rag-icons span {{
            opacity: 0.6;
            transition: all 0.3s ease;
        }}
        
        .chat-header .rag-icons span:hover {{
            opacity: 1;
            transform: scale(1.1);
        }}
        
        .chat-header h2 {{
            margin: 0;
            font-size: var(--font-size-h3);
            color: var(--primary-color);
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);
        }}
        
        .chat-header h2::before {{
            content: '💬';
        }}
        
        /* --- Enhanced Chat Messages with Bubbles --- */
        .stChatMessage {{
            background-color: var(--card-background);
            border-radius: var(--border-radius-message);
            padding: var(--spacing-md) var(--spacing-lg);
            margin-bottom: var(--spacing-md);
            box-shadow: var(--card-glow);
            transition: all 0.3s ease;
            border: 1px solid var(--border-color);
            backdrop-filter: blur(8px);
            position: relative;
            overflow: hidden;
            max-width: 90%;
            animation: fadeIn 0.3s ease-out;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .stChatMessage::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: linear-gradient(to bottom, var(--primary-color), var(--secondary-color));
            border-radius: var(--border-radius-message) 0 0 var(--border-radius-message);
        }}
        
        .stChatMessage:hover {{
            box-shadow: var(--box-shadow-medium), var(--card-glow);
            transform: translateY(-1px);
        }}
        
        .stChatMessage.st-chat-message-user {{
            color: var(--text-color);
            align-self: flex-end;
            background-color: var(--user-message-bg);
            border-color: var(--user-message-border);
            border-radius: var(--border-radius-message) var(--border-radius-message) 0 var(--border-radius-message);
        }}
        
        .stChatMessage.st-chat-message-user::before {{
            background: linear-gradient(to bottom, var(--primary-color), var(--hover-color));
        }}
        
        .stChatMessage.st-chat-message-assistant {{
            color: var(--text-color);
            align-self: flex-start;
            background-color: var(--assistant-message-bg);
            border-color: var(--assistant-message-border);
            border-radius: var(--border-radius-message) var(--border-radius-message) var(--border-radius-message) 0;
        }}
        
        .stChatMessage.st-chat-message-assistant::before {{
            background: linear-gradient(to bottom, var(--secondary-color), var(--primary-color));
        }}
        
        /* --- RAG Message Icons --- */
        .stChatMessage.st-chat-message-assistant::after {{
            content: '🧠';
            position: absolute;
            top: 10px;
            right: 10px;
            font-size: 1.2em;
            opacity: 0.2;
            color: var(--tertiary-color);
        }}
        
        .stChatMessage.st-chat-message-user::after {{
            content: '📄';
            position: absolute;
            top: 10px;
            right: 10px;
            font-size: 1.2em;
            opacity: 0.2;
            color: var(--primary-color);
        }}
        
        /* --- Enhanced Message Content --- */
        .stChatMessage p {{
            font-size: var(--font-size-md);
            margin-bottom: var(--spacing-xs);
            line-height: 1.6;
        }}
        
        .stChatMessage .st-cc {{ /* Chat Message caption (timestamp) */
            font-size: var(--font-size-sm);
            color: var(--subtle-text-color);
            text-align: right;
            margin-top: var(--spacing-xs);
            display: flex;
            align-items: center;
            gap: var(--spacing-xs);
        }}
        
        .stChatMessage .st-cc::before {{
            content: '⏱️';
            font-size: 0.8em;
        }}
        
        .stChatMessage.st-chat-message-user .st-cc {{
            justify-content: flex-end;
        }}
        
        .stChatMessage.st-chat-message-assistant .st-cc {{
            justify-content: flex-start;
        }}
        
        /* --- Enhanced Sources Section --- */
        .stChatMessage .sources-section {{
            background-color: rgba({primary_color_rgb}, 0.05);
            border-left: 3px solid var(--primary-color);
            padding: var(--spacing-sm) var(--spacing-md);
            margin-top: var(--spacing-md);
            border-radius: 0 var(--border-radius-element) var(--border-radius-element) 0;
        }}
        
        .stChatMessage .sources-section h4 {{
            display: flex;
            align-items: center;
            gap: var(--spacing-xs);
            margin: 0 0 var(--spacing-xs) 0;
            color: var(--primary-color);
            font-size: var(--font-size-sm);
        }}
        
        .stChatMessage .sources-section h4::before {{
            content: '🔍';
        }}
        
        .stChatMessage .sources-section ul {{
            margin: 0;
            padding-left: var(--spacing-md);
        }}
        
        .stChatMessage .sources-section li {{
            font-size: var(--font-size-sm);
            margin-bottom: var(--spacing-xs);
            list-style-type: '📄 ';
            color: var(--subtle-text-color);
        }}
        
        /* --- Enhanced Chat Input Area --- */
        .chat-input-container {{
            position: relative;
            margin-top: var(--spacing-lg);
        }}
        
        .chat-input-container::before {{
            content: '✍️';
            position: absolute;
            left: var(--spacing-md);
            top: 50%;
            transform: translateY(-50%);
            color: var(--subtle-text-color);
            font-size: 1.2em;
            z-index: 2;
        }}
        
        .chat-input-container .stTextInput > div > div > input {{
            padding-left: 2.5rem !important;
            background-color: var(--card-background);
            color: var(--text-color);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius-element);
            transition: all 0.3s ease;
            font-family: var(--font-family-body);
            font-size: var(--font-size-md);
            width: 100%;
            box-sizing: border-box;
            backdrop-filter: blur(8px);
            box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
        }}
        
        .chat-input-container .stTextInput > div > div > input:focus {{
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba({primary_color_rgb}, 0.2), 0 0 10px rgba({primary_color_rgb}, 0.3);
            outline: none;
            background-color: rgba(10, 14, 23, 0.95);
        }}
        
        .chat-input-container .stButton > button {{
            background: var(--primary-color);
            color: white;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: absolute;
            right: var(--spacing-md);
            bottom: var(--spacing-md);
            padding: 0;
            font-size: 1.2em;
            box-shadow: 0 0 10px rgba({primary_color_rgb}, 0.4);
            transition: all 0.3s ease;
            border: none;
        }}
        
        .chat-input-container .stButton > button::before {{
            content: '🚀';
        }}
        
        .chat-input-container .stButton > button:hover {{
            background: var(--hover-color);
            transform: scale(1.1);
            box-shadow: 0 0 15px rgba({primary_color_rgb}, 0.6);
        }}
        
        /* --- Typing Indicator Animation --- */
        .typing-indicator {{
            display: inline-block;
            position: relative;
            width: 80px;
            height: 20px;
        }}
        
        .typing-indicator span {{
            position: absolute;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background-color: var(--primary-color);
            opacity: 0.4;
            top: 50%;
            transform: translateY(-50%);
            animation: typing 1.4s infinite ease-in-out;
        }}
        
        .typing-indicator span:nth-child(1) {{
            left: 10px;
            animation-delay: 0s;
        }}
        
        .typing-indicator span:nth-child(2) {{
            left: 30px;
            animation-delay: 0.2s;
        }}
        
        .typing-indicator span:nth-child(3) {{
            left: 50px;
            animation-delay: 0.4s;
        }}
        
        @keyframes typing {{
            0%, 60%, 100% {{ transform: translateY(-50%) scaleY(0.4); opacity: 0.4; }}
            30% {{ transform: translateY(-50%) scaleY(1); opacity: 1; }}
        }}
        
        /* --- General Buttons (outside sidebar) --- */
        .stButton:not(.stSidebar .stButton) > button {{
            background: var(--button-gradient);
            color: white;
            border-radius: var(--border-radius-pill);
            border: none;
            padding: var(--spacing-sm) var(--spacing-md);
            font-weight: 500;
            transition: all 0.3s cubic-bezier(.25,.8,.25,1);
            box-shadow: var(--neon-glow);
            font-size: var(--font-size-md);
            text-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
            position: relative;
            overflow: hidden;
        }}
        
        .stButton:not(.stSidebar .stButton) > button::after {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: 0.6s;
        }}
        
        .stButton:not(.stSidebar .stButton) > button:hover::after {{
            left: 100%;
        }}
        
        .stButton:not(.stSidebar .stButton) > button:hover {{
            background: var(--button-hover-gradient);
            transform: translateY(-2px);
            box-shadow: 0 0 15px rgba({primary_color_rgb}, 0.5), 0 0 25px rgba({secondary_color_rgb}, 0.3);
            cursor: pointer;
        }}
        
        .stButton:not(.stSidebar .stButton) > button:active {{
            transform: translateY(0);
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.25);
        }}
        
        /* Slider (Global) - Ultra Light, No Background */
        .stSlider {{
            background: none; /* no background */
            border-radius: 25px;
            padding: 0.6em 1.2em;
            font-weight: 600;
            font-size: 1rem;
            color: #0088FF; /* main blue color */
            box-shadow: 0 0 8px rgba(0, 136, 255, 0.3), 0 0 12px rgba(255, 0, 170, 0.2);
            border: 2px solid rgba(0, 136, 255, 0.4);
            position: relative;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(.25,.8,.25,1);
            cursor: pointer;
        }}

        .stSlider:hover {{
            color: #00C6FF; /* lighter blue on hover */
            border-color: rgba(0, 198, 255, 0.6);
            box-shadow: 0 0 15px rgba(0, 198, 255, 0.4), 0 0 20px rgba(255, 0, 170, 0.25);
            transform: translateY(-2px);
        }}

        /* Track of the slider */
        .stSlider input[type="range"] {{
            -webkit-appearance: none;
            width: 100%;
            height: 6px;
            background: none;
            border-radius: 25px;
            border: 2px solid rgba(0, 136, 255, 0.4);
            box-shadow: 0 0 6px rgba(0, 136, 255, 0.3), 0 0 10px rgba(255, 0, 170, 0.2);
            outline: none;
            cursor: pointer;
            transition: border-color 0.3s ease;
        }}

        /* Thumb of the slider */
        .stSlider input[type="range"]::-webkit-slider-thumb {{
            -webkit-appearance: none;
            appearance: none;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: linear-gradient(135deg, #0088FF, #FF00AA);
            box-shadow: 0 0 8px rgba(0, 136, 255, 0.7), 0 0 12px rgba(255, 0, 170, 0.6);
            cursor: pointer;
            transition: background 0.3s ease, box-shadow 0.3s ease;
            border: none;
        }}

        .stSlider input[type="range"]:hover::-webkit-slider-thumb {{
            background: linear-gradient(135deg, #00C6FF, #FF00AA);
            box-shadow: 0 0 14px rgba(0, 198, 255, 0.9), 0 0 20px rgba(255, 0, 170, 0.8);
        }}

        /* Firefox thumb */
        .stSlider input[type="range"]::-moz-range-thumb {{
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: linear-gradient(135deg, #0088FF, #FF00AA);
            box-shadow: 0 0 8px rgba(0, 136, 255, 0.7), 0 0 12px rgba(255, 0, 170, 0.6);
            cursor: pointer;
            border: none;
            transition: background 0.3s ease, box-shadow 0.3s ease;
        }}

        .stSlider input[type="range"]:hover::-moz-range-thumb {{
            background: linear-gradient(135deg, #00C6FF, #FF00AA);
            box-shadow: 0 0 14px rgba(0, 198, 255, 0.9), 0 0 20px rgba(255, 0, 170, 0.8);
        }}

        
        /* --- Global Radio Buttons --- */
        /* Radio Buttons (Global) - Ultra Light, No Background */
        .stRadio > div {{
            background: none; /* no background */
            color: #0088FF; /* main blue text */
            border-radius: 25px;
            padding: 0.6em 1.2em;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(.25,.8,.25,1);
            box-shadow: 0 0 8px rgba(0, 136, 255, 0.15), 0 0 12px rgba(255, 0, 170, 0.1);
            font-size: 1rem;
            text-shadow: none;
            border: 2px solid rgba(0, 136, 255, 0.4);
            position: relative;
            overflow: hidden;
            margin-bottom: 0.6rem;
            cursor: pointer;
        }}

        .stRadio > div::after {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(0, 136, 255, 0.15), transparent);
            transition: 0.6s;
        }}

        .stRadio > div:hover::after {{
            left: 100%;
        }}

        .stRadio > div:hover {{
            color: #00C6FF; /* lighter blue on hover */
            border-color: rgba(0, 198, 255, 0.6);
            box-shadow: 0 0 15px rgba(0, 198, 255, 0.3), 0 0 20px rgba(255, 0, 170, 0.15);
            transform: translateY(-2px);
        }}

        .stRadio label[data-testid="stMarkdownContainer"] {{
            color: #333; /* dark text */
            font-weight: 700;
            text-shadow: none;
        }}

        .stRadio label {{
            color: rgba(51, 51, 51, 0.8);
            font-weight: 600;
        }}

        /* --- Theme Toggle Button --- */
        .theme-toggle-btn {{
            background: rgba(10, 14, 23, 0.7) !important;
            border: 1px solid var(--border-color) !important;
            color: var(--text-color) !important;
            box-shadow: var(--neon-glow) !important;
            padding: var(--spacing-xs) var(--spacing-md) !important;
            font-size: var(--font-size-sm) !important;
            width: auto !important;
            margin-bottom: 0 !important;
            border-radius: var(--border-radius-element) !important;
            backdrop-filter: blur(5px) !important;
            display: flex;
            align-items: center;
            gap: var(--spacing-xs);
        }}
        
        .theme-toggle-btn::before {{
            content: '🌓';
        }}
        
        .theme-toggle-btn:hover {{
            background-color: rgba({primary_color_rgb}, 0.1) !important;
            color: var(--primary-color) !important;
            transform: none !important;
            box-shadow: 0 0 15px rgba({primary_color_rgb}, 0.5) !important;
            border-color: var(--primary-color) !important;
        }}
        
        .theme-toggle-btn.active {{
            background-color: rgba({primary_color_rgb}, 0.2) !important;
            color: var(--primary-color) !important;
            box-shadow: 0 0 15px rgba({primary_color_rgb}, 0.5) !important;
            border-color: var(--primary-color) !important;
        }}
        
        /* --- FIX FOR INPUT FIELD BACKGROUND ISSUE --- */
        /* Ensure consistent background and text color during focus */
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {{
            background-color: var(--card-background) !important;
            color: var(--text-color) !important;
            border-color: var(--primary-color) !important;
            box-shadow: 0 0 15px rgba({primary_color_rgb}, 0.5) !important;
            outline: none !important;
        }}
        
        /* Fix for Chrome autofill issue (which often causes black background) */
        input:-webkit-autofill,
        input:-webkit-autofill:hover,
        input:-webkit-autofill:focus,
        input:-webkit-autofill:active {{
            -webkit-text-fill-color: var(--text-color) !important;
            -webkit-box-shadow: 0 0 0px 1000px var(--card-background) inset !important;
            transition: background-color 5000s ease-in-out 0s !important;
        }}
        
        /* Ensure text remains visible in all states */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {{
            color: var(--text-color) !important;
            background-color: var(--card-background) !important;
            transition: all 0.3s ease !important;
        }}
        
        /* Additional fix for chat input specifically */
        [data-testid="stChatInput"] input:focus {{
            background-color: var(--card-background) !important;
            color: var(--text-color) !important;
        }}
        
        /* --- Text Inputs --- */
        .stTextInput > div > div > input {{
            background-color: var(--card-background);
            color: var(--text-color);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius-element);
            padding: 12px 16px;
            transition: all 0.3s ease;
            font-family: var(--font-family-body);
            font-size: var(--font-size-md);
            width: 100%;
            max-width: 500px;
            height: 48px;
            box-sizing: border-box;
            backdrop-filter: blur(10px);
            box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba({primary_color_rgb}, 0.2), 0 0 10px rgba({primary_color_rgb}, 0.3);
            outline: none;
            background-color: rgba(10, 14, 23, 0.95);
        }}
        
        /* --- TextAreas --- */
        .stTextArea > div > div > textarea {{
            background-color: var(--card-background);
            color: var(--text-color);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius-element);
            padding: var(--spacing-sm);
            transition: all 0.3s ease;
            font-family: var(--font-family-body);
            font-size: var(--font-size-md);
            width: 100%;
            box-sizing: border-box;
            backdrop-filter: blur(10px);
            box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
        }}
        
        .stTextArea > div > div > textarea:focus {{
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba({primary_color_rgb}, 0.2), 0 0 10px rgba({primary_color_rgb}, 0.3);
            outline: none;
            background-color: rgba(10, 14, 23, 0.95);
        }}
        
        /* --- Styling for dropdown options --- */
        div[data-baseweb="popover"] .st-emotion-cache-1d6xpsj,
        div[data-baseweb="popover"] .st-emotion-cache-1j0xazr,
        div[data-baseweb="popover"] .st-emotion-cache-1j0xazr > div {{
            background-color: var(--card-background) !important;
            color: var(--text-color) !important;
            border-radius: var(--border-radius-element) !important;
            border: 1px solid var(--border-color) !important;
            box-shadow: var(--box-shadow-light) !important;
            backdrop-filter: blur(10px) !important;
        }}
        
        div[data-baseweb="popover"] .st-emotion-cache-1aehp66 {{ /* Option hover */
            background-color: rgba({primary_color_rgb}, 0.15) !important;
            color: var(--primary-color) !important;
            border-left: 3px solid var(--primary-color) !important;
        }}
        
        /* --- Tabs Styling (Neon Glow Effect) --- */
        .stTabs [data-baseweb="tab-list"] {{
            background: var(--tab-list-gradient);
            border-radius: var(--border-radius-container);
            padding: 0.5rem;
            display: flex;
            justify-content: space-around;
            margin-bottom: var(--spacing-lg);
            box-shadow: var(--box-shadow-light);
            border: 1px solid var(--border-color);
            position: relative;
            overflow: hidden;
        }}
        
        .stTabs [data-baseweb="tab-list"]::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba({primary_color_rgb}, 0.1), transparent);
            animation: shine 3s infinite;
        }}
        
        @keyframes shine {{
            0% {{ transform: translateX(-100%); }}
            100% {{ transform: translateX(100%); }}
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: var(--card-background);
            color: var(--text-color);
            padding: 0.75rem 1.75rem;
            margin: 0 0.4rem;
            border-radius: var(--border-radius-element);
            font-weight: 600;
            font-size: var(--font-size-md);
            border: 2px solid transparent;
            backdrop-filter: blur(8px);
            transition: all 0.3s ease-in-out;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            cursor: pointer;
            flex-grow: 1;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .stTabs [data-baseweb="tab"]::after {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: 0.6s;
        }}
        
        .stTabs [data-baseweb="tab"]:hover::after {{
            left: 100%;
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            transform: scale(1.03);
            border: 2px solid var(--primary-color);
            background-color: rgba({primary_color_rgb}, 0.1);
            color: var(--hover-color);
            box-shadow: 0 6px 12px rgba({primary_color_rgb}, 0.2);
        }}
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            background: var(--tab-active-gradient);
            color: white;
            font-weight: 700;
            border: 2px solid var(--primary-color);
            box-shadow: 0 6px 20px rgba({primary_color_rgb}, 0.4);
            transform: scale(1.05);
            text-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
        }}
        
        .stTabs [data-baseweb="tab-panel"] {{
            background-color: var(--card-background);
            padding: var(--spacing-lg);
            border-radius: var(--border-radius-container);
            box-shadow: var(--box-shadow-medium);
            border: 1px solid var(--border-color);
            border-top: none;
            transition: all 0.4s ease;
            backdrop-filter: blur(8px);
            position: relative;
            overflow: hidden;
        }}
        
        .stTabs [data-baseweb="tab-panel"]::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(to right, var(--primary-color), var(--secondary-color));
        }}
        
        /* --- Streamlit Alert Boxes --- */
        .stAlert {{
            border-radius: var(--border-radius-element);
            padding: var(--spacing-md);
            margin-bottom: var(--spacing-md);
            font-size: var(--font-size-md);
            line-height: 1.5;
            box-shadow: var(--box-shadow-light);
            border: 1px solid;
            background-color: var(--card-background);
            backdrop-filter: blur(8px);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .stAlert::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            border-radius: var(--border-radius-element) 0 0 var(--border-radius-element);
        }}
        
        .stAlert.st-emotion-cache-p5m8u {{ /* Info */
            color: var(--info-color);
            border-color: var(--info-color);
        }}
        
        .stAlert.st-emotion-cache-1629853 {{ /* Success */
            color: var(--success-color);
            border-color: var(--success-color);
        }}
        
        .stAlert.st-emotion-cache-1fzhg0f {{ /* Warning */
            color: var(--warning-color);
            border-color: var(--warning-color);
        }}
        
        .stAlert.st-emotion-cache-10grl5a {{ /* Error */
            color: var(--error-color);
            border-color: var(--error-color);
        }}
        
        /* --- Spinner Animation (Neon Pulse) --- */
        .stSpinner > div > div {{
            color: var(--primary-color);
            border-top-color: var(--primary-color);
            border-left-color: var(--primary-color);
            animation: pulse 1.5s ease-in-out infinite;
        }}
        
        @keyframes pulse {{
            0% {{ box-shadow: 0 0 0 0 rgba({primary_color_rgb}, 0.4); }}
            70% {{ box-shadow: 0 0 0 10px rgba({primary_color_rgb}, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba({primary_color_rgb}, 0); }}
        }}
        
        /* --- PDF Viewer Container --- */
        .pdf-viewer-container {{
            border-radius: var(--border-radius-element);
            overflow: hidden;
            box-shadow: var(--card-glow);
            border: 1px solid var(--border-color);
            background-color: #000;
            position: relative;
        }}
        
        .pdf-viewer-container::before {{
            content: 'AAI PDF VIEWER';
            position: absolute;
            top: 10px;
            left: 10px;
            color: var(--primary-color);
            font-family: var(--font-family-mono);
            font-size: var(--font-size-sm);
            letter-spacing: 1px;
            text-transform: uppercase;
            z-index: 10;
            opacity: 0.7;
        }}
        
        /* --- Analytics Metrics Glow --- */
        .stMetric {{
            background: var(--card-background);
            border-radius: var(--border-radius-element);
            padding: var(--spacing-md);
            box-shadow: var(--card-glow);
            transition: all 0.3s ease;
            border: 1px solid var(--border-color);
            backdrop-filter: blur(8px);
        }}
        
        .stMetric:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2), var(--card-glow);
        }}
        
        .stMetric .st-emotion-cache-1h7jxd9 {{
            color: var(--primary-color) !important;
            font-weight: 600;
            text-shadow: 0 0 5px rgba({primary_color_rgb}, 0.3);
        }}
        
        /* --- Dataframe Styling --- */
        .stDataFrame {{
            border-radius: var(--border-radius-element);
            overflow: hidden;
            box-shadow: var(--card-glow);
        }}
        
        table {{
            border-collapse: separate;
            border-spacing: 0;
            width: 100%;
        }}
        
        th {{
            background: linear-gradient(to bottom, var(--card-background), rgba({primary_color_rgb}, 0.1));
            color: var(--primary-color);
            font-weight: 600;
            border-bottom: 1px solid var(--border-color);
            padding: var(--spacing-sm) !important;
        }}
        
        td {{
            border-bottom: 1px solid var(--border-color);
            padding: var(--spacing-sm) !important;
        }}
        
        tr:last-child td {{
            border-bottom: none;
        }}
        
        tr:hover {{
            background-color: rgba({primary_color_rgb}, 0.05);
        }}
        
        /* --- Responsive Design Adjustments --- */
        @media (max-width: 768px) {{
            :root {{
                --font-size-base: 15px;
                --font-size-h1: 2.1rem;
                --font-size-h2: 1.7rem;
                --font-size-h3: 1.4rem;
                --spacing-lg: 1rem;
                --spacing-xl: 1.5rem;
                --spacing-xxl: 2rem;
            }}
            
            .main .block-container {{
                padding-left: var(--spacing-md);
                padding-right: var(--spacing-md);
            }}
            
            .stSidebar {{
                padding: var(--spacing-md);
            }}
            
            .stTabs [data-baseweb="tab"] {{
                padding: var(--spacing-xs) var(--spacing-sm);
                font-size: var(--font-size-sm);
                margin: 0 0.2rem;
            }}
            
            .stTextInput > div > div > input {{
                max-width: 100%;
            }}
            
            .main-title {{
                font-size: var(--font-size-h2);
            }}
        }}
        
        /* --- Custom Markdown for AAI Branding --- */
        .aai-brand {{
            display: inline-block;
            background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            font-family: var(--font-family-heading);
            font-size: 1.2em;
        }}
        
        .aai-glow {{
            text-shadow: 0 0 10px rgba({primary_color_rgb}, 0.5);
            color: var(--primary-color);
        }}
        
        /* --- Footer Styling --- */
        .sidebar-footer {{
            margin-top: var(--spacing-xl);
            padding-top: var(--spacing-lg);
            border-top: 1px solid var(--border-color);
        }}
        
        .sidebar-footer a {{
            color: var(--primary-color);
            transition: all 0.3s ease;
            text-decoration: none;
        }}
        
        .sidebar-footer a:hover {{
            color: var(--hover-color);
            text-shadow: 0 0 5px rgba({primary_color_rgb}, 0.5);
        }}
        
        /* --- Expandable Summary Styling --- */
        details {{
            background-color: var(--card-background);
            border-radius: var(--border-radius-element);
            padding: var(--spacing-md);
            margin-bottom: var(--spacing-md);
            box-shadow: var(--card-glow);
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
        }}
        
        details[open] {{
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2), var(--card-glow);
        }}
        
        summary {{
            cursor: pointer;
            font-weight: 600;
            color: var(--primary-color);
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);
        }}
        
        summary::marker {{
            color: var(--primary-color);
        }}
        
        summary:hover {{
            color: var(--hover-color);
        }}
        
        /* --- Backend Status Animation in Sidebar --- */
        .stSidebar span[style*="color:"] {{
            font-weight: bold;
            position: relative;
        }}
        
        .stSidebar span[style*="#f44336"], .stSidebar span[style*="red"] {{
            animation: pulse-error 1.5s infinite;
        }}
        
        .stSidebar span[style*="green"] {{
            animation: pulse-success 1.5s infinite;
        }}
        
        @keyframes pulse-error {{
            0% {{ text-shadow: 0 0 5px rgba(255, 0, 85, 0.5); }}
            50% {{ text-shadow: 0 0 15px rgba(255, 0, 85, 0.8); }}
            100% {{ text-shadow: 0 0 5px rgba(255, 0, 85, 0.5); }}
        }}
        
        @keyframes pulse-success {{
            0% {{ text-shadow: 0 0 5px rgba(0, 255, 135, 0.5); }}
            50% {{ text-shadow: 0 0 15px rgba(0, 255, 135, 0.8); }}
            100% {{ text-shadow: 0 0 5px rgba(0, 255, 135, 0.5); }}
        }}
        
        /* --- Download Button Styling --- */
        .stDownloadButton > button {{
            background: var(--button-gradient);
            color: white !important;
            font-weight: 600;
            padding: 0.75rem 1.75rem;
            border-radius: 10px;
            border: none;
            box-shadow: 0 4px 14px rgba({primary_color_rgb}, 0.25);
            cursor: pointer;
            transition: all 0.3s ease-in-out;
            user-select: none;
            backdrop-filter: blur(8px);
            outline: none;
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: var(--spacing-sm);
        }}
        
        .stDownloadButton > button::before {{
            content: '📥';
        }}
        
        .stDownloadButton > button::after {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: 0.6s;
        }}
        
        .stDownloadButton > button:hover::after {{
            left: 100%;
        }}
        
        .stDownloadButton > button:hover {{
            background: var(--button-hover-gradient);
            box-shadow: 0 6px 24px rgba({primary_color_rgb}, 0.4);
            transform: scale(1.05);
        }}
        
        .stDownloadButton > button:focus {{
            outline: none;
            box-shadow: 0 0 0 3px rgba({primary_color_rgb}, 0.6);
        }}
        
        /* --- Horizontal Rule Style --- */
        hr {{
            border-top: 1px solid var(--border-color);
            margin: var(--spacing-xl) 0;
            opacity: 0.7;
            transition: border-color 0.4s ease;
        }}
        
        /* --- Link Styling --- */
        a {{
            color: var(--primary-color);
            text-decoration: none;
            transition: all 0.3s ease;
        }}
        
        a:hover {{
            color: var(--hover-color);
            text-decoration: underline;
            text-shadow: 0 0 5px rgba({primary_color_rgb}, 0.5);
        }}
        
        /* --- Animation for Error Messages --- */
        .shake {{
            animation: shake 0.5s;
            transform: translate3d(0, 0, 0);
        }}
        
        @keyframes shake {{
            10%, 90% {{ transform: translate3d(-1px, 0, 0); }}
            20%, 80% {{ transform: translate3d(2px, 0, 0); }}
            30%, 50%, 70% {{ transform: translate3d(-4px, 0, 0); }}
            40%, 60% {{ transform: translate3d(4px, 0, 0); }}
        }}
        
        /* --- Assistant Typing Indicator --- */
        .assistant-typing {{
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);
            padding: var(--spacing-md) var(--spacing-lg);
            background-color: var(--assistant-message-bg);
            border: 1px solid var(--assistant-message-border);
            border-radius: var(--border-radius-message) var(--border-radius-message) var(--border-radius-message) 0;
            max-width: 90%;
            margin-bottom: var(--spacing-md);
            animation: fadeIn 0.3s ease-out;
        }}
        
        .assistant-typing .avatar {{
            background-color: var(--secondary-color);
            color: white;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            flex-shrink: 0;
        }}
        
        .assistant-typing .typing-text {{
            font-size: var(--font-size-md);
            color: var(--subtle-text-color);
            margin-right: var(--spacing-sm);
        }}
        
        /* --- Theme Toggle Button Specific Styles --- */
        .theme-toggle-container {{
            display: flex;
            gap: var(--spacing-sm);
            margin-top: var(--spacing-md);
        }}
        
        .theme-toggle-container .theme-toggle-btn {{
            flex: 1;
            text-align: center;
        }}
        
        .theme-toggle-container .theme-toggle-btn.active {{
            background: var(--button-gradient) !important;
            color: white !important;
        }}

        .footer-thin {{
            position: fixed;
            bottom: 0;
            left: 0;
            width: calc(100% - 21rem - 24px);
            margin-left: 21rem;
            margin-right: 24px;
            background-color: rgba(240, 240, 245, 0.95); /* soft gray background */
            color: #2a2e3d; /* strong dark text */
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 13px;
            padding: 8px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;

            border: 1px solid rgba(180, 180, 210, 0.3); /* very subtle border */
            box-shadow:
            0 0 4px rgba(0, 136, 255, 0.1),  /* very faint neon blue glow at 10% */
            0 3px 6px rgba(255, 0, 170, 0.1); /* very faint pink glow at 10% */
            z-index: 1000;
            border-radius: 10px;
            backdrop-filter: blur(8px);
            text-shadow:
            0 0 1px rgba(0, 136, 255, 0.1),
            0 0 2px rgba(255, 0, 170, 0.1); /* very subtle text glow */
        }}

        .footer-thin .left,
        .footer-thin .center,
        .footer-thin .right {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .footer-thin .center {{
            flex-grow: 0.1;
            justify-content: center;
            text-align: center;
            font-weight: 700;
            color: #FF33CC; /* solid pink */
            text-shadow:
            0 0 2px rgba(155, 38, 139, 0.1),
            0 0 4px rgba(155, 38, 139, 0.1);
        }}

        .footer-thin a {{
            color: #0066cc; /* solid blue links */
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            padding: 2px 8px;
            border-radius: 4px;
            position: relative;
            text-shadow:
            0 0 1px rgba(0, 102, 204, 0.1),
            0 0 3px rgba(0, 102, 204, 0.1);
        }}

        .footer-thin a:hover {{
            color: #fff;
            background: linear-gradient(45deg, #b85cae, #5a9fff);
            box-shadow:
            0 0 6px rgba(184, 92, 174, 0.3),
            0 0 10px rgba(90, 159, 255, 0.3);
            text-decoration: none;
        }}

        .footer-thin a::after {{
            content: "";
            display: block;
            height: 2px;
            background: #b85cae;
            width: 0;
            transition: width 0.3s ease;
            position: absolute;
            bottom: -2px;
            left: 0;
            border-radius: 2px;
        }}

        .footer-thin a:hover::after {{
            width: 100%;
        }}

        /* Responsive design */
        @media (max-width: 960px) {{
            .footer-thin {{
                margin-left: 0;
                margin-right: 0;
                width: 100%;
                flex-direction: column;
                padding: 10px 12px;
                gap: 6px;
                text-align: center;
            }}

            .footer-thin .left,
            .footer-thin .center,
            .footer-thin .right {{
                justify-content: center;
                flex-wrap: wrap;
            }}

            .footer-thin .center {{
                order: 1;
            }}
        }}

        /* Reduced motion */
        @media (prefers-reduced-motion: reduce) {{
            .footer-thin a,
            .footer-thin a::after {{
                transition: none;
                text-shadow: none;
                box-shadow: none;
            }}
        }}




   
        
        /* --- Developer Profile Section --- */
        .developer-profile {{
            background: var(--card-background);
            border-radius: var(--border-radius-element);
            padding: var(--spacing-md);
            margin-top: var(--spacing-xl);
            box-shadow: var(--card-glow);
            border: 1px solid var(--border-color);
            backdrop-filter: blur(8px);
            position: relative;
            overflow: hidden;
        }}
        
        .developer-profile::before {{
            content: '✨';
            position: absolute;
            top: 10px;
            right: 10px;
            font-size: 1.5rem;
            opacity: 0.2;
            color: var(--primary-color);
        }}
        
        .developer-header {{
            display: flex;
            align-items: center;
            gap: var(--spacing-md);
            margin-bottom: var(--spacing-md);
        }}
        
        .developer-avatar {{
            width: 60px;
            height: 60px;
            border-radius: 50%;
            overflow: hidden;
            border: 2px solid var(--primary-color);
            box-shadow: 0 0 10px rgba({primary_color_rgb}, 0.3);
        }}
        
        .developer-avatar img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .developer-name {{
            font-size: var(--font-size-lg);
            font-weight: 600;
            color: var(--primary-color);
        }}
        
        .developer-role {{
            font-size: var(--font-size-sm);
            color: var(--subtle-text-color);
            margin-top: var(--spacing-xs);
        }}
        
        .developer-links {{
            display: flex;
            gap: var(--spacing-sm);
            margin-top: var(--spacing-md);
        }}
        
        .developer-links a {{
            display: flex;
            align-items: center;
            gap: var(--spacing-xs);
            color: var(--subtle-text-color);
            text-decoration: none;
            font-size: var(--font-size-sm);
            transition: all 0.3s ease;
        }}
        
        .developer-links a:hover {{
            color: var(--primary-color);
        }}
        
        .developer-links a::before {{
            content: '🔗';
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    
    # JavaScript for theme toggle and developer section
    js_code = f"""
    <script>
        // --- Theme Toggle Functionality ---
        function setupThemeToggle() {{
            // Create theme toggle container if it doesn't exist
            const sidebar = window.parent.document.querySelector('.stSidebar');
            if (sidebar && !document.querySelector('.theme-toggle-container')) {{
                const themeContainer = document.createElement('div');
                themeContainer.className = 'theme-toggle-container';
                
                // Create theme buttons
                const darkBtn = document.createElement('button');
                darkBtn.className = 'theme-toggle-btn';
                darkBtn.innerHTML = 'Dark';
                darkBtn.dataset.theme = 'neon-dark';
                
                const lightBtn = document.createElement('button');
                lightBtn.className = 'theme-toggle-btn';
                lightBtn.innerHTML = 'Light';
                lightBtn.dataset.theme = 'light';
                
                // Set active theme
                const currentTheme = '{st.session_state.theme}';
                if (currentTheme === 'neon-dark') {{
                    darkBtn.classList.add('active');
                }} else {{
                    lightBtn.classList.add('active');
                }}
                
                // Add event listeners
                darkBtn.addEventListener('click', function() {{
                    // Update active state
                    darkBtn.classList.add('active');
                    lightBtn.classList.remove('active');
                    
                    // Update Streamlit session state
                    const xhr = new XMLHttpRequest();
                    xhr.open('POST', '/_stcore/set_session_state', true);
                    xhr.setRequestHeader('Content-Type', 'application/json');
                    xhr.send(JSON.stringify({{
                        "theme": "neon-dark"
                    }}));
                    
                    // Refresh page to apply theme
                    setTimeout(() => {{
                        window.location.reload();
                    }}, 100);
                }});
                
                lightBtn.addEventListener('click', function() {{
                    // Update active state
                    lightBtn.classList.add('active');
                    darkBtn.classList.remove('active');
                    
                    // Update Streamlit session state
                    const xhr = new XMLHttpRequest();
                    xhr.open('POST', '/_stcore/set_session_state', true);
                    xhr.setRequestHeader('Content-Type', 'application/json');
                    xhr.send(JSON.stringify({{
                        "theme": "light"
                    }}));
                    
                    // Refresh page to apply theme
                    setTimeout(() => {{
                        window.location.reload();
                    }}, 100);
                }});
                
                // Add buttons to container
                themeContainer.appendChild(darkBtn);
                themeContainer.appendChild(lightBtn);
                
                // Find the theme toggle section (Chat Settings section)
                const chatSettings = sidebar.querySelector('div[data-testid="stHeader"]:contains("Chat Settings")');
                if (chatSettings) {{
                    const nextElement = chatSettings.nextElementSibling;
                    if (nextElement) {{
                        sidebar.insertBefore(themeContainer, nextElement);
                    }} else {{
                        sidebar.appendChild(themeContainer);
                    }}
                }} else {{
                    // If Chat Settings not found, add at the end of sidebar
                    sidebar.appendChild(themeContainer);
                }}
            }}
        }}
        
        // --- RAG Network Particles Background ---
        function createRagNetwork() {{
            const container = document.createElement('div');
            container.className = 'rag-network-bg';
            document.body.appendChild(container);
            
            const canvas = document.createElement('canvas');
            container.appendChild(canvas);
            
            const ctx = canvas.getContext('2d');
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            
            // Configuration
            const config = {{
                particleCount: 60,
                maxDistance: 150,
                particleSize: 2,
                connectionLineWidth: 0.5,
                particleSpeed: 0.5,
                connectionColor: 'rgba(0, 243, 255, 0.3)',
                particleColor: 'rgba(255, 0, 255, 0.7)'
            }};
            
            // Particle class
            class Particle {{
                constructor() {{
                    this.x = Math.random() * canvas.width;
                    this.y = Math.random() * canvas.height;
                    this.vx = (Math.random() - 0.5) * config.particleSpeed;
                    this.vy = (Math.random() - 0.5) * config.particleSpeed;
                }}
                
                update() {{
                    this.x += this.vx;
                    this.y += this.vy;
                    
                    // Bounce off edges
                    if (this.x <= 0 || this.x >= canvas.width) this.vx *= -1;
                    if (this.y <= 0 || this.y >= canvas.height) this.vy *= -1;
                }}
                
                draw() {{
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, config.particleSize, 0, Math.PI * 2);
                    ctx.fillStyle = config.particleColor;
                    ctx.fill();
                }}
            }}
            
            // Create particles
            const particles = [];
            for (let i = 0; i < config.particleCount; i++) {{
                particles.push(new Particle());
            }}
            
            // Animation loop
            function animate() {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                // Update and draw particles
                particles.forEach(particle => {{
                    particle.update();
                    particle.draw();
                    
                    // Draw connections
                    particles.forEach(otherParticle => {{
                        const dx = particle.x - otherParticle.x;
                        const dy = particle.y - otherParticle.y;
                        const distance = Math.sqrt(dx * dx + dy * dy);
                        
                        if (distance < config.maxDistance) {{
                            const opacity = 1 - (distance / config.maxDistance);
                            ctx.beginPath();
                            ctx.moveTo(particle.x, particle.y);
                            ctx.lineTo(otherParticle.x, otherParticle.y);
                            ctx.lineWidth = config.connectionLineWidth;
                            ctx.strokeStyle = `rgba(0, 243, 255, ${{opacity * 0.3}})`;
                            ctx.stroke();
                        }}
                    }});
                }});
                
                requestAnimationFrame(animate);
            }}
            
            // Handle window resize
            window.addEventListener('resize', () => {{
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            }});
            
            animate();
        }}
        
        // --- Fade-in Animation ---
        document.addEventListener('DOMContentLoaded', function() {{
            const app = window.parent.document.querySelector('.stApp');
            if (app) {{
                if (!sessionStorage.getItem('streamlit_first_load')) {{
                    app.classList.add('initial-load');
                    sessionStorage.setItem('streamlit_first_load', 'true');
                    setTimeout(() => {{
                        app.classList.remove('initial-load');
                        app.classList.add('fade-in-complete');
                    }}, 100);
                }} else {{
                    app.classList.add('fade-in-complete');
                }}
                
                // Add glow effect to main title
                const mainTitle = window.parent.document.querySelector('.main-title');
                if (mainTitle) {{
                    mainTitle.style.position = 'relative';
                    mainTitle.style.zIndex = '1';
                    
                    // Create glow elements
                    const glow1 = document.createElement('div');
                    glow1.style.position = 'absolute';
                    glow1.style.top = '0';
                    glow1.style.left = '0';
                    glow1.style.width = '100%';
                    glow1.style.height = '100%';
                    glow1.style.background = 'linear-gradient(45deg, transparent, rgba(0, 243, 255, 0.1), transparent)';
                    glow1.style.zIndex = '-1';
                    glow1.style.borderRadius = '10px';
                    glow1.style.filter = 'blur(20px)';
                    glow1.style.pointerEvents = 'none';
                    mainTitle.appendChild(glow1);
                    
                    const glow2 = document.createElement('div');
                    glow2.style.position = 'absolute';
                    glow2.style.bottom = '0';
                    glow2.style.left = '0';
                    glow2.style.width = '100%';
                    glow2.style.height = '5px';
                    glow2.style.background = 'linear-gradient(to right, #00F3FF, #FF00FF)';
                    glow2.style.zIndex = '-1';
                    glow2.style.borderRadius = '0 0 10px 10px';
                    mainTitle.appendChild(glow2);
                }}
                
                // Add AAI branding to sidebar
                const sidebar = window.parent.document.querySelector('.stSidebar');
                if (sidebar && !document.querySelector('.sidebar-header')) {{
                    const sidebarHeader = document.createElement('div');
                    sidebarHeader.className = 'sidebar-header';
                    sidebarHeader.innerHTML = `
                        <div class="aai-logo">AAI</div>
                        <div class="aai-tagline">Advanced AI Interface</div>
                    `;
                    sidebar.insertBefore(sidebarHeader, sidebar.firstChild);
                    
                    // Add RAG icons to sidebar
                    const pdfIcon = document.createElement('div');
                    pdfIcon.className = 'rag-icon-sidebar pdf';
                    pdfIcon.innerHTML = '📄';
                    sidebar.appendChild(pdfIcon);
                    
                    const urlIcon = document.createElement('div');
                    urlIcon.className = 'rag-icon-sidebar url';
                    urlIcon.innerHTML = '🔗';
                    sidebar.appendChild(urlIcon);
                }}
                
                // Add developer profile section
                if (sidebar && !document.querySelector('.developer-profile')) {{
                    const developerSection = document.createElement('div');
                    developerSection.className = 'developer-profile';
                    developerSection.innerHTML = `
                        <div class="developer-header">
                            <div class="developer-avatar">
                                <img src="https://avatars.githubusercontent.com/u/101348283?v=4" alt="Developer Avatar">
                            </div>
                            <div>
                                <div class="developer-name">Suraj Varma</div>
                                <div class="developer-role">Lead Developer & AI Specialist</div>
                            </div>
                        </div>
                        <p>Building intelligent RAG systems that transform how we interact with information.</p>
                        <div class="developer-links">
                            <a href="https://github.com/suraj5424" target="_blank">GitHub</a>
                            <a href="https://linkedin.com/in/surajvarma" target="_blank">LinkedIn</a>
                        </div>
                    `;
                    // Add developer section before the footer
                    const footer = sidebar.querySelector('.sidebar-footer');
                    if (footer) {{
                        sidebar.insertBefore(developerSection, footer);
                    }} else {{
                        sidebar.appendChild(developerSection);
                    }}
                }}
                
                // Add RAG icons to chat header
                const chatHeader = window.parent.document.querySelector('.chat-header');
                if (chatHeader && !chatHeader.querySelector('.rag-icons')) {{
                    const ragIcons = document.createElement('div');
                    ragIcons.className = 'rag-icons';
                    ragIcons.innerHTML = `
                        <span class="rag-icon rag-icon-pdf">📄</span>
                        <span class="rag-icon rag-icon-url">🔗</span>
                        <span class="rag-icon rag-icon-ai">🧠</span>
                    `;
                    chatHeader.appendChild(ragIcons);
                }}
                
                // Initialize RAG Network
                createRagNetwork();
                
                // Setup theme toggle
                setupThemeToggle();
                
                // Add special classes to specific buttons
                const buttons = window.parent.document.querySelectorAll('.stSidebar .stButton > button');
                buttons.forEach(button => {{
                    const text = button.textContent || button.innerText;
                    if (text && text.includes('Clear Chat History')) {{
                        button.classList.add('clear-chat-btn');
                    }}
                    if (text && (text.includes('Remove PDF Vectors') || text.includes('Remove Vectors'))) {{
                        button.classList.add('remove-vectors-btn');
                    }}
                }});
            }}
        }});
        
        // --- Theme Toggle Button Class ---
        function addThemeToggleClass() {{
            const buttons = window.parent.document.querySelectorAll('.stSidebar .stButton > button');
            buttons.forEach(button => {{
                const text = button.textContent || button.innerText;
                if (text && (text.toLowerCase().includes('theme') || 
                             text.toLowerCase().includes('dark') || 
                             text.toLowerCase().includes('light'))) {{
                    button.classList.add('theme-toggle-btn');
                }}
            }});
        }}
        
        addThemeToggleClass();
        
        const observer = new MutationObserver(mutations => {{
            mutations.forEach(mutation => {{
                if (mutation.type === 'childList') {{
                    mutation.addedNodes.forEach(node => {{
                        if (node.nodeType === Node.ELEMENT_NODE) {{
                            const buttons = node.querySelectorAll ? 
                                node.querySelectorAll('.stSidebar .stButton > button') : [];
                            if (buttons.length > 0 || 
                               (node.matches && node.matches('.stSidebar .stButton > button'))) {{
                                addThemeToggleClass();
                            }}
                        }}
                    }});
                }}
            }});
        }});
        
        observer.observe(window.parent.document.body, {{ childList: true, subtree: true }});
        
        // --- Enhance document browser with icons ---
        function enhanceDocumentBrowser() {{
            const sidebar = window.parent.document.querySelector('.stSidebar');
            if (sidebar) {{
                // Create document browser container if it doesn't exist
                let docBrowser = sidebar.querySelector('.document-browser');
                if (!docBrowser) {{
                    docBrowser = document.createElement('div');
                    docBrowser.className = 'document-browser';
                    
                    // Find the existing document browser elements
                    const existingHeader = sidebar.querySelector('div[data-testid="stHeader"]');
                    const existingDataframe = sidebar.querySelector('.stDataFrame');
                    
                    if (existingDataframe) {{
                        // Create header
                        const header = document.createElement('div');
                        header.className = 'header';
                        header.innerHTML = '<h4>Document Browser</h4><button class="refresh-btn" style="background: none; border: none; cursor: pointer; color: var(--primary-color);">🔄</button>';
                        docBrowser.appendChild(header);
                        
                        // Move the dataframe into our container
                        docBrowser.appendChild(existingDataframe);
                        
                        // Insert before the manage documents section
                        const manageSection = sidebar.querySelector('div[data-testid="stHeader"]:contains("Manage Documents")');
                        if (manageSection) {{
                            sidebar.insertBefore(docBrowser, manageSection);
                        }} else {{
                            sidebar.appendChild(docBrowser);
                        }}
                        
                        // Add event listener to refresh button
                        const refreshBtn = header.querySelector('.refresh-btn');
                        if (refreshBtn) {{
                            refreshBtn.addEventListener('click', function() {{
                                const refreshButton = sidebar.querySelector('button:contains("Refresh Documents")');
                                if (refreshButton) refreshButton.click();
                            }});
                        }}
                    }}
                }}
                
                // Add icons to document items
                const dataframe = sidebar.querySelector('.stDataFrame table');
                if (dataframe) {{
                    const rows = dataframe.querySelectorAll('tbody tr');
                    rows.forEach(row => {{
                        const cells = row.querySelectorAll('td');
                        if (cells.length > 1) {{
                            // Add file icon to filename
                            const filename = cells[0].textContent;
                            cells[0].innerHTML = `<span style="margin-right: 5px;">📄</span>${{filename}}`;
                            
                            // Add page icon to page count
                            const pageCount = cells[1].textContent;
                            cells[1].innerHTML = `<span style="margin-right: 5px;">📑</span>${{pageCount}}`;
                        }}
                    }});
                }}
            }}
        }}
        
        // Run document browser enhancement after a delay to allow elements to load
        setTimeout(enhanceDocumentBrowser, 500);
        setTimeout(enhanceDocumentBrowser, 1000);









        
        // --- Ensure Developer Section is Added ---
        function ensureDeveloperSection() {{
            const sidebar = window.parent.document.querySelector('.stSidebar');
            if (sidebar && !document.querySelector('.developer-profile')) {{
                // Create developer section
                const developerSection = document.createElement('div');
                developerSection.className = 'developer-profile';
                developerSection.innerHTML = `
                    <div class="developer-header">
                        <div class="developer-avatar">
                            <img src="https://avatars.githubusercontent.com/u/101348283?v=4" alt="Developer Avatar">
                        </div>
                        <div>
                            <div class="developer-name">Suraj Varma</div>
                            <div class="developer-role">Lead Developer & AI Specialist</div>
                        </div>
                    </div>
                    <p>Building intelligent RAG systems that transform how we interact with information.</p>
                    <div class="developer-links">
                        <a href="https://github.com/suraj5424" target="_blank">GitHub</a>
                        <a href="https://linkedin.com/in/surajvarma" target="_blank">LinkedIn</a>
                    </div>
                `;
                
                // Add developer section before the footer
                const footer = sidebar.querySelector('.sidebar-footer');
                if (footer) {{
                    sidebar.insertBefore(developerSection, footer);
                }} else {{
                    sidebar.appendChild(developerSection);
                }}
            }}
        }}
        
        // Run developer section check multiple times to ensure it's added
        setTimeout(ensureDeveloperSection, 2000);
        setTimeout(ensureDeveloperSection, 4000);
        setTimeout(ensureDeveloperSection, 6000);
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)