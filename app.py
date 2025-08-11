import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import random

# Page settings
st.set_page_config(page_title="Envelope Surprise", layout="centered")

# Messages to show at the end
messages = [
    "Yrrr aap guse me toh ekdum tazi tazi laal tamatar Igti hogi!!.",
    "Yrr ap itne khobsuratho kahe 'Al generated' to nhi ho?",
    "Acha hai ki khubsurat hone ka koi bill nhi aata nhi toh aapke papa ji ke bohot paise Ig jaye.",
    "Main raat ko nini bohot der se krta hu... kya aap mujhe 2 thapaa laga ke apni godi me nini karaogi."
]

# Positions (x, y) for 4 random spots + center
positions = [
    (-0.5, 0.3),
    (0.4, -0.2),
    (-0.3, -0.4),
    (0.5, 0.5),
    (0, 0)  # center
]

# Session state to track taps
if "tap_count" not in st.session_state:
    st.session_state.tap_count = 0

st.title("📩 Tap the Envelope!")

# Create envelope figure
fig, ax = plt.subplots(figsize=(4, 4))
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.axis("off")

# Current position based on taps
pos = positions[min(st.session_state.tap_count, len(positions) - 1)]

# Draw envelope
envelope_x = [pos[0] - 0.2, pos[0] + 0.2, pos[0] + 0.2, pos[0] - 0.2, pos[0] - 0.2]
envelope_y = [pos[1] - 0.1, pos[1] - 0.1, pos[1] + 0.1, pos[1] + 0.1, pos[1] - 0.1]
ax.plot(envelope_x, envelope_y, color="black", linewidth=2)

# Envelope flap
ax.plot(
    [pos[0] - 0.2, pos[0], pos[0] + 0.2],
    [pos[1] + 0.1, pos[1], pos[1] + 0.1],
    color="black",
    linewidth=2
)

st.pyplot(fig)

# Tap button
if st.button("📌 Tap Envelope"):
    st.session_state.tap_count += 1
    if st.session_state.tap_count > len(positions) - 1:
        st.session_state.tap_count = len(positions) - 1

# Show message after final tap
if st.session_state.tap_count == len(positions) - 1:
    if st.button("💌 Open Envelope"):
        st.success(random.choice(messages))
