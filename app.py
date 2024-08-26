import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import google.generativeai as palm
import json
import logging
import sympy as sp

# Initialize Gemini
palm.configure(api_key="AIzaSyBFCRAdNSHw6894aq_56iBNfaDAhZgsIXI")

# Set up logging to capture errors silently
logging.basicConfig(filename='app_errors.log', level=logging.ERROR)

# Clear cache function
def clear_cache():
    st.cache_data.clear()  # Clear cached data
    st.success("Cache cleared successfully!")

# Function to safely evaluate equations
def evaluate_equation(equation, x_vals):
    try:
        expr = sp.sympify(equation)
        return [float(expr.subs(sp.Symbol('x'), x_val)) for x_val in x_vals]
    except Exception as e:
        logging.error(f"Error in equation evaluation: {e}")
        st.error("Error: Unable to evaluate the equation.")
        return []

# Function to plot the points or equation
def plot_graph(parsed_data, x_unit, y_unit):
    fig, ax = plt.subplots()
    ax.set_xlabel(f"X ({x_unit})")
    ax.set_ylabel(f"Y ({y_unit})")
    ax.set_title("Graph Based on Provided Data")

    if "points" in parsed_data:
        points = parsed_data["points"]
        x_vals = [point[0] for point in points]
        y_vals = [point[1] for point in points]
        ax.plot(x_vals, y_vals, 'bo-', label="Points")
        st.pyplot(fig)

    elif "equation" in parsed_data:
        equation = parsed_data["equation"]
        x = np.linspace(-10, 10, 400)
        y = evaluate_equation(equation, x)
        if y:
            ax.plot(x, y, label=f"{equation}")
            st.pyplot(fig)

# Function to generate explanation and parse data using Gemini
def process_input_with_gemini(user_input):
    # Handle specific known physics equations
    known_equations = {
        "first equation of motion": "u + a*x",
        "second equation of motion": "u*x + 0.5*a*x**2",
        "third equation of motion": "u**2 + 2*a*x"
    }

    for key, equation in known_equations.items():
        if key in user_input.lower():
            return {"equation": equation}

    # Otherwise, use Gemini for general parsing
    prompt = f"""
    Please parse the following input and return a JSON object.
    If it contains points, return as: {{"points": [[x1, y1], [x2, y2], ...]}}.
    If it contains an equation, return as: {{"equation": "equation_in_terms_of_x"}}.
    Input: {user_input}
    """
    response = palm.generate_text(prompt=prompt)
    try:
        parsed_data = json.loads(response.result)
        return parsed_data
    except json.JSONDecodeError:
        st.error("Error: Unable to parse Gemini's response. Please check the format.")
        return {}

# Streamlit UI
# Add a responsive header with a sticker
st.markdown("""
    <style>
    .header {
        font-size: 2em;
        font-weight: bold;
        text-align: center;
        background-color: #f7f7f7;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    </style>
    <div class="header">Graph Generator AI <img src="https://cdn-icons-png.flaticon.com/512/189/189001.png" width="40" /></div>
    """, unsafe_allow_html=True)

# Input for graph generation
user_input = st.text_input("Enter a mathematical question (e.g. 'Plot the points (1, 2) and (3, 4)' or 'y = 2x + 3'):")

# Additional inputs for units
x_unit = st.text_input("Enter the unit for the X axis (e.g., time, meters, etc.):", value="units")
y_unit = st.text_input("Enter the unit for the Y axis (e.g., distance, millions, etc.):", value="units")

# Buttons for search and clearing cache
if st.button("Search"):
    if user_input:
        # Parse and process user input using Gemini or predefined equations
        parsed_data = process_input_with_gemini(user_input)

        # Plot the graph based on parsed data with unit labels
        if parsed_data:
            plot_graph(parsed_data, x_unit, y_unit)

        # Generate and display explanation
        explanation = palm.generate_text(prompt=f"Explain how to plot the graph for: {user_input}")
        st.markdown("### Explanation")
        st.write(explanation.result)

# Clear cache button
if st.button("Clear Cache"):
    clear_cache()

# Footer sticker for a decorative touch
st.markdown("""
    <div style='text-align: center; margin-top: 50px;'>
        <img src='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSzcgQ6toDLgGTJzH1wY5AjqR0Zk38RBLU7TA&s' width='80' />
        <p>Powered by Ahsan TECH</p>
    </div>
    """, unsafe_allow_html=True)
