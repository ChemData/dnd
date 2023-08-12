import numpy as np
import cairo


def generate_weather(start, N, states, probs):
    output = start
    for i in range(N-1):
        output += np.random.choice(states, p=probs[output[-1]])
    return output


def line(from_xy, to_xy, context):
    context.move_to(*from_xy)
    context.line_to(*to_xy)


states = ["N", "H", "C"]
transition_probs = {
    "N": [0.7, 0.15, 0.15],
    "H": [0.5, 0.4, 0.1],
    "C": [0.5, 0.1, 0.4]
}

rolls = {
    "Normal": ['1-14', '15-17', '18-20'],
    "Hot": ['1-10', '11-18', '19-20'],
    "Cold": ['1-10', '11-12', '13-20']
}


for i in range(10):
    print(generate_weather("N", 30, states, transition_probs))


