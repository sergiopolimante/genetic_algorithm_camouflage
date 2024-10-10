import streamlit as st
import matplotlib
import matplotlib.backends.backend_agg as agg
import pylab
import random
import itertools
from genetic_algorithm import *
import time

# Draw functions
def draw_plot(x, y, x_label='Generation', y_label='Fitness'):
    fig = pylab.figure(figsize=[4, 4], dpi=300)
    ax = fig.gca()
    ax.plot(x   , y)
    # st.pyplot(fig)
    placeholder_plot.pyplot(fig)

def draw_squares(population):
    matrix = []
    i = 0
    for row in range(n):
        matrix_row = []
        for col in range(n):
            color = population[i]
            matrix_row.append(color)
            i += 1
        matrix.append(matrix_row)
    return matrix

# def display_squares(matrix, placeholder):
#     'without background'
#     grid = []
#     for row in matrix:
#         grid_row = []
#         for color in row:
#             grid_row.append(f'<div style="width: {square_size}px; height: {square_size}px; background-color: rgb({color[0]}, {color[1]}, {color[2]}); border: 1px solid black;"></div>')
#         grid.append(''.join(grid_row))
#     #st.markdown('<div style="display: flex; flex-direction: column;">' + ''.join([f'<div style="display: flex;">{r}</div>' for r in grid]) + '</div>', unsafe_allow_html=True)
#     placeholder.markdown('<div style="display: flex; flex-direction: column;">' + ''.join([f'<div style="display: flex;">{r}</div>' for r in grid]) + '</div>', unsafe_allow_html=True)


def display_squares(matrix, placeholder):
    # Calculate the total size for the background square
    # The background square should account for the padding
    background_size = square_size * n + distance_between_squares * (n - 1) + 2 * distance_between_squares  # Adding padding space

    # Create a background square with flex properties
    background_square = (
        f'<div style="width: {background_size}px; height: {background_size}px; background-color: rgb({target_color[0]}, {target_color[1]}, {target_color[2]}); display: flex; align-items: center; justify-content: center; margin: 10px;">'
    )

    # Create a container for the grid that will be centered with padding
    grid_container = (
        f'<div style="display: grid; grid-template-columns: repeat({n}, 1fr); gap: {distance_between_squares}px; padding: {distance_between_squares}px; box-sizing: border-box;">'
    )

    # Create a grid for the colored squares
    for row in matrix:
        for color in row:
            grid_container += (
                f'<div style="width: {square_size}px; height: {square_size}px; background-color: rgb({color[0]}, {color[1]}, {color[2]}); border: 1px solid black;"></div>'
            )
    
    grid_container += '</div>'  # Close the grid container

    # Combine background and grid
    placeholder.markdown(background_square + grid_container + '</div>', unsafe_allow_html=True)

# Streamlit app
st.title("Camouflage Simulation")


placeholder_box = st.empty()
placeholder_plot = st.empty()
placeholder_text = st.empty()


# Set the backend for matplotlib
matplotlib.use("Agg")

# Global variables
FPS = 10
target_color = [150, 150, 200]
n = 10
square_size = 50
distance_between_squares = 10
population_size = 100


# Initialize session state
if 'generation_counter' not in st.session_state:
    st.session_state.generation_counter = itertools.count(start=1)
    st.session_state.population = generate_random_population(population_size)
    st.session_state.best_fitness_values = []
    st.session_state.best_colors = []
    st.session_state.start_sim = False

# Sidebar for interaction
target_red = st.sidebar.slider("Target Red", 0, 255, 125, 1)
target_green = st.sidebar.slider("Target Green", 0, 255, 125, 1)
target_blue = st.sidebar.slider("Target Blue", 0, 255, 125, 1)
st.sidebar.divider()
mutation_probability = st.sidebar.slider("Mutation Probability", 0, 100, 10, 1)
apply_elitism = st.sidebar.checkbox("Apply Elitism")
#time = st.sidebar.slider("time", 1, 2, 1, 0.1)

if st.sidebar.button("Run Simulation") or st.session_state.start_sim == True:
    st.session_state.start_sim = True

    while st.session_state.start_sim:
        # Update target color
        target_color[0] = target_red
        target_color[1] = target_green
        target_color[2] = target_blue
        i = next(st.session_state.generation_counter)

        # Sort population by fitness
        st.session_state.population = sorted(st.session_state.population,
                                              key=lambda individual: calculate_fitness(individual, target_color))

        best_fitness = calculate_fitness(st.session_state.population[0], target_color)
        best_color = st.session_state.population[0]
        st.session_state.best_fitness_values.append(best_fitness)
        st.session_state.best_colors.append(best_color)

        # Create new population
        if apply_elitism:
            new_population = [st.session_state.population[0]]  # Keep the best individual
        else:
            new_population = []
        while len(new_population) < population_size:
            parent1, parent2 = random.choices(st.session_state.population[:10], k=2)
            child1, child2 = crossover(parent1, parent2)
            child1 = mutate(child1, mutation_probability=mutation_probability)
            child2 = mutate(child2, mutation_probability=mutation_probability)
            new_population.extend([child1, child2])

        st.session_state.population = new_population

        # Draw methods
        draw_plot(list(range(len(st.session_state.best_fitness_values))), st.session_state.best_fitness_values)
        matrix = draw_squares(st.session_state.population)
        display_squares(matrix, placeholder_box)

        # Display text
        placeholder_text.write(f"Best Solution: {best_color}\nTarget: {tuple(target_color)}")

        # Check for stopping condition
        if list(best_color) == target_color:
            st.write('Best individual color matches the target color!')
            start_sim = False
            break

        time.sleep(0.5)  # Simulate delay
